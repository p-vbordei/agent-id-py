# Architecture — agent-id (Python)

## Goal

Port the [agent-id v1.0 spec](../SPEC.md) to Python with byte-deterministic compatibility with the [TypeScript reference](https://github.com/p-vbordei/agent-id). The same JCS canonical bytes, the same `did:key` encoding, the same `eddsa-jcs-2022` proofs.

## Module map

| File | TS counterpart | Role |
|---|---|---|
| `src/agent_id/__init__.py` | `src/index.ts` | Public API barrel |
| `src/agent_id/types.py` | `src/types.ts` | Public types (`KeyPair`, `VerifiableCredential`, `IssueOptions`, ...) |
| `src/agent_id/jcs.py` | `src/jcs.ts` | RFC 8785 canonicalization + SHA-256 hash helper |
| `src/agent_id/keys.py` | `src/keys.ts` | Ed25519 keygen, sign / verify, `did:key` codec, base58btc multibase |
| `src/agent_id/resolve.py` | `src/resolve.ts` | `did:key` (algorithmic) + `did:web` (HTTP) resolution |
| `src/agent_id/vc.py` | `src/vc.ts` | `issue()` / `verify()` with `eddsa-jcs-2022` |
| `src/agent_id/schema.py` | `src/schema.ts` | JSON-Schema 2020-12 validation of the Capability VC |

The JSON-LD context and JSON-Schema are bundled into the wheel via `[tool.hatch.build.targets.wheel.force-include]`, so the library has no runtime file-system dependency on the source tree.

## Key dependency choices

| Concern | Library | Why |
|---|---|---|
| Ed25519 | [`cryptography`](https://cryptography.io) | Audited, hazmat-level Ed25519 API matching RFC 8032 |
| JCS (RFC 8785) | [`jcs`](https://pypi.org/project/jcs/) | Spec-correct canonical JSON; integer / float handling matches the TS reference |
| base58btc multibase | [`base58`](https://pypi.org/project/base58/) | Encoding for the `did:key` multibase + multicodec prefix |
| JSON Schema | [`jsonschema`](https://pypi.org/project/jsonschema/) | Draft 2020-12 support |
| HTTP (did:web) | [`httpx`](https://www.python-httpx.org) | Async client with timeouts and response-size caps |

Five runtime deps total. Everything else is stdlib.

## Byte-determinism invariants

The port MUST produce the same bytes as the TS reference for:

1. `jcs.canonicalize(value)` — RFC 8785 JCS encoding.
2. `did_key_from_public_key(pk)` — `'z' || base58btc(0xed01 || pk)`.
3. The `proofValue` of any issued VC — Ed25519 signature over `sha256(JCS(proofConfig)) || sha256(JCS(unsigned))`.

The conformance vectors in `vectors/` lock these invariants. Any change to serialization MUST keep `pytest tests/test_conformance.py` green.

## Async surface

`issue()`, `verify()`, and `resolve()` are `async def`. `did:key` resolution is fully synchronous internally — the `async` keeps the API uniform with `did:web` and matches the TS reference shape. `generate_key_pair()` and `did_key_from_public_key()` are plain sync functions.

## Testing strategy

- **Unit tests** — `tests/test_jcs.py`, `tests/test_keys.py`, `tests/test_issue_verify.py` cover individual modules.
- **Conformance vectors** — `tests/test_conformance.py` loads the JSON vectors from `vectors/` and asserts pass / fail matches the expected outcome from the TS reference.
- **Cross-impl byte equality** — runs in the meta-repo (`agent-ports/scripts/`); confirms TS + Py + Rs emit identical canonical bytes on a common input.
