from enums import Cell, Direction, Lane, MachineKind
from models import IOLabel, LineSpec, MachineIO, Solution
from ortools.sat.python import cp_model


def solve_first_feasible(spec: LineSpec) -> Solution | None:
    if spec.machine_kind == MachineKind.ASSEMBLER_3X3:
        machine_size = 3
    else:
        machine_size = 4

    fixed_height = spec.height
    machine_top = max(0, (fixed_height - machine_size) // 2)
    machine_left = 0
    total_machine_width = machine_size * spec.machine_count
    max_inputs = min(spec.input_count, machine_size)
    min_width = total_machine_width
    max_width = min_width + max(2, max_inputs)
    machine_ios = list(spec.machine_ios)
    if len(machine_ios) != spec.machine_count:
        return None

    model = cp_model.CpModel()
    width = model.NewIntVar(min_width, max_width, "width")
    io_row_vars: list[cp_model.IntVar] = []
    io_lane_vars: list[cp_model.IntVar] = []
    io_dir: list[Direction] = []
    io_item: list[str] = []

    if not _add_machine_io_flow_constraints(model, spec, machine_ios):
        return None
    _add_io_lane_constraints(
        model=model,
        tile_height=fixed_height,
        machine_top=machine_top,
        machine_size=machine_size,
        input_items=spec.hub_input_items,
        output_items=spec.output_items,
        io_row_vars=io_row_vars,
        io_lane_vars=io_lane_vars,
        io_dir=io_dir,
        io_item=io_item,
    )

    # Objective (phase 1): minimize total width.
    model.Minimize(width)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    solved_width = solver.Value(width)
    grid = [[Cell.EMPTY for _ in range(solved_width)] for _ in range(fixed_height)]
    belt_directions = [[None for _ in range(solved_width)] for _ in range(fixed_height)]
    belt_lanes = [[None for _ in range(solved_width)] for _ in range(fixed_height)]
    inserter_directions = [[None for _ in range(solved_width)] for _ in range(fixed_height)]
    machine_regions: list[tuple[int, int, int]] = []
    io_labels: list[IOLabel] = []

    for machine_idx in range(spec.machine_count):
        top = machine_top
        left = machine_left + (machine_idx * machine_size)
        machine_regions.append((top, left, machine_size))
        for y in range(top, top + machine_size):
            for x in range(left, left + machine_size):
                grid[y][x] = Cell.MACHINE

    _place_placeholder_io(
        grid=grid,
        belt_directions=belt_directions,
        belt_lanes=belt_lanes,
        inserter_directions=inserter_directions,
        machine_ios=machine_ios,
        machine_count=spec.machine_count,
        hub_input_items=spec.hub_input_items,
        box_input_items=spec.box_input_items,
        output_items=spec.output_items,
        machine_top=machine_top,
        machine_left=machine_left,
        machine_size=machine_size,
        total_machine_width=total_machine_width,
    )
    for idx, item in enumerate(io_item):
        y = solver.Value(io_row_vars[idx])
        lane_raw = solver.Value(io_lane_vars[idx])
        lane = Lane.LEFT if lane_raw == 0 else Lane.RIGHT
        io_labels.append(IOLabel(tile_y=y, direction=io_dir[idx], lane=lane, item=item))

    return Solution(
        height=fixed_height,
        width=solved_width,
        machine_top=machine_top,
        grid=grid,
        belt_directions=belt_directions,
        belt_lanes=belt_lanes,
        inserter_directions=inserter_directions,
        machine_regions=machine_regions,
        io_labels=tuple(io_labels),
    )


def _place_placeholder_io(
    grid: list[list[Cell]],
    belt_directions: list[list[Direction | None]],
    belt_lanes: list[list[Lane | None]],
    inserter_directions: list[list[Direction | None]],
    machine_ios: list[MachineIO],
    machine_count: int,
    hub_input_items: tuple[str, ...],
    box_input_items: tuple[str, ...],
    output_items: tuple[str, ...],
    machine_top: int,
    machine_left: int,
    machine_size: int,
    total_machine_width: int,
) -> None:
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    input_source_items = set(hub_input_items) | set(box_input_items)

    def in_bounds(x: int, y: int) -> bool:
        return 0 <= x < width and 0 <= y < height

    def place_belt(x: int, y: int, direction: Direction) -> None:
        if not in_bounds(x, y):
            return
        grid[y][x] = Cell.BELT
        belt_directions[y][x] = direction
        belt_lanes[y][x] = Lane.LEFT

    def place_inserter(x: int, y: int, direction: Direction) -> None:
        if not in_bounds(x, y):
            return
        grid[y][x] = Cell.INSERTER
        inserter_directions[y][x] = direction

    top_belt_y = machine_top - 2
    top_inserter_y = machine_top - 1
    bottom_inserter_y = machine_top + machine_size
    bottom_belt_y = bottom_inserter_y + 1

    # Map each produced item to producer machine index (first producer wins).
    producer_by_item: dict[str, int] = {}
    for idx, machine_io in enumerate(machine_ios):
        if machine_io.output_item not in producer_by_item:
            producer_by_item[machine_io.output_item] = idx

    # 1) Place input inserters/belts per machine input item.
    for machine_idx in range(machine_count):
        machine_io = machine_ios[machine_idx]
        m_left = machine_left + machine_idx * machine_size
        for port_idx, input_item in enumerate(machine_io.input_items):
            if port_idx >= machine_size:
                break
            x = m_left + port_idx
            place_inserter(x, top_inserter_y, Direction.TOP_TO_BOTTOM)

            if input_item in input_source_items:
                place_belt(x, top_belt_y, Direction.LEFT_TO_RIGHT)
                continue

            src_idx = producer_by_item.get(input_item)
            if src_idx is None or src_idx >= machine_idx:
                continue
            src_left = machine_left + src_idx * machine_size
            src_x = src_left + (machine_size - 1)

            # Producer outputs upward to top belt, then belt runs to destination port.
            place_inserter(src_x, top_inserter_y, Direction.BOTTOM_TO_TOP)
            step = 1 if src_x <= x else -1
            for bx in range(src_x, x + step, step):
                direction = Direction.LEFT_TO_RIGHT if step > 0 else Direction.RIGHT_TO_LEFT
                place_belt(bx, top_belt_y, direction)

    # 2) Place external outputs for machines whose output is exported.
    for machine_idx, machine_io in enumerate(machine_ios):
        if machine_io.output_item not in output_items:
            continue
        m_left = machine_left + machine_idx * machine_size
        out_x = m_left + (machine_size // 2)
        place_inserter(out_x, bottom_inserter_y, Direction.BOTTOM_TO_TOP)
        place_belt(out_x, bottom_belt_y, Direction.RIGHT_TO_LEFT)

    # Keep top and bottom buses continuous where they contain at least one segment.
    if 0 <= top_belt_y < height:
        xs = [x for x in range(width) if grid[top_belt_y][x] == Cell.BELT]
        if xs:
            for x in range(min(xs), max(xs) + 1):
                place_belt(x, top_belt_y, Direction.LEFT_TO_RIGHT)
    if 0 <= bottom_belt_y < height:
        xs = [x for x in range(width) if grid[bottom_belt_y][x] == Cell.BELT]
        if xs:
            for x in range(min(xs), max(xs) + 1):
                place_belt(x, bottom_belt_y, Direction.RIGHT_TO_LEFT)


def _add_machine_io_flow_constraints(
    model: cp_model.CpModel,
    spec: LineSpec,
    machine_ios: list[MachineIO],
) -> bool:
    belt_flow_vars: dict[tuple[int, int, str], cp_model.IntVar] = {}

    # Input feasibility: each machine input must come from belt input, box input,
    # or a belt-mediated transfer from a previous machine output.
    for dst_idx, machine_io in enumerate(machine_ios):
        for input_idx, input_item in enumerate(machine_io.input_items):
            candidates: list[cp_model.IntVar] = []

            if input_item in spec.hub_input_items:
                from_belt = model.NewBoolVar(f"in_{dst_idx}_{input_idx}_from_belt")
                candidates.append(from_belt)
            if input_item in spec.box_input_items:
                from_box = model.NewBoolVar(f"in_{dst_idx}_{input_idx}_from_box")
                candidates.append(from_box)

            for src_idx in range(dst_idx):
                if machine_ios[src_idx].output_item != input_item:
                    continue
                key = (src_idx, dst_idx, input_item)
                via_belt = belt_flow_vars.get(key)
                if via_belt is None:
                    via_belt = model.NewBoolVar(
                        f"via_belt_{src_idx}_to_{dst_idx}_{input_item}"
                    )
                    belt_flow_vars[key] = via_belt
                candidates.append(via_belt)

            if not candidates:
                return False
            model.Add(sum(candidates) == 1)

    # Output feasibility: each machine output must have exactly one destination.
    # Destinations are either a belt-mediated feed to a later machine, or export to sink.
    for src_idx, machine_io in enumerate(machine_ios):
        out_item = machine_io.output_item
        destinations: list[cp_model.IntVar] = []

        for dst_idx in range(src_idx + 1, len(machine_ios)):
            key = (src_idx, dst_idx, out_item)
            via_belt = belt_flow_vars.get(key)
            if via_belt is None:
                continue
            destinations.append(via_belt)

        if out_item in spec.output_items:
            to_sink = model.NewBoolVar(f"out_{src_idx}_to_sink")
            destinations.append(to_sink)

        if not destinations:
            return False
        model.Add(sum(destinations) == 1)

    return True


def _add_io_lane_constraints(
    model: cp_model.CpModel,
    tile_height: int,
    machine_top: int,
    machine_size: int,
    input_items: tuple[str, ...],
    output_items: tuple[str, ...],
    io_row_vars: list[cp_model.IntVar],
    io_lane_vars: list[cp_model.IntVar],
    io_dir: list[Direction],
    io_item: list[str],
) -> None:
    input_bus_row = machine_top - 2
    output_bus_row = machine_top + machine_size + 1
    if input_items and not (0 <= input_bus_row < tile_height):
        return
    if output_items and not (0 <= output_bus_row < tile_height):
        return
    # Single belt row has two lanes.
    if len(input_items) > 2 or len(output_items) > 2:
        return

    # Create vars for all bus I/O labels.
    for idx, item in enumerate(input_items):
        row = model.NewIntVar(input_bus_row, input_bus_row, f"in_row_{idx}")
        lane = model.NewIntVar(idx % 2, idx % 2, f"in_lane_{idx}")
        io_row_vars.append(row)
        io_lane_vars.append(lane)
        io_dir.append(Direction.LEFT_TO_RIGHT)
        io_item.append(item)

    in_count = len(input_items)
    for idx, item in enumerate(output_items):
        row = model.NewIntVar(output_bus_row, output_bus_row, f"out_row_{idx}")
        lane = model.NewIntVar(idx % 2, idx % 2, f"out_lane_{idx}")
        io_row_vars.append(row)
        io_lane_vars.append(lane)
        io_dir.append(Direction.RIGHT_TO_LEFT)
        io_item.append(item)

    if not io_row_vars:
        return

    # No two labels can use the same row+lane slot.
    slot_vars: list[cp_model.IntVar] = []
    for idx, row in enumerate(io_row_vars):
        slot = model.NewIntVar(0, tile_height * 2 - 1, f"io_slot_{idx}")
        model.Add(slot == row * 2 + io_lane_vars[idx])
        slot_vars.append(slot)
    model.AddAllDifferent(slot_vars)
