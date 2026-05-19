# agent-id (Python)

[![CI](https://github.com/p-vbordei/agent-id-py/actions/workflows/ci.yml/badge.svg)](https://github.com/p-vbordei/agent-id-py/actions/workflows/ci.yml)
[![Spec v1.0](https://img.shields.io/badge/spec-v1.0-blue)](./SPEC.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)

> **Python port of [`@p-vbordei/agent-id`](https://github.com/p-vbordei/agent-id).** Self-custody DID + capability Verifiable Credential profile for AI agents. Byte-deterministic-compatible with the TypeScript reference: passes the same C1/C2/C3 conformance vectors.

```python
import asyncio
from agent_id import (
    IssueOptions, did_key_from_public_key, generate_key_pair, issue, verify,
)

async def main():
    principal = generate_key_pair()
    agent = generate_key_pair()

    vc = await issue(IssueOptions(
        principal=principal,
        subject={
            "id": did_key_from_public_key(agent.public_key),
            "type": "Agent",
            "principal": did_key_from_public_key(principal.public_key),
            "model": {"vendor": "anthropic", "id": "claude-opus-4-7"},
            "capability": {"action": "answer", "sla": {"latency_ms_p95": 2000}},
            "valid_from": "2026-04-24T00:00:00.000Z",
        },
    ))

    res = await verify(vc)
    print(res.verified)  # True

asyncio.run(main())
```

## Why this exists

This is a Python implementation of the [agent-id spec v1.0](./SPEC.md). The TypeScript reference defines the canonical wire format; this port follows it byte-for-byte for all serialization-critical surfaces (JCS, did:key encoding, eddsa-jcs-2022 proofs). If a vector passes in TS, it passes here.

See the [TS reference](https://github.com/p-vbordei/agent-id) for the full conceptual background.

## Install

```bash
uv add agent-id
# or
pip install agent-id
```

## DID methods supported

- **`did:key`** with Ed25519 (multicodec `0xed01`, base58btc multibase).
- **`did:web`** with Ed25519 verification methods.

## Verification

`verify(vc)` returns a `VerifyResult(verified: bool, errors: list[str])`. It checks:

1. JSON Schema (`schema/capability-v1.json`).
2. `validFrom` / `validUntil` window (±5 min clock skew default).
3. Signature: `Ed25519.verify(issuer_pk, sha256(JCS(proofConfig)) || sha256(JCS(unsigned)), proofValue)`.
4. Agent DID resolves and has at least one `verificationMethod`.

## Conformance

```bash
uv sync --extra dev
uv run pytest tests/test_conformance.py -v
```

Vectors in `vectors/` are copied verbatim from the [TS conformance suite](https://github.com/p-vbordei/agent-id/tree/main/conformance).

## License

Apache-2.0
