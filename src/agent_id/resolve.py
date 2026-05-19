"""DID resolution for did:key and did:web."""

from __future__ import annotations

from typing import Any

import httpx

from .keys import public_key_from_did_key
from .types import DidDocument, ResolveOptions

DEFAULT_FETCH_TIMEOUT_MS = 5000
DEFAULT_MAX_RESPONSE_BYTES = 1024 * 1024


async def resolve(did: str, opts: ResolveOptions | None = None) -> DidDocument:
    opts = opts or ResolveOptions()
    if did.startswith("did:key:"):
        return _resolve_did_key(did)
    if did.startswith("did:web:"):
        return await _resolve_did_web(did, opts)
    raise ValueError(f"unsupported DID method: {did}")


def _resolve_did_key(did: str) -> DidDocument:
    # Throws on malformed or non-Ed25519.
    public_key_from_did_key(did)
    fragment = did[len("did:key:") :]
    vm_id = f"{did}#{fragment}"
    return {
        "@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/multikey/v1"],
        "id": did,
        "verificationMethod": [
            {
                "id": vm_id,
                "type": "Multikey",
                "controller": did,
                "publicKeyMultibase": fragment,
            }
        ],
        "assertionMethod": [vm_id],
        "authentication": [vm_id],
    }


async def _resolve_did_web(did: str, opts: ResolveOptions) -> DidDocument:
    url = _did_web_to_url(did)
    timeout_s = opts.fetch_timeout_ms / 1000
    max_bytes = opts.max_response_bytes

    if opts.fetch is not None:
        resp = await opts.fetch(url)
        status = resp.get("status", 0)
        if status < 200 or status >= 300:
            raise RuntimeError(f"did:web fetch failed: {status}")
        body = resp.get("body", b"")
        if len(body) > max_bytes:
            raise RuntimeError(
                f"did:web response too large: {len(body)} bytes exceeds limit {max_bytes}"
            )
        import json

        doc: DidDocument = json.loads(body.decode("utf-8"))
    else:
        try:
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                resp = await client.get(url)
        except httpx.TimeoutException as err:
            raise RuntimeError(
                f"did:web fetch timed out after {opts.fetch_timeout_ms}ms ({url})"
            ) from err

        if resp.status_code < 200 or resp.status_code >= 300:
            raise RuntimeError(
                f"did:web fetch failed: {resp.status_code} {resp.reason_phrase}"
            )
        cl = resp.headers.get("content-length")
        if cl is not None:
            try:
                size = int(cl)
                if size > max_bytes:
                    raise RuntimeError(
                        f"did:web response too large: {size} bytes exceeds limit {max_bytes}"
                    )
            except ValueError:
                pass
        body_bytes = resp.content
        if len(body_bytes) > max_bytes:
            raise RuntimeError(
                f"did:web response too large: {len(body_bytes)} bytes exceeds limit {max_bytes}"
            )
        doc = resp.json()

    if doc.get("id") != did:
        raise RuntimeError(f"did:web document id mismatch: expected {did}, got {doc.get('id')}")
    return doc


def _did_web_to_url(did: str) -> str:
    from urllib.parse import unquote

    rest = did[len("did:web:") :]
    parts = [unquote(p) for p in rest.split(":")]
    host = parts[0] if parts else ""
    if not host:
        raise ValueError(f"invalid did:web: empty host in {did}")
    if any(p == "" for p in parts[1:]):
        raise ValueError(f"invalid did:web: empty segment in {did}")
    if len(parts) == 1:
        return f"https://{host}/.well-known/did.json"
    path = "/".join(parts[1:])
    return f"https://{host}/{path}/did.json"
