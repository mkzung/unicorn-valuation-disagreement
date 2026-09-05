"""The listing-date table, checked offline against the committed CSV.

`src/listing_dates.py` reaches SEC, so nothing here re-fetches. What is asserted is the
part that can go wrong without the network: that every date in the table still lands where
the panel says the company stopped being private, and that the two traps the module exists
to encode are still encoded in the data it wrote.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import listing_dates as ld


@pytest.fixture(scope="module")
def table():
    return ld.load()


def test_every_candidate_is_in_the_committed_table(table):
    assert set(table.key) == set(ld.CANDIDATES), "the CSV and the candidate list disagree"


def test_the_dated_names_agree_with_the_panel_exit():
    v = ld.validate()
    ok = v[v.validated]
    assert len(ok) == 18, f"{len(ok)} names validate, not 18"
    assert ok.gap_days.abs().max() <= ld.ANCHOR_TOLERANCE
    # The threshold is claimed to separate rather than cut. That claim is the reason a
    # reader should accept a hand-set tolerance, so it is asserted rather than described.
    rejected = v[~v.validated & v.gap_days.notna()]
    assert rejected.gap_days.abs().min() > 2 * ok.gap_days.abs().max()


def test_palantir_takes_the_earliest_registration_not_the_latest(table):
    """Palantir filed 8-A12B twice: the 2020 direct listing and the 2024 Nasdaq move."""
    r = table[table.key == "NM:PALANTIR"].iloc[0]
    assert r.listing_date == "2020-09-21", "the exchange move has displaced the listing"
    assert r.accession == "0001193125-20-250175"


def test_a_de_spac_does_not_inherit_the_shells_registration(table):
    """DraftKings' earliest 8-A12B is Diamond Eagle's, filed a year before the merger."""
    r = table[table.key == "NM:DRAFTKINGS"].iloc[0]
    assert r.era_name == "DraftKings Inc."
    assert r.form == "8-K12B" and r.listing_date.startswith("2020-04")
    assert pd.Timestamp(r.listing_date) > pd.Timestamp(r.era_from)


def test_the_table_records_what_it_could_not_date(table):
    """A table holding only its successes hides its coverage."""
    blank = table[table.listing_date == ""]
    assert set(blank.key) == {"NM:ROOFOODS", "NM:ANT"}
    assert (blank.mechanism == "no SEC registration").all()
