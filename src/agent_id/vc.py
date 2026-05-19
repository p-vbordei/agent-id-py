"""Issue and verify Capability Verifiable Credentials (eddsa-jcs-2022)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .jcs import jcs_hash
from .keys import (
    base58btc_decode,
    base58btc_encode,
    did_key_from_public_key,
    ed25519_sign,
    ed25519_verify,
    public_key_from_multibase,
    verification_method_id,
)
from .resolve import resolve
from .schema import validate_capability_vc
from .types import (
    CONTEXT_AGENT_V1,
    CONTEXT_V2,
    DidDocument,
    IssueOptions,
    ResolveOptions,
    VerifiableCredential,
    VerifyOptions,
    VerifyResult,
)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Mirror JS Date.toISOString(): "2026-04-24T00:00:00.000Z"
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


async def issue(opts: IssueOptions) -> VerifiableCredential:
    principal_did = opts.issuer or did_key_from_public_key(opts.principal.public_key)
    vm_id = opts.verification_method or verification_method_id(principal_did)
    now = opts.now or datetime.now(timezone.utc)
    subject = dict(opts.subject)
    subject.setdefault("principal", principal_did)

    unsigned: dict[str, Any] = {
        "@context": [CONTEXT_V2, CONTEXT_AGENT_V1],
        "type": ["VerifiableCredential", "AgentCapabilityCredential"],
        "issuer": principal_did,
        "validFrom": opts.valid_from or _iso(now),
        "credentialSubject": subject,
    }
    if opts.valid_until:
        unsigned["validUntil"] = opts.valid_until

    proof_config = {
        "@context": unsigned["@context"],
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "created": _iso(now),
        "verificationMethod": vm_id,
        "proofPurpose": "assertionMethod",
    }

    hash_data = jcs_hash(proof_config) + jcs_hash(unsigned)
    signature = ed25519_sign(opts.principal.private_key, hash_data)
    proof_value = base58btc_encode(signature)

    proof = {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "created": proof_config["created"],
        "verificationMethod": vm_id,
        "proofPurpose": "assertionMethod",
        "proofValue": proof_value,
    }
    return {**unsigned, "proof": proof}


async def verify(
    vc: VerifiableCredential | dict[str, Any],
    opts: VerifyOptions | None = None,
) -> VerifyResult:
    opts = opts or VerifyOptions()
    errors: list[str] = []

    if not isinstance(vc, dict):
        return VerifyResult(verified=False, errors=[f"vc must be an object, got {type(vc).__name__}"])

    schema_res = validate_capability_vc(vc)
    if not schema_res.valid:
        for e in schema_res.errors:
            errors.append(f"schema: {e}")

    # Validity window.
    now = opts.now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    skew_ms = opts.skew_seconds * 1000
    valid_from_s = vc.get("validFrom")
    valid_until_s = vc.get("validUntil")
    from_dt = _parse_rfc3339(valid_from_s) if valid_from_s else None
    until_dt = _parse_rfc3339(valid_until_s) if valid_until_s else None
    if valid_from_s is not None and from_dt is None:
        errors.append("validFrom is not a valid RFC 3339 date-time")
    elif from_dt is not None and (now.timestamp() * 1000 + skew_ms) < from_dt.timestamp() * 1000:
        errors.append(f"not yet valid (validFrom {valid_from_s})")
    if valid_until_s is not None:
        if until_dt is None:
            errors.append("validUntil is not a valid RFC 3339 date-time")
        elif (now.timestamp() * 1000 - skew_ms) > until_dt.timestamp() * 1000:
            errors.append(f"expired (validUntil {valid_until_s})")

    # Signature check.
    try:
        proof = vc.get("proof") or {}
        if (
            not proof
            or proof.get("type") != "DataIntegrityProof"
            or proof.get("cryptosuite") != "eddsa-jcs-2022"
        ):
            errors.append("proof missing or unsupported cryptosuite")
        else:
            proof_value = proof["proofValue"]
            proof_fields = {k: v for k, v in proof.items() if k != "proofValue"}
            proof_config_for_hash = {"@context": vc["@context"], **proof_fields}
            unsigned = {k: v for k, v in vc.items() if k != "proof"}

            hash_data = jcs_hash(proof_config_for_hash) + jcs_hash(unsigned)
            signature = base58btc_decode(proof_value)

            issuer_public_key: bytes | None = None
            try:
                issuer_doc = await resolve(vc["issuer"], _resolve_opts_from(opts))
                issuer_public_key = _extract_key_for_vm(issuer_doc, proof["verificationMethod"])
                if not issuer_public_key:
                    errors.append(
                        f"issuer DID document does not list verificationMethod "
                        f"{proof['verificationMethod']}"
                    )
            except Exception as err:
                errors.append(f"issuer resolution failed: {err}")

            if issuer_public_key:
                if not ed25519_verify(issuer_public_key, hash_data, signature):
                    errors.append("signature verification failed")
    except Exception as err:
        errors.append(f"signature check threw: {err}")

    # Agent DID resolution.
    try:
        agent_doc = await resolve(vc["credentialSubject"]["id"], _resolve_opts_from(opts))
        if not agent_doc.get("verificationMethod"):
            errors.append("agent DID document has no verificationMethod")
    except Exception as err:
        errors.append(f"agent DID resolution failed: {err}")

    return VerifyResult(verified=len(errors) == 0, errors=errors)


def _resolve_opts_from(opts: VerifyOptions) -> ResolveOptions:
    return ResolveOptions(
        fetch=opts.fetch,
        fetch_timeout_ms=opts.fetch_timeout_ms,
        max_response_bytes=opts.max_response_bytes,
    )


def _extract_key_for_vm(doc: DidDocument, vm_id: str) -> bytes | None:
    for vm in doc.get("verificationMethod", []) or []:
        if vm.get("id") == vm_id:
            mb = vm.get("publicKeyMultibase")
            if mb:
                return public_key_from_multibase(mb)
            return None
    return None


def _parse_rfc3339(s: str) -> datetime | None:
    try:
        # Python's fromisoformat handles "Z" only from 3.11+; normalise.
        norm = s.replace("Z", "+00:00") if s.endswith("Z") else s
        return datetime.fromisoformat(norm)
    except (ValueError, TypeError):
        return None
