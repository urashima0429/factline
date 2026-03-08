import unittest
from pathlib import Path

from input_loader import load_spec
from render import render_solution
from solver import solve_first_feasible


ROOT = Path(__file__).resolve().parents[1]


class LayoutCaseTest(unittest.TestCase):
    CASES = [
        {
            "name": "sample_input_min_width_is_6_tiles_with_top_bottom_io",
            "input": ROOT / "sample_input.json",
            "expected_width": 6,
            "expected_height": 7,
        },
    ]

    def test_cases(self) -> None:
        for case in self.CASES:
            with self.subTest(case=case["name"]):
                spec = load_spec(str(case["input"]))
                solution = solve_first_feasible(spec)
                self.assertIsNotNone(solution)
                assert solution is not None

                self.assertEqual(solution.width, case["expected_width"])
                self.assertEqual(solution.height, case["expected_height"])

                rendered = render_solution(solution)
                lines = rendered.splitlines()

                # Header (3 lines) + each tile row rendered as 2 lines.
                self.assertEqual(len(lines), 3 + solution.height * 2)


if __name__ == "__main__":
    unittest.main()
