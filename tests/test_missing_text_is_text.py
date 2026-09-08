"""A missing title must reach the regexes as text on every pandas the floor allows.

`astype(str)` wrote a missing value as the string "nan" up to pandas 2 and leaves it
missing from pandas 3. The nightly `verify (floor)` job installed pandas 3.0.5 against
`verify (lock)`'s 2.2.3 and died in `series_letters` with

    TypeError: expected string or bytes-like object, got 'float'

which is the loud half. The quiet half is `company_class.up`, which drops a title by
testing it against the literal {"", "NAN", "NONE"}, and the fallback that replaces a
short issuer name by testing `str.lower() != "nan"`: on pandas 3 both compare against a
missing value and pass everything through.

These assert on the rendering rather than on a version, so they hold either way.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

MISSING = pd.Series(["SERIES A SHARES", np.nan, "CLASS B", pd.NA], dtype=object)


def test_as_text_returns_a_string_for_every_row():
    out = pop.as_text(MISSING)
    assert len(out) == len(MISSING)
    assert all(isinstance(v, str) for v in out), [type(v).__name__ for v in out]


def test_as_text_renders_a_missing_value_the_way_the_guards_expect():
    """The two guards in `company_class` test for this literal, so it is the contract."""
    out = pop.as_text(MISSING).str.upper()
    assert out.iloc[1] == "NAN"
    assert out.iloc[3] == "NAN"
    assert out.iloc[0] == "SERIES A SHARES"


def test_as_text_leaves_a_column_with_nothing_missing_alone():
    """Which is why the fix cannot move a reported number: it only fills what was NA."""
    full = pd.Series(["a", "b", "c"], dtype=object)
    assert list(pop.as_text(full)) == list(full.astype(str))


def test_the_two_flavours_of_missing_render_the_same():
    """`astype(str)` writes NaN as "nan" and pd.NA as "<NA>", and one guard reads both."""
    out = pop.as_text(MISSING).str.upper()
    assert out.iloc[1] == out.iloc[3] == "NAN"


@pytest.mark.parametrize("call", [
    lambda s: pop.extract_series(s),
    lambda s: pop.series_letters(pd.DataFrame({"ISSUER_TITLE": s, "ISSUER_NAME": s})),
])
def test_the_regex_callers_do_not_raise_on_a_missing_title(call):
    out = call(MISSING)
    assert len(out) == len(MISSING)


def test_a_missing_title_names_no_series():
    """"NAN" carries no series letter, so filling with it adds nothing to the panel."""
    assert pop.extract_series(MISSING).iloc[1] is None
    letters = pop.series_letters(
        pd.DataFrame({"ISSUER_TITLE": MISSING, "ISSUER_NAME": MISSING}))
    assert letters.iloc[1] == frozenset()
    assert letters.iloc[0] == frozenset({"A"})
