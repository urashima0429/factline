from dataclasses import dataclass
from typing import List

from enums import Cell, Direction, Lane, MachineKind


@dataclass(frozen=True)
class MachineIO:
    input_items: tuple[str, ...]
    output_item: str
    input_fluid: str | None = None


@dataclass(frozen=True)
class LineSpec:
    machine_kind: MachineKind
    height: int
    input_count: int
    underground_max_distance: int = 4
    bus_input_items: tuple[str, ...] = ()
    box_input_items: tuple[str, ...] = ()
    bus_output_items: tuple[str, ...] = ()
    box_output_items: tuple[str, ...] = ()
    has_output: bool = True
    machine_count: int = 1
    machine_ios: tuple[MachineIO, ...] = ()


@dataclass(frozen=True)
class IOLabel:
    tile_y: int
    direction: Direction
    lane: Lane
    item: str


@dataclass
class Solution:
    height: int
    width: int
    machine_top: int
    grid: List[List[Cell]]
    belt_directions: List[List[Direction | None]]
    belt_lanes: List[List[Lane | None]]
    inserter_directions: List[List[Direction | None]]
    machine_regions: List[tuple[int, int, int]]
    io_labels: tuple[IOLabel, ...]
