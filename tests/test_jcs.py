"""JCS torture vectors — must match TS canonicalize() output byte-for-byte."""

from __future__ import annotations

from agent_id.jcs import canonical_json, jcs_hash


def test_object_key_sorting():
    out = canonical_json({"b": 1, "a": 2, "c": 3}).decode("utf-8")
    assert out == '{"a":2,"b":1,"c":3}'


def test_nested_sorting():
    out = canonical_json({"z": {"y": 1, "x": 2}, "a": [3, 1, 2]}).decode("utf-8")
    assert out == '{"a":[3,1,2],"z":{"x":2,"y":1}}'


def test_unicode_strings():
    out = canonical_json({"name": "Héllo, 世界"}).decode("utf-8")
    assert out == '{"name":"Héllo, 世界"}'


def test_jcs_hash_deterministic():
    a = jcs_hash({"a": 1, "b": [True, False, None]})
    b = jcs_hash({"b": [True, False, None], "a": 1})
    assert a == b
    assert len(a) == 32


def test_integer_numbers():
    out = canonical_json({"n": 12345}).decode("utf-8")
    assert out == '{"n":12345}'
