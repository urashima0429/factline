import argparse

from input_loader import load_spec_and_config
from render import render_solution
from solver import solve_first_feasible


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to input JSON file")
    args = parser.parse_args()

    try:
        spec, config = load_spec_and_config(args.input)
    except Exception as exc:
        print(f"INVALID INPUT: {exc}")
        return

    solution = solve_first_feasible(spec, config.min_height, config.max_height)
    if solution is None:
        print("UNSAT")
        return

    print(render_solution(solution))


if __name__ == "__main__":
    main()
