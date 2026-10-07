"""The round-date sensor, and the two rules the calibration dictated rather than suggested.

Offline against the committed panel. What it asserts is the shape of the calibration — the gap
the tolerance is read from — and the two structural cases that break the natural sign claim.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import round_dates as rd


@pytest.fixture(scope="module")
def cal():
    return rd.calibrate()


def test_the_tolerance_is_read_off_a_gap_and_not_chosen(cal):
    """The same discipline as the listing dates: a threshold is only honest if the distribution
    has a gap to put it in. Here the worst pair inside is 33 days and the nearest outside 59."""
    ok = cal[cal.dated]
    inside = ok[ok.inside_tolerance].gap_days.abs().max()
    outside = ok[~ok.inside_tolerance].gap_days.abs().min()
    assert inside < rd.TOLERANCE_DAYS < outside, "the gap the tolerance sits in has closed"
    assert ok.inside_tolerance.mean() > 0.9


def test_one_house_is_not_a_round(cal):
    """Every calibration pair that misses by months rests on a single house.

    Discord Series G at +670 days, OpenAI A-2 at +426, SpaceX B at +570 — one fund each. A
    letter one fund reports is that fund's holding; a letter several houses report is a round.
    """
    bad = cal[cal.gap_days.abs() > 100]
    assert not bad.empty
    assert (bad[~bad.censored].houses < rd.MIN_HOUSES).all(), \
        "a broad pair now misses by months; re-read the note"


def test_the_sign_of_the_error_is_not_guaranteed(cal):
    """The correction to the natural claim, asserted so it cannot quietly become an assumption.

    SpaceX Series A is censored at the panel's first date. Anthropic Series G appears in N-PORT
    two months before any of the ten companies' N-CSR filers records buying it, because N-PORT
    covers every registered fund and the N-CSR harvest covers ten companies. Neither date is the
    round close, so "N-PORT is always later" is not available as a premise.
    """
    assert (cal.gap_days < 0).any(), "the negatives are gone; the sign claim may now hold"
    assert cal[cal.censored].gap_days.min() < -500
    anth = cal[(cal.ncsr_company == "Anthropic") & (cal.series == "G")]
    assert len(anth) == 1 and anth.iloc[0].gap_days < 0 and anth.iloc[0].dated


def test_the_sensor_reaches_past_the_ten_ncsr_names():
    """The point of calibrating: the rule applies where no N-CSR schedule was ever read."""
    s = rd.summary()
    assert s["dated_companies"] > 100, "coverage has collapsed to the calibration set"
    assert s["dated_pairs"] > s["calibration_pairs"] * 10


def test_confirmations_is_the_shared_rule_and_refuses_a_bad_unit():
    """Three metrics in a row counted registrants by default. This is the one place that decides."""
    import pandas as pd
    import fund_complex as fx
    d = pd.DataFrame({"house": ["Fidelity", "Fidelity", "ARK"],
                      "CIK": ["1", "2", "3"], "fund": ["a", "b", "c"]})
    assert fx.confirmations(d) == 2
    assert fx.confirmations(d, "CIK") == 3
    with pytest.raises(ValueError):
        fx.confirmations(d, "registrant")
