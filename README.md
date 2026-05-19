# agent-id (Python)

[![CI](https://github.com/p-vbordei/agent-id-py/actions/workflows/ci.yml/badge.svg)](https://github.com/p-vbordei/agent-id-py/actions/workflows/ci.yml)
[![Spec v1.0](https://img.shields.io/badge/spec-v1.0-blue)](./SPEC.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)

> **Idiomatic Python port of [`@p-vbordei/agent-id`](https://github.com/p-vbordei/agent-id).** Self-custody DID + capability Verifiable Credential profile for AI agents. Byte-deterministic-compatible with the TypeScript reference: passes the same C1 / C2 / C3 conformance vectors. 17 tests pass.

## What's in the box

- `generate_key_pair()` / `did_key_from_public_key()` — Ed25519 keys + `did:key` codec.
- `issue(opts)` — sign a Capability VC with the `eddsa-jcs-2022` cryptosuite.
- `verify(vc)` — JSON-Schema → validity window → signature → DID resolution, accumulating errors.
- `resolve(did)` — `did:key` (offline) and `did:web` (HTTP, with timeout + response cap) resolution.

## Install

```bash
pip install agent-id
# or
uv add agent-id
```

## Quickstart

```python
import asyncio
from agent_id import IssueOptions, did_key_from_public_key, generate_key_pair, issue, verify

async def main() -> None:
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

    result = await verify(vc)
    print(f"issued VC for {vc['credentialSubject']['id']}")
    print(f"verified  = {result.verified}")

asyncio.run(main())
```

Run it:

```bash
python examples/quickstart.py
```

## How it relates

| Language | Repo | Notes |
|---|---|---|
| TypeScript (reference) | [agent-id](https://github.com/p-vbordei/agent-id) | canonical spec, conformance suite |
| Python | [agent-id-py](https://github.com/p-vbordei/agent-id-py) | this repo |
| Rust | [agent-id-rs](https://github.com/p-vbordei/agent-id-rs) | sibling port |

All three implementations produce **byte-identical** output for serialization-critical surfaces. See [docs/architecture.md](docs/architecture.md) for details.

## Conformance

```bash
uv run pytest -v          # runs the same C1 / C2 / C3 vectors as the TS reference
```

Vectors in `vectors/` are copied verbatim from the [TS conformance suite](https://github.com/p-vbordei/agent-id/tree/main/conformance). Pass / fail behaviour matches byte-for-byte.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the module layout, dependency choices, and byte-determinism invariants.

## Development

```bash
git clone https://github.com/p-vbordei/agent-id-py
cd agent-id-py
uv venv -p 3.13
uv pip install -e ".[dev]"
uv run pytest -v
uv run ruff check .
```

Contributions welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

Apache-2.0 — see [LICENSE](./LICENSE).
