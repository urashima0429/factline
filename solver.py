from enums import Cell, MachineKind
from models import LineSpec, Solution


def solve_first_feasible(spec: LineSpec, min_height: int, max_height: int) -> Solution | None:
    if spec.machine_kind == MachineKind.ASSEMBLER_3X3:
        machine_size = 3
        machine_left = 2
    else:
        machine_size = 4
        machine_left = 2

    for height in range(min_height, max_height + 1):
        if height < machine_size:
            continue

        machine_top = 0
        grid = [[Cell.EMPTY for _ in range(spec.width)] for _ in range(height)]

        for y in range(machine_top, machine_top + machine_size):
            for x in range(machine_left, machine_left + machine_size):
                grid[y][x] = Cell.MACHINE

        _place_placeholder_io(
            grid=grid,
            machine_top=machine_top,
            machine_left=machine_left,
            machine_size=machine_size,
            input_count=spec.input_count,
            has_output=spec.has_output,
        )

        return Solution(
            height=height,
            width=spec.width,
            machine_top=machine_top,
            grid=grid,
        )

    return None


def _place_placeholder_io(
    grid: list[list[Cell]],
    machine_top: int,
    machine_left: int,
    machine_size: int,
    input_count: int,
    has_output: bool,
) -> None:
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    input_belt_x = machine_left - 2
    input_inserter_x = machine_left - 1
    if input_belt_x >= 0:
        max_inputs = min(input_count, machine_size)
        for i in range(max_inputs):
            y = machine_top + i
            if y < 0 or y >= height:
                continue
            grid[y][input_belt_x] = Cell.BELT
            if input_inserter_x >= 0:
                grid[y][input_inserter_x] = Cell.INSERTER

    if has_output:
        y = machine_top + machine_size // 2
        output_inserter_x = machine_left + machine_size
        output_belt_x = output_inserter_x + 1
        if 0 <= y < height and 0 <= output_inserter_x < width:
            grid[y][output_inserter_x] = Cell.INSERTER
        if 0 <= y < height and 0 <= output_belt_x < width:
            grid[y][output_belt_x] = Cell.BELT
