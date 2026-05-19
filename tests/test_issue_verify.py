"""End-to-end: issue then verify a freshly generated VC."""

from __future__ import annotations

import pytest

from agent_id.keys import did_key_from_public_key, generate_key_pair
from agent_id.types import IssueOptions
from agent_id.vc import issue, verify


@pytest.mark.asyncio
async def test_roundtrip_issue_verify():
    principal = generate_key_pair()
    agent = generate_key_pair()

    vc = await issue(
        IssueOptions(
            principal=principal,
            subject={
                "id": did_key_from_public_key(agent.public_key),
                "type": "Agent",
                "principal": did_key_from_public_key(principal.public_key),
                "model": {"vendor": "anthropic", "id": "claude-opus-4-7"},
                "capability": {"action": "answer", "sla": {"latency_ms_p95": 2000}},
                "valid_from": "2026-04-24T00:00:00.000Z",
            },
        )
    )

    res = await verify(vc)
    assert res.verified is True, res.errors


@pytest.mark.asyncio
async def test_mutated_signature_fails():
    principal = generate_key_pair()
    agent = generate_key_pair()
    vc = await issue(
        IssueOptions(
            principal=principal,
            subject={
                "id": did_key_from_public_key(agent.public_key),
                "type": "Agent",
                "principal": did_key_from_public_key(principal.public_key),
                "model": {"vendor": "anthropic", "id": "claude-opus-4-7"},
                "capability": {"action": "answer"},
                "valid_from": "2026-04-24T00:00:00.000Z",
            },
        )
    )

    # Mutate the action: signature must fail.
    vc["credentialSubject"]["capability"]["action"] = "bnswer"
    res = await verify(vc)
    assert res.verified is False
    assert any("signature" in e for e in res.errors)
