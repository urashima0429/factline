from enum import Enum, IntEnum, auto


class Cell(IntEnum):
    EMPTY = 0
    BELT = auto()
    UNDER_IN = auto()
    UNDER_OUT = auto()
    INSERTER = auto()
    MACHINE = auto()
    BOX = auto()
    PIPE = auto()


class Direction(IntEnum):
    NONE = 0
    TOP_TO_BOTTOM = auto()
    BOTTOM_TO_TOP = auto()
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()


class Lane(IntEnum):
    NONE = 0
    LEFT = auto()
    RIGHT = auto()


class MachineKind(Enum):
    ASSEMBLER_3X3 = "ASSEMBLER_3X3"
    PLANT_4X4 = "PLANT_4X4"


CELL_TO_CHAR: dict[Cell, str] = {
    Cell.EMPTY: " ",
    Cell.BELT: "B",
    Cell.UNDER_IN: "S",
    Cell.UNDER_OUT: "T",
    Cell.INSERTER: "I",
    Cell.MACHINE: "M",
    Cell.BOX: "C",
    Cell.PIPE: "P",
}
