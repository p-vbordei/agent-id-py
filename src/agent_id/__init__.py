"""agent-id — self-custody DID + capability VC profile for AI agents."""

from .keys import (
    did_key_from_public_key,
    generate_key_pair,
    public_key_from_did_key,
    verification_method_id,
)
from .resolve import resolve
from .types import (
    CONTEXT_AGENT_V1,
    CONTEXT_V2,
    Capability,
    CredentialSubject,
    DidDocument,
    IssueOptions,
    KeyPair,
    Model,
    Proof,
    ResolveOptions,
    SLA,
    VerifiableCredential,
    VerificationMethod,
    VerifyOptions,
    VerifyResult,
)
from .vc import issue, verify

__all__ = [
    "CONTEXT_AGENT_V1",
    "CONTEXT_V2",
    "Capability",
    "CredentialSubject",
    "DidDocument",
    "IssueOptions",
    "KeyPair",
    "Model",
    "Proof",
    "ResolveOptions",
    "SLA",
    "VerifiableCredential",
    "VerificationMethod",
    "VerifyOptions",
    "VerifyResult",
    "did_key_from_public_key",
    "generate_key_pair",
    "issue",
    "public_key_from_did_key",
    "resolve",
    "verification_method_id",
    "verify",
]
