import json
from pathlib import Path

from enums import MachineKind
from models import LineSpec, SolveConfig

DEFAULT_INPUT = {
    "machine_kind": "ASSEMBLER_3X3",
    "width": 7,
    "input_items": ["iron-plate"],
    "output_item": "gear-wheel",
    "min_height": 3,
    "max_height": 10,
}


def load_spec_and_config(input_path: str | None) -> tuple[LineSpec, SolveConfig]:
    if input_path is None:
        data = DEFAULT_INPUT
    else:
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    machine_kind = _parse_machine_kind(data.get("machine_kind", "ASSEMBLER_3X3"))
    width = int(data.get("width", 7))
    input_items = data.get("input_items", [])
    if not isinstance(input_items, list):
        raise ValueError("input_items must be a list")

    has_output = data.get("output_item") is not None
    spec = LineSpec(
        machine_kind=machine_kind,
        width=width,
        input_count=len(input_items),
        has_output=has_output,
    )
    config = SolveConfig(
        min_height=int(data.get("min_height", 3)),
        max_height=int(data.get("max_height", 20)),
    )
    return spec, config


def _parse_machine_kind(value: str) -> MachineKind:
    normalized = value.strip().upper()
    if normalized == "ASSEMBLER_3X3":
        return MachineKind.ASSEMBLER_3X3
    if normalized == "PLANT_4X4":
        return MachineKind.PLANT_4X4
    raise ValueError(f"unsupported machine_kind: {value}")
