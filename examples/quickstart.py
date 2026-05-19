"""Minimal end-to-end demo: principal issues a Capability VC for an agent, then verifies it.

Mirrors examples/demo.ts from the TypeScript reference.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from agent_id import (
    IssueOptions,
    did_key_from_public_key,
    generate_key_pair,
    issue,
    verify,
)


async def main() -> None:
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
                "valid_from": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            },
        )
    )

    print(f"issued VC for {vc['credentialSubject']['id']}")

    result = await verify(vc)
    print(f"verified  = {result.verified}")
    if result.errors:
        for err in result.errors:
            print(f"  - {err}")


if __name__ == "__main__":
    asyncio.run(main())
