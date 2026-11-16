"""Solution 02-1: add a unit_converter tool without touching lessons/02/tools.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lessons" / "02"))
from tools import TOOL_DEFINITIONS, ToolBox  # noqa: E402

UNIT_CONVERTER = {
    "name": "unit_converter",
    "description": (
        "Convert a value between units. Call this whenever the user asks to "
        "convert distance, temperature or weight."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "value": {"type": "number", "description": "The number to convert"},
            "from_unit": {"type": "string", "enum": ["km", "mi", "c", "f", "kg", "lb"]},
            "to_unit": {"type": "string", "enum": ["km", "mi", "c", "f", "kg", "lb"]},
        },
        "required": ["value", "from_unit", "to_unit"],
        "additionalProperties": False,
    },
}

_FACTORS = {("km", "mi"): 0.621371, ("mi", "km"): 1.609344, ("kg", "lb"): 2.204623, ("lb", "kg"): 0.45359237}


def convert(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return value
    if (from_unit, to_unit) == ("c", "f"):
        return value * 9 / 5 + 32
    if (from_unit, to_unit) == ("f", "c"):
        return (value - 32) * 5 / 9
    if (from_unit, to_unit) in _FACTORS:
        return value * _FACTORS[(from_unit, to_unit)]
    raise ValueError(f"cannot convert {from_unit} to {to_unit}")


class ExtendedToolBox(ToolBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.definitions = TOOL_DEFINITIONS + [UNIT_CONVERTER]
        self._schemas["unit_converter"] = UNIT_CONVERTER["input_schema"]

    def _dispatch(self, name: str, args: dict) -> str:
        if name == "unit_converter":
            allowed = UNIT_CONVERTER["input_schema"]["properties"]["from_unit"]["enum"]
            if args["from_unit"] not in allowed or args["to_unit"] not in allowed:
                raise ValueError(f"units must be one of {allowed}")
            return f"{convert(args['value'], args['from_unit'], args['to_unit']):.4g}"
        return super()._dispatch(name, args)
