"""Round-trip key generation, did:key encode/decode, signature sanity."""

from __future__ import annotations

import pytest

from agent_id.keys import (
    base58btc_decode,
    base58btc_encode,
    did_key_from_public_key,
    ed25519_sign,
    ed25519_verify,
    generate_key_pair,
    public_key_from_did_key,
    verification_method_id,
)


def test_roundtrip_did_key():
    kp = generate_key_pair()
    did = did_key_from_public_key(kp.public_key)
    assert did.startswith("did:key:z")
    assert public_key_from_did_key(did) == kp.public_key


def test_did_key_rejects_wrong_length():
    with pytest.raises(ValueError, match="32 bytes"):
        did_key_from_public_key(b"\x00" * 31)


def test_did_key_rejects_wrong_method():
    with pytest.raises(ValueError, match="did:key"):
        public_key_from_did_key("did:web:example.com")


def test_verification_method_id_for_did_key():
    did = "did:key:z6Mkon3Necd6NkkyfoGoHxid2znGc59LU3K7mubaRcFbLfLX"
    vm = verification_method_id(did)
    assert vm == f"{did}#z6Mkon3Necd6NkkyfoGoHxid2znGc59LU3K7mubaRcFbLfLX"


def test_signature_roundtrip():
    kp = generate_key_pair()
    msg = b"hello agent-id"
    sig = ed25519_sign(kp.private_key, msg)
    assert ed25519_verify(kp.public_key, msg, sig)
    assert not ed25519_verify(kp.public_key, b"tampered", sig)


def test_base58btc_roundtrip():
    data = bytes(range(64))
    enc = base58btc_encode(data)
    assert enc.startswith("z")
    assert base58btc_decode(enc) == data
