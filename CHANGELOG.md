# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-19

### Added
- Initial Python port of [`@p-vbordei/agent-id`](https://github.com/p-vbordei/agent-id) v1.0 spec.
- `did:key` (Ed25519) + `did:web` resolution.
- Capability VC issue + verify with the `eddsa-jcs-2022` cryptosuite.
- JSON-Schema 2020-12 validation of the Capability VC.
- Passes all C1 / C2 / C3 conformance vectors byte-identical with the TS reference.
- Runnable `examples/quickstart.py` demo.

[Unreleased]: https://github.com/p-vbordei/agent-id-py/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/p-vbordei/agent-id-py/releases/tag/v0.1.0
