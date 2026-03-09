import json
from pathlib import Path

from enums import MachineKind
from models import LineSpec, MachineIO

DEFAULT_INPUT = {
    "bus_input_items": ["copper-plate", "iron-plate"],
    "box_input_items": [],
    "bus_output_items": ["electronic-circuit"],
    "box_output_items": [],
    "underground_max_distance": 4,
    "machines": [
        {
            "kind": "ASSEMBLER_3X3",
            "count": 1,
            "input_items": ["copper-plate"],
            "output_item": "copper-cable",
        },
        {
            "kind": "ASSEMBLER_3X3",
            "count": 1,
            "input_items": ["iron-plate", "copper-cable"],
            "output_item": "electronic-circuit",
        }
    ],
}


def load_spec(input_path: str | None) -> LineSpec:
    if input_path is None:
        data = DEFAULT_INPUT
    else:
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    bus_input_items = data.get("bus_input_items", [])
    if not isinstance(bus_input_items, list):
        raise ValueError("bus_input_items must be a list")
    normalized_bus_input_items = _normalize_item_list(bus_input_items, "bus_input_items")

    box_input_items = data.get("box_input_items", [])
    if not isinstance(box_input_items, list):
        raise ValueError("box_input_items must be a list")
    normalized_box_input_items = _normalize_item_list(box_input_items, "box_input_items")

    box_output_items = data.get("box_output_items", [])
    if not isinstance(box_output_items, list):
        raise ValueError("box_output_items must be a list")
    normalized_box_output_items = _normalize_item_list(box_output_items, "box_output_items")

    machines_raw = data.get("machines", [])
    if not isinstance(machines_raw, list) or len(machines_raw) == 0:
        raise ValueError("machines must be a non-empty list")

    underground_max_distance = int(data.get("underground_max_distance", 4))
    if underground_max_distance < 0:
        raise ValueError("underground_max_distance must be >= 0")

    machine_kinds: list[MachineKind] = []
    machine_ios: list[MachineIO] = []
    machine_count = 0
    for machine in machines_raw:
        if not isinstance(machine, dict):
            raise ValueError("each machines entry must be an object")
        kind = _parse_machine_kind(str(machine.get("kind", "")))
        count = int(machine.get("count", 0))
        if count <= 0:
            raise ValueError("machine count must be >= 1")
        machine_io = _parse_machine_io(machine)
        machine_kinds.append(kind)
        machine_count += count
        machine_ios.extend([machine_io] * count)

    first_kind = machine_kinds[0]
    if any(kind != first_kind for kind in machine_kinds):
        raise ValueError("mixed machine kinds are not supported yet")

    height = _fixed_height(first_kind)
    input_items_from_machines = {
        item for machine_io in machine_ios for item in machine_io.input_items
    }
    all_solid_input_items = (
        set(normalized_bus_input_items)
        | set(normalized_box_input_items)
        | input_items_from_machines
    )
    bus_output_items_raw = data.get("bus_output_items", [])
    if not isinstance(bus_output_items_raw, list):
        raise ValueError("bus_output_items must be a list")
    normalized_bus_output_items = _normalize_item_list(bus_output_items_raw, "bus_output_items")

    has_output = (
        (len(normalized_bus_output_items) > 0)
        or (len(box_output_items) > 0)
        or len(machine_ios) > 0
    )
    spec = LineSpec(
        machine_kind=first_kind,
        height=height,
        input_count=len(all_solid_input_items),
        underground_max_distance=underground_max_distance,
        bus_input_items=tuple(normalized_bus_input_items),
        box_input_items=tuple(normalized_box_input_items),
        bus_output_items=tuple(normalized_bus_output_items),
        box_output_items=tuple(normalized_box_output_items),
        has_output=has_output,
        machine_count=machine_count,
        machine_ios=tuple(machine_ios),
    )
    return spec


def _parse_machine_kind(value: str) -> MachineKind:
    normalized = value.strip().upper()
    if normalized == "ASSEMBLER_3X3":
        return MachineKind.ASSEMBLER_3X3
    if normalized == "PLANT_4X4":
        return MachineKind.PLANT_4X4
    raise ValueError(f"unsupported machine_kind: {value}")


def _fixed_height(machine_kind: MachineKind) -> int:
    if machine_kind == MachineKind.ASSEMBLER_3X3:
        return 7
    return 8


def _parse_machine_io(machine: dict) -> MachineIO:
    if "recipe" in machine:
        raise ValueError("machine recipe is no longer supported; use input_items/input_fluid/output_item")

    input_items = machine.get("input_items", [])
    if not isinstance(input_items, list):
        raise ValueError("machine input_items must be a list")
    normalized_input_items: list[str] = []
    for item in input_items:
        name = str(item).strip()
        if name == "":
            raise ValueError("machine input_items cannot contain empty values")
        normalized_input_items.append(name)
    if len(normalized_input_items) == 0:
        raise ValueError("machine input_items must be non-empty")

    raw_input_fluid = machine.get("input_fluid")
    if raw_input_fluid is None:
        input_fluid = None
    else:
        input_fluid = str(raw_input_fluid).strip()
        if input_fluid == "":
            raise ValueError("machine input_fluid must be non-empty when provided")

    raw_output_item = machine.get("output_item")
    if raw_output_item is None:
        raise ValueError("machine output_item is required")
    output_item = str(raw_output_item).strip()
    if output_item == "":
        raise ValueError("machine output_item must be non-empty")

    return MachineIO(
        input_items=tuple(normalized_input_items),
        output_item=output_item,
        input_fluid=input_fluid,
    )


def _normalize_item_list(values: list[object], field_name: str) -> list[str]:
    result: list[str] = []
    for raw in values:
        item = str(raw).strip()
        if item == "":
            raise ValueError(f"{field_name} cannot contain empty values")
        result.append(item)
    return result
