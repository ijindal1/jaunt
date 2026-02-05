from __future__ import annotations

import types

import pytest

from jaunt.spec_ref import normalize_spec_ref, spec_ref_from_object

_SPEC_REF_ATTR = "__jaunt_spec_ref__"


def test_normalize_colon_format_passthrough() -> None:
    assert normalize_spec_ref("pkg.mod:Thing") == "pkg.mod:Thing"


def test_normalize_dot_shorthand_conversion() -> None:
    assert normalize_spec_ref("pkg.mod.Thing") == "pkg.mod:Thing"


def test_normalize_nested_qualname_stability_for_colon_form() -> None:
    assert normalize_spec_ref("pkg.mod:Outer.Inner") == "pkg.mod:Outer.Inner"


def test_normalize_rejects_obviously_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        normalize_spec_ref("")
    with pytest.raises(ValueError):
        normalize_spec_ref("no_separator")
    with pytest.raises(ValueError):
        normalize_spec_ref(":Qual")
    with pytest.raises(ValueError):
        normalize_spec_ref("pkg.mod:")
    with pytest.raises(ValueError):
        normalize_spec_ref("pkg..mod:Qual")


def test_spec_ref_from_object_function_and_class() -> None:
    def f() -> None:
        return None

    class C:
        pass

    f_ref = spec_ref_from_object(f)
    c_ref = spec_ref_from_object(C)

    f_mod, f_qual = f_ref.split(":", 1)
    c_mod, c_qual = c_ref.split(":", 1)

    # Nested objects include the defining function and "<locals>" in __qualname__.
    assert f_mod == __name__
    assert c_mod == __name__
    assert f_qual.split(".")[-1] == "f"
    assert c_qual.split(".")[-1] == "C"


def test_spec_ref_from_object_override_is_honored() -> None:
    def f() -> None:
        return None

    # types.FunctionType allows attribute assignment.
    assert isinstance(f, types.FunctionType)
    setattr(f, _SPEC_REF_ATTR, "pkg.mod.Thing")
    assert spec_ref_from_object(f) == "pkg.mod:Thing"
