from enums import CELL_TO_CHAR
from models import Solution
from enums import Cell, Direction, Lane


def render_solution(solution: Solution) -> str:
    lines = [
        f"height={solution.height}",
        f"width={solution.width}",
        f"machine_top={solution.machine_top}",
    ]

    canvas = _build_2x2_canvas(solution)
    line_labels = _build_line_labels(solution)
    label_width = max((len(label) for label in line_labels), default=0)
    for y, row in enumerate(canvas):
        label = line_labels[y] if y < len(line_labels) else ""
        left = f"{label:<{label_width}} | " if label_width > 0 else ""
        lines.append(f"{left}{''.join(row)}")

    return "\n".join(lines)


def _build_2x2_canvas(solution: Solution) -> list[list[str]]:
    h2 = solution.height * 2
    w2 = solution.width * 2
    canvas = [[" " for _ in range(w2)] for _ in range(h2)]

    for y, row in enumerate(solution.grid):
        for x, cell in enumerate(row):
            px = x * 2
            py = y * 2
            if cell == Cell.EMPTY:
                continue
            if cell == Cell.BELT:
                d = _belt_dir_char(solution, x, y)
                canvas[py][px] = "B"
                canvas[py][px + 1] = d
                canvas[py + 1][px] = d
                canvas[py + 1][px + 1] = d
                continue
            if cell == Cell.UNDER_IN:
                d = _belt_dir_char(solution, x, y)
                canvas[py][px] = "S"
                canvas[py][px + 1] = d
                canvas[py + 1][px] = d
                canvas[py + 1][px + 1] = d
                continue
            if cell == Cell.UNDER_OUT:
                d = _belt_dir_char(solution, x, y)
                canvas[py][px] = "T"
                canvas[py][px + 1] = d
                canvas[py + 1][px] = d
                canvas[py + 1][px + 1] = d
                continue
            if cell == Cell.INSERTER:
                d = _inserter_dir_char(solution, x, y)
                canvas[py][px] = "I"
                canvas[py][px + 1] = d
                canvas[py + 1][px] = d
                canvas[py + 1][px + 1] = d
                continue
            if cell == Cell.MACHINE:
                # Machine is drawn as one outer frame later.
                continue

            base = CELL_TO_CHAR[cell]
            canvas[py][px] = base
            canvas[py][px + 1] = base
            canvas[py + 1][px] = base
            canvas[py + 1][px + 1] = base

    _draw_machine_frames(solution, canvas)
    return canvas


def _belt_dir_char(solution: Solution, x: int, y: int) -> str:
    direction = solution.belt_directions[y][x]
    if direction == Direction.NONE:
        return "?"
    if direction == Direction.TOP_TO_BOTTOM:
        return "v"
    if direction == Direction.BOTTOM_TO_TOP:
        return "^"
    if direction == Direction.LEFT_TO_RIGHT:
        return ">"
    if direction == Direction.RIGHT_TO_LEFT:
        return "<"
    return ">"


def _inserter_dir_char(solution: Solution, x: int, y: int) -> str:
    direction = solution.inserter_directions[y][x]
    if direction == Direction.NONE:
        return "?"
    if direction == Direction.TOP_TO_BOTTOM:
        return "v"
    if direction == Direction.BOTTOM_TO_TOP:
        return "^"
    if direction == Direction.LEFT_TO_RIGHT:
        return ">"
    if direction == Direction.RIGHT_TO_LEFT:
        return "<"
    return ">"


def _draw_machine_frames(solution: Solution, canvas: list[list[str]]) -> None:
    for top_y, left_x, size in solution.machine_regions:
        _draw_single_machine_frame(canvas, top_y, left_x, size)


def _draw_single_machine_frame(
    canvas: list[list[str]],
    top_y: int,
    left_x: int,
    size: int,
) -> None:
    left = left_x * 2
    right = (left_x + size) * 2 - 1
    top = top_y * 2
    bottom = (top_y + size) * 2 - 1

    canvas[top][left] = "┌"
    canvas[top][right] = "┐"
    canvas[bottom][left] = "└"
    canvas[bottom][right] = "┘"
    for px in range(left + 1, right):
        canvas[top][px] = "─"
        canvas[bottom][px] = "─"
    for py in range(top + 1, bottom):
        canvas[py][left] = "│"
        canvas[py][right] = "│"

    m_x = left_x * 2 + 1
    m_y = top_y * 2 + 1
    canvas[m_y][m_x] = "M"


def _build_line_labels(solution: Solution) -> list[str]:
    labels = ["" for _ in range(solution.height * 2)]
    for io in solution.io_labels:
        line_y = _line_index(io.tile_y, io.direction, io.lane)
        if line_y < 0 or line_y >= len(labels):
            continue
        prefix = _direction_prefix(io.direction)
        text = f"{prefix}{io.item}"
        if labels[line_y] == "":
            labels[line_y] = text
        else:
            labels[line_y] = f"{labels[line_y]} {text}"
    return labels


def _line_index(tile_y: int, direction: Direction, lane: Lane) -> int:
    base = tile_y * 2
    if direction == Direction.NONE:
        return base
    if lane == Lane.NONE:
        lane = Lane.LEFT
    if direction == Direction.LEFT_TO_RIGHT:
        return base if lane == Lane.LEFT else base + 1
    if direction == Direction.RIGHT_TO_LEFT:
        return base + 1 if lane == Lane.LEFT else base
    if direction == Direction.TOP_TO_BOTTOM:
        return base if lane == Lane.LEFT else base + 1
    return base + 1 if lane == Lane.LEFT else base


def _direction_prefix(direction: Direction) -> str:
    if direction == Direction.NONE:
        return "?"
    if direction == Direction.LEFT_TO_RIGHT:
        return ">"
    if direction == Direction.RIGHT_TO_LEFT:
        return "<"
    if direction == Direction.TOP_TO_BOTTOM:
        return "v"
    return "^"
