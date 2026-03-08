import argparse

from input_loader import load_spec
from render import render_solution
from solver import solve_first_feasible


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to input JSON file")
    args = parser.parse_args()

    try:
        spec = load_spec(args.input)
    except Exception as exc:
        print(f"INVALID INPUT: {exc}")
        return

    solution = solve_first_feasible(spec)
    if solution is None:
        print("UNSAT")
        return

    print(render_solution(solution))


if __name__ == "__main__":
    main()
