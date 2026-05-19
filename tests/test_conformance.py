"""Run the canonical TS conformance vectors against the Python port."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agent_id.types import FetchResponse, VerifyOptions
from agent_id.vc import verify

VECTORS_DIR = Path(__file__).resolve().parent.parent / "vectors"
REQUIRED_CLAUSES = {"C1", "C2", "C3"}


def _load_vectors() -> list[dict]:
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(VECTORS_DIR.glob("*.json"))
        if not p.name.startswith("fixtures")
    ]


def _stub_fetch(fixtures: dict[str, dict]):
    async def fetch(url: str) -> FetchResponse:
        for k, v in fixtures.items():
            if url == k:
                return {"status": 200, "headers": {}, "body": json.dumps(v).encode("utf-8")}
        return {"status": 404, "headers": {}, "body": b"not found"}

    return fetch


def test_clauses_present():
    seen = {v["clause"] for v in _load_vectors()}
    missing = REQUIRED_CLAUSES - seen
    assert not missing, f"missing conformance clauses: {missing}"


@pytest.mark.parametrize("vector", _load_vectors(), ids=lambda v: f"{v['clause']}-{v['name']}")
async def test_vector(vector):
    opts = VerifyOptions()
    if "now" in vector:
        opts.now = datetime.fromisoformat(vector["now"].replace("Z", "+00:00")).astimezone(timezone.utc)
    if "didWebFixtures" in vector:
        opts.fetch = _stub_fetch(vector["didWebFixtures"])

    res = await verify(vector["vc"], opts)
    expected = vector["expect"]
    assert res.verified == expected["verified"], (
        f"verified mismatch: got {res.verified}, expected {expected['verified']}, "
        f"errors={res.errors}"
    )
    for pat in expected.get("errorMatches", []):
        assert any(re.search(pat, e) for e in res.errors), (
            f"no error matched pattern {pat!r}; errors={res.errors}"
        )
