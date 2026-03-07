from dataclasses import dataclass
from typing import List

from enums import Cell, MachineKind


@dataclass(frozen=True)
class LineSpec:
    machine_kind: MachineKind
    width: int
    input_count: int
    has_output: bool = True


@dataclass(frozen=True)
class SolveConfig:
    min_height: int = 3
    max_height: int = 20


@dataclass
class Solution:
    height: int
    width: int
    machine_top: int
    grid: List[List[Cell]]
