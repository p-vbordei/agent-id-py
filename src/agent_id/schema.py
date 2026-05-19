"""JSON-Schema validation for the Capability VC."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@dataclass
class SchemaValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


def _load_schema() -> dict[str, Any]:
    raw = files("agent_id._data.schema").joinpath("capability-v1.json").read_text(encoding="utf-8")
    return json.loads(raw)


try:
    _SCHEMA = _load_schema()
except (FileNotFoundError, ModuleNotFoundError):
    # Dev path: read directly from repo root (src/agent_id/ → repo root is parents[2]).
    import pathlib

    _SCHEMA = json.loads(
        (pathlib.Path(__file__).resolve().parents[2] / "schema" / "capability-v1.json")
        .read_text(encoding="utf-8")
    )

_VALIDATOR = Draft202012Validator(_SCHEMA, format_checker=FormatChecker())


def validate_capability_vc(value: Any) -> SchemaValidationResult:
    errors = sorted(_VALIDATOR.iter_errors(value), key=lambda e: e.path)
    if not errors:
        return SchemaValidationResult(valid=True)
    msgs = [_format_error(e) for e in errors]
    return SchemaValidationResult(valid=False, errors=msgs)


def _format_error(err: Any) -> str:
    path = "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "/"
    return f"{path} {err.message}"
