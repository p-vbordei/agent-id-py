"""Public type definitions mirroring the TypeScript reference."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Literal, TypedDict

CONTEXT_V2 = "https://www.w3.org/ns/credentials/v2"
CONTEXT_AGENT_V1 = "https://agent-id.dev/context/v1"


@dataclass(frozen=True)
class KeyPair:
    public_key: bytes
    private_key: bytes


class Model(TypedDict, total=False):
    vendor: str
    id: str
    fingerprint: str


class SLA(TypedDict, total=False):
    latency_ms_p95: float
    availability: float
    token_budget: int


class Capability(TypedDict, total=False):
    action: str
    scope: list[str]
    sla: SLA


class CredentialSubject(TypedDict, total=False):
    id: str
    type: Literal["Agent"]
    principal: str
    model: Model
    capability: Capability
    valid_from: str
    valid_until: str


class Proof(TypedDict):
    type: Literal["DataIntegrityProof"]
    cryptosuite: Literal["eddsa-jcs-2022"]
    created: str
    verificationMethod: str
    proofPurpose: Literal["assertionMethod"]
    proofValue: str


class VerifiableCredential(TypedDict, total=False):
    # The "@context" key forces TypedDict-functional form; use dict[str, Any] in practice.
    pass


# Functional TypedDicts let us use the "@context" key with a hyphen-free Python name.
VerifiableCredential = TypedDict(  # type: ignore[misc]
    "VerifiableCredential",
    {
        "@context": list[str],
        "type": list[str],
        "issuer": str,
        "validFrom": str,
        "validUntil": str,
        "credentialSubject": CredentialSubject,
        "proof": Proof,
    },
    total=False,
)


class VerificationMethod(TypedDict, total=False):
    id: str
    type: Literal["Multikey", "Ed25519VerificationKey2020"]
    controller: str
    publicKeyMultibase: str


DidDocument = TypedDict(  # type: ignore[misc]
    "DidDocument",
    {
        "@context": str | list[str],
        "id": str,
        "verificationMethod": list[VerificationMethod],
        "assertionMethod": list[str | VerificationMethod],
        "authentication": list[str | VerificationMethod],
    },
    total=False,
)


@dataclass
class VerifyResult:
    verified: bool
    errors: list[str] = field(default_factory=list)


FetchFn = Callable[[str], Awaitable["FetchResponse"]]


class FetchResponse(TypedDict, total=False):
    """Minimal response surface — status, headers, body bytes."""
    status: int
    headers: dict[str, str]
    body: bytes


@dataclass
class VerifyOptions:
    now: datetime | None = None
    fetch: FetchFn | None = None
    skew_seconds: int = 300
    fetch_timeout_ms: int = 5000
    max_response_bytes: int = 1024 * 1024


@dataclass
class IssueOptions:
    principal: KeyPair
    subject: dict[str, Any]
    valid_from: str | None = None
    valid_until: str | None = None
    now: datetime | None = None
    issuer: str | None = None
    verification_method: str | None = None


@dataclass
class ResolveOptions:
    fetch: FetchFn | None = None
    fetch_timeout_ms: int = 5000
    max_response_bytes: int = 1024 * 1024
