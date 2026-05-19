# Contributing

Thanks for considering a contribution.

## Quick setup

```bash
git clone https://github.com/p-vbordei/agent-id-py
cd agent-id-py

uv venv -p 3.13
uv pip install -e ".[dev]"
uv run pytest -v
uv run ruff check .
```

## What to know before sending a PR

1. **Conformance vectors are the contract.** Any change that affects serialization must keep the existing `vectors/*.json` tests green. If you need to change the wire format, propose it upstream in the [TS reference](https://github.com/p-vbordei/agent-id) first.

2. **Cross-port consistency.** If you change behaviour here, please open a tracking issue on the sibling port ([agent-id-rs](https://github.com/p-vbordei/agent-id-rs)) so it doesn't drift.

3. **Tests + lints** must pass locally before pushing. CI re-runs them on every PR.

4. **Idiomatic Python over TS parity.** This port is allowed to use Python-idiomatic naming (snake_case function names, dataclasses, type hints) as long as the wire format and conformance behaviour are unchanged.

## Release process

We use semver. Bump `version` in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`, push.
