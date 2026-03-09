import unittest
from pathlib import Path

from input_loader import load_spec
from render import render_solution
from solver import solve_first_feasible


ROOT = Path(__file__).resolve().parents[1]


class LayoutCaseTest(unittest.TestCase):
    CASES = [
        {
            "name": "sample_input_00_bootstrap_layout",
            "input": ROOT / "sample_input_00.json",
        },
        {
            "name": "sample_input_01_bootstrap_layout",
            "input": ROOT / "sample_input_01.json",
        },
        {
            "name": "sample_input_02_bootstrap_layout_even_if_underground_short",
            "input": ROOT / "sample_input_02_too_short_underground.json",
        },
    ]

    def test_cases(self) -> None:
        for case in self.CASES:
            with self.subTest(case=case["name"]):
                spec = load_spec(str(case["input"]))
                solution = solve_first_feasible(spec)
                self.assertIsNotNone(solution)
                assert solution is not None

                self.assertGreaterEqual(solution.width, 1)
                self.assertEqual(solution.height, spec.height)

                rendered = render_solution(solution)
                lines = rendered.splitlines()

                # Header (3 lines) + each tile row rendered as 2 lines.
                self.assertEqual(len(lines), 3 + solution.height * 2)


if __name__ == "__main__":
    unittest.main()
