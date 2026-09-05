"""Appendix D's two family-level facts, and the counting error they exist to avoid.

The per-series harvest adds two claims to the exit adjudication: that no house is a
systematically better forecaster, and that a nominally broad pre-IPO holder base collapses to
a handful of independent views. Both are counting claims, and both are counted over the unit
this paper spent its headline correcting — the house, not the trust. Nothing tested either.

`family_accuracy` was at 54% with `family_table` and the sleeve counter unexercised, which is
how the second of those claims could have gone on saying "four insurers" while the map read
five trusts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import family_accuracy as fa


@pytest.fixture(scope="module")
def df():
    return fa.load()


def test_written_off_placeholders_are_dropped_rather_than_scored(df):
    """A $0.00 mark is a fund writing a position off, not a forecast of zero. Scored, it
    returns an error of -100% and drags whichever family filed it to the bottom of a table
    that is supposed to be about accuracy."""
    import pandas as pd
    raw = pd.read_csv(ROOT / "data" / "ipo_premarks_byfund.csv")
    assert (raw.mark_pps <= 0).any(), "no placeholder left; this filter is now untested"
    assert (df.mark_pps > 0).all()
    assert len(df) < len(raw)


def test_the_sleeve_platforms_collapse_to_fewer_insurers_than_trusts(df):
    """§4.3's mirror structure at the exit, and the reason the count is of insurer GROUPS.

    MassMutual files these through two trusts, MassMutual Select and MML Series. Counting
    trusts would report five independent carriers of one sub-advisor's $32.50 where there are
    four, which is the count-funds-not-houses error one layer down from the paper's own.
    """
    trusts, funds, insurers = fa.instacart_sleeve_counts(df)
    assert trusts >= insurers, "more insurer groups than trusts is not possible"
    assert insurers < trusts, "no multi-trust insurer left; the collapse is untested"
    assert insurers == 4 and funds == 22, (trusts, funds, insurers)
    assert set(fa.INSURER_OF.values()) >= {"MassMutual"}
    assert fa.INSURER_OF["MASSMUTUAL"] == fa.INSURER_OF["MML"], (
        "the two MassMutual trusts no longer map to one insurer")


def test_no_family_scores_enough_exits_to_be_ranked(df):
    """The appendix says each family scores one to four exits, too few to rank, and that is
    the claim doing the work: a table sorted by median error invites exactly the reading it
    refuses. If some family ever reaches enough exits, the sentence has to change."""
    t = fa.family_table(df)
    assert not t.empty
    assert t.exits.max() <= 4, f"a family now scores {t.exits.max()} exits; re-read Appendix D"
    assert t.median_abs_err_pct.is_monotonic_increasing, "the table is not sorted by accuracy"
    assert t.sleeve.any() and (~t.sleeve).any(), "the sleeve flag no longer separates anything"


def test_fidelity_undershoots_every_clean_exit_it_marks(df):
    """The one directional regularity the appendix does claim, asserted with its direction.

    Conservatism is a signed statement — every one of Fidelity's clean fund-mark exits came in
    BELOW the listing. An absolute-error check would pass on a house that overshot all three.
    """
    fid = df[df.family == "Fidelity"]
    assert fid.company.nunique() >= 3, "Fidelity no longer marks three exits here"
    per_exit = fid.groupby("company").err_pct.median()
    assert (per_exit < 0).all(), f"Fidelity did not undershoot everywhere: {dict(per_exit)}"
