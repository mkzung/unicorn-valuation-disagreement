"""The Form D extract, checked offline.

`src/form_d.py` reaches SEC, so nothing here re-fetches. What is asserted is the part that
failed silently the first time it was written: the boolean columns are spelled `true` and
`false`, and a filter that assumes `Y` and `N` matches nothing while looking exactly like an
empty data set. The coverage table said the SEC archive contains no original offerings at
all, which is what a broken filter reports.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import form_d as fd


@pytest.fixture(scope="module")
def offerings():
    return pd.read_csv(fd.OUT, dtype=str, low_memory=False)


def test_the_boolean_vocabulary_is_the_one_the_filings_use(offerings):
    got = set(offerings.ISAMENDMENT.dropna().str.lower()) | set(
        offerings.ISEQUITYTYPE.dropna().str.lower())
    assert got <= {"true", "false"}, f"unexpected boolean spelling: {sorted(got)}"
    assert fd.flag(pd.Series(["true", "false", "", None, "Y", "N"])).tolist() == \
        [True, False, False, False, True, False]


def test_the_amendment_filter_actually_removes_something(offerings):
    """A filter that matches nothing passes every downstream assertion for the wrong reason."""
    amended = fd.flag(offerings.ISAMENDMENT)
    assert amended.any() and not amended.all()


def test_the_coverage_table_is_a_share_of_something(offerings):
    cov = pd.read_csv(fd.STATS)
    orig = cov.loc[cov.fact.str.contains("live originals"), "n"].iloc[0]
    assert orig > 100_000, "the original-offering count collapsed; check the flag parser"
    rev = cov.loc[cov.fact.str.contains("usable bucket"), "share_of_live_originals"].iloc[0]
    assert rev < 50, "revenue fill rate has changed enough to reopen the covariate question"


def test_special_purpose_vehicles_are_recognised(offerings):
    """An SPV files under the company's name and dates its own raise, not the company's."""
    sample = pd.DataFrame({
        "ENTITYNAME": ["Anthropic Series D NMJFF Apr 2024 a Series of CGF2021 LLC",
                       "Stripe Inc Stock May 2024 a Series of CGF2021 LLC",
                       "Databricks, Inc.", "Neuralink Corp."],
        "INDUSTRYGROUPTYPE": ["Other", "Other", "Other Technology", "Other Technology"],
        "IS40ACT": [None, None, None, None]})
    assert fd.is_vehicle(sample).tolist() == [True, True, False, False]
    assert offerings.vehicle.astype(str).str.lower().eq("true").any()


def test_the_validation_still_fails_to_separate():
    """The verdict this module exists to produce, asserted so it cannot drift into a claim.

    Form D dates about half the panel and misses the rest by years. If a later harvest ever
    makes the distances separate the way the listing dates did, this test fails and the
    conclusion in notes/form_d_validation.md has to be rewritten rather than quietly kept.
    """
    v = fd.validate()
    g = v.gap_months.dropna().abs().sort_values().tolist()
    assert len(v) < 20, "coverage improved; re-read the validation note"
    assert max(g) > 24, "the far tail is gone; the sensor may now be usable"
    assert sum(x <= 3 for x in g) < len(g), "everything now lands inside a quarter"
