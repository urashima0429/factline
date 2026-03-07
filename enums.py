from enum import Enum, IntEnum, auto


class MachineKind(Enum):
    ASSEMBLER_3X3 = auto()
    PLANT_4X4 = auto()


class TileKind(Enum):
    EMPTY = auto()
    MACHINE = auto()
    BELT = auto()
    UNDERGROUND_BELT_IN = auto()
    UNDERGROUND_BELT_OUT = auto()
    INSERTER = auto()


class Direction(Enum):
    TOP_TO_BOTTOM = auto()
    BOTTOM_TO_TOP = auto()
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()


class FluidInputFrom(Enum):
    # Machines without fluid input ports can use NONE.
    NONE = auto()
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


# Legacy tile enum kept for compatibility while migrating to split enums.
class Cell(IntEnum):
    EMPTY = 0
    MACHINE = 1
    BELT = 2
    UNDER_IN = 4
    UNDER_OUT = 5
    INSERTER = 6


CELL_TO_CHAR = {
    Cell.EMPTY: " ",        # 空白
    Cell.MACHINE: "M",      # 組立機
    Cell.BELT: "B",         # ベルト
    Cell.UNDER_IN: "U",     # 地下ベルト入口
    Cell.UNDER_OUT: "D",    # 地下ベルト出口
    Cell.INSERTER: "I",     # インサータ
}
