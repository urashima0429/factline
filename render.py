from enums import CELL_TO_CHAR
from models import Solution


def render_solution(solution: Solution) -> str:
    lines = [
        f"height={solution.height}",
        f"width={solution.width}",
        f"machine_top={solution.machine_top}",
    ]

    for row in solution.grid:
        lines.append("".join(CELL_TO_CHAR[cell] for cell in row))

    return "\n".join(lines)
