from enums import Cell, Direction, Lane, MachineKind
from models import IOLabel, LineSpec, Solution
from ortools.sat.python import cp_model


def solve_first_feasible(spec: LineSpec) -> Solution | None:
    machine_size = _machine_size(spec.machine_kind)
    model = cp_model.CpModel()

    min_width = spec.machine_count * machine_size
    max_width = min_width + 3
    width = model.NewIntVar(min_width, max_width, "width")
    machine_top = model.NewIntVar(0, max(0, spec.height - 1), "machine_top")

    # Variable declarations only (no structural constraints yet).
    cell_vars: list[list[cp_model.IntVar]] = []
    belt_direction_vars: list[list[cp_model.IntVar]] = []
    belt_lane_vars: list[list[cp_model.IntVar]] = []
    inserter_direction_vars: list[list[cp_model.IntVar]] = []
    for y in range(spec.height):
        cell_row: list[cp_model.IntVar] = []
        belt_dir_row: list[cp_model.IntVar] = []
        belt_lane_row: list[cp_model.IntVar] = []
        ins_dir_row: list[cp_model.IntVar] = []
        for x in range(max_width):
            cell_row.append(model.NewIntVar(int(Cell.EMPTY), int(Cell.PIPE), f"cell_{y}_{x}"))
            belt_dir_row.append(
                model.NewIntVar(
                    int(Direction.NONE),
                    int(Direction.RIGHT_TO_LEFT),
                    f"belt_dir_{y}_{x}",
                )
            )
            belt_lane_row.append(model.NewIntVar(int(Lane.NONE), int(Lane.RIGHT), f"belt_lane_{y}_{x}"))
            ins_dir_row.append(
                model.NewIntVar(
                    int(Direction.NONE),
                    int(Direction.RIGHT_TO_LEFT),
                    f"ins_dir_{y}_{x}",
                )
            )
        cell_vars.append(cell_row)
        belt_direction_vars.append(belt_dir_row)
        belt_lane_vars.append(belt_lane_row)
        inserter_direction_vars.append(ins_dir_row)

    bus_input_items = list(spec.bus_input_items)
    bus_output_items = list(spec.bus_output_items)
    bus_io_items = bus_input_items + bus_output_items
    bus_io_port_row_vars = [
        model.NewIntVar(0, max(0, spec.height - 1), f"bus_io_port_row_{i}")
        for i, _ in enumerate(bus_io_items)
    ]
    bus_io_port_lane_vars = [
        model.NewIntVar(int(Lane.NONE), int(Lane.RIGHT), f"bus_io_port_lane_{i}")
        for i, _ in enumerate(bus_io_items)
    ]
    bus_io_port_direction_vars = [
        model.NewIntVar(
            int(Direction.NONE),
            int(Direction.RIGHT_TO_LEFT),
            f"bus_io_port_direction_{i}",
        )
        for i, _ in enumerate(bus_io_items)
    ]

    # Variable-activation constraints (DESIGN Variables + General placement):
    # - Tiles outside width are invalid (forced EMPTY).
    # - Direction/lane vars are meaningful only for compatible cell kinds.
    default_direction = int(Direction.NONE)
    default_lane = int(Lane.NONE)
    belt_family = (Cell.BELT, Cell.UNDER_IN, Cell.UNDER_OUT)
    for y in range(spec.height):
        for x in range(max_width):
            cell = cell_vars[y][x]
            belt_dir = belt_direction_vars[y][x]
            belt_lane = belt_lane_vars[y][x]
            ins_dir = inserter_direction_vars[y][x]

            out_of_width = model.NewBoolVar(f"out_of_width_{y}_{x}")
            model.Add(width <= x).OnlyEnforceIf(out_of_width)
            model.Add(width > x).OnlyEnforceIf(out_of_width.Not())
            model.Add(cell == int(Cell.EMPTY)).OnlyEnforceIf(out_of_width)

            is_belt_family = model.NewBoolVar(f"is_belt_family_{y}_{x}")
            model.AddAllowedAssignments([cell], [[int(c)] for c in belt_family]).OnlyEnforceIf(is_belt_family)
            model.AddForbiddenAssignments([cell], [[int(c)] for c in belt_family]).OnlyEnforceIf(is_belt_family.Not())
            model.Add(belt_dir == default_direction).OnlyEnforceIf(is_belt_family.Not())
            model.Add(belt_lane == default_lane).OnlyEnforceIf(is_belt_family.Not())

            is_inserter = model.NewBoolVar(f"is_inserter_{y}_{x}")
            model.Add(cell == int(Cell.INSERTER)).OnlyEnforceIf(is_inserter)
            model.Add(cell != int(Cell.INSERTER)).OnlyEnforceIf(is_inserter.Not())
            model.Add(ins_dir == default_direction).OnlyEnforceIf(is_inserter.Not())

    model.Minimize(width)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    solved_width = solver.Value(width)
    solved_machine_top = solver.Value(machine_top)

    grid: list[list[Cell]] = []
    belt_directions: list[list[Direction | None]] = []
    belt_lanes: list[list[Lane | None]] = []
    inserter_directions: list[list[Direction | None]] = []
    for y in range(spec.height):
        grid_row: list[Cell] = []
        belt_dir_row: list[Direction | None] = []
        belt_lane_row: list[Lane | None] = []
        ins_dir_row: list[Direction | None] = []
        for x in range(solved_width):
            grid_row.append(_as_cell(solver.Value(cell_vars[y][x])))
            belt_dir_row.append(_as_direction(solver.Value(belt_direction_vars[y][x])))
            belt_lane_row.append(_as_lane(solver.Value(belt_lane_vars[y][x])))
            ins_dir_row.append(_as_direction(solver.Value(inserter_direction_vars[y][x])))
        grid.append(grid_row)
        belt_directions.append(belt_dir_row)
        belt_lanes.append(belt_lane_row)
        inserter_directions.append(ins_dir_row)

    io_labels = tuple(
        IOLabel(
            tile_y=solver.Value(bus_io_port_row_vars[i]),
            direction=_as_direction(solver.Value(bus_io_port_direction_vars[i])),
            lane=_as_lane(solver.Value(bus_io_port_lane_vars[i])),
            item=item,
        )
        for i, item in enumerate(bus_io_items)
    )

    return Solution(
        height=spec.height,
        width=solved_width,
        machine_top=solved_machine_top,
        grid=grid,
        belt_directions=belt_directions,
        belt_lanes=belt_lanes,
        inserter_directions=inserter_directions,
        machine_regions=[],
        io_labels=io_labels,
    )


def _machine_size(kind: MachineKind) -> int:
    if kind == MachineKind.ASSEMBLER_3X3:
        return 3
    return 4


def _as_cell(raw: int) -> Cell:
    try:
        return Cell(raw)
    except ValueError:
        return Cell.EMPTY


def _as_direction(raw: int) -> Direction:
    try:
        return Direction(raw)
    except ValueError:
        return Direction.NONE


def _as_lane(raw: int) -> Lane:
    try:
        return Lane(raw)
    except ValueError:
        return Lane.NONE
