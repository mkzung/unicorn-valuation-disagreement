"""Round dates from the first appearance of a series letter, and what that date really is.

The event study has been blocked on round dates through three sources. Form D misses the large
rounds, which are placed under Section 4(a)(2). N-CSR gives an acquisition date, but it is the
fund's entry rather than the round. The press gives a date this repository will not cite.

The fourth source was already downloaded. Filers name the series in the security title —
"SER H PC PP", "Class B PP" — so the first report date on which a new letter appears anywhere in
the population bounds the round from above. It is a filing, not a claim, and it costs nothing:
32.1% of population rows carry a letter.

WHAT THE DATE IS, AND WHAT IT IS NOT
It is the first month in which a fund reported holding that series. It is not the closing date,
and the resolution is the reporting month rather than the day. Rounds that create no new class —
extensions, SAFEs, secondaries — are invisible to it, and a letter that appears because one fund
bought into an old series on the secondary market is not a round at all.

THE SIGN OF THE ERROR IS NOT GUARANTEED, AND THAT IS THE CORRECTION
The natural claim is that the N-PORT date must be at or after the round, so the error has a
known sign. Two of twenty-four calibration pairs say otherwise, and both for a structural
reason. SpaceX Series A first appears on 2019-09-30, the panel's own first date, against an
N-CSR entry of 2022-06-08: the series predates the panel, and what looks like a 982-day negative
error is left censoring. Anthropic Series G first appears in January 2026 against an earliest
N-CSR entry of March 2026: N-PORT covers every registered fund and N-CSR covers ten companies'
filers, so the N-CSR date is one filer's purchase and can be later than the series' arrival.

Neither date is the round close. They agree to within a month on the clean cases, and that is
what licenses the N-PORT date as a proxy at monthly resolution — not an argument about signs.

THE TWO RULES THE CALIBRATION DICTATES
Breadth, and censoring. Every calibration pair confirmed by two or more houses lands inside
`TOLERANCE_DAYS` except the two structural cases above; every pair outside it that is not
structural rests on a single house. A letter one fund reports is that fund's holding; a letter
several houses report in the same quarter is a round.

Run:  python3 src/round_dates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import ncsr_acquisitions as na
import population as pop

OUT = ROOT / "data" / "round_dates.csv"

MIN_HOUSES = 2          # counted with fund_complex.confirmations, never registrants
TOLERANCE_DAYS = 35     # read off the calibration below, not chosen: every broad, uncensored
                        # pair lands inside it and the nearest excluded one is at 49 days

# The ten §4.3 names as the population keys they resolve to. Databricks resolves under the code
# name several filers use for it, which is the resolver joining on an identifier and doing its
# job; the key it picks is the most common normalised string in the cluster.
NCSR_KEYS = {"Databricks": "NM:PROJECT DEBUSSY", "Anthropic": "NM:ANTHROPIC",
             "Stripe": "NM:STRIPE", "Canva": "NM:CANVA", "OpenAI": "NM:OPENAI",
             "SpaceX": "NM:SPACEX", "Discord": "NM:DISCORD", "Epic Games": "NM:EPIC GAMES",
             "Anduril": "NM:ANDURIL", "Revolut": "NM:REVOLUT"}


_MEMO: dict[str, pd.DataFrame] = {}


def first_seen(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """The first report date each company-series appears on, with its breadth.

    The default call is memoised on the panel's own cache key — the source file's mtime and
    size — because `round_event_study.selection_ladder` asks for it six times in a row and
    each miss re-reads and re-resolves 309,654 marks. Keying on the source rather than on
    nothing is what stops the memo outliving a change to the data.
    """
    if d is None:
        key = pop._cache_key()
        if key not in _MEMO:
            _MEMO.clear()
            _MEMO[key] = _first_seen(pop.comparable(pop.load_marks()))
        return _MEMO[key].copy()
    return _first_seen(d)


def _first_seen(d: pd.DataFrame) -> pd.DataFrame:
    d = d.dropna(subset=["dt"]).copy()
    d["series"] = pop.extract_series(d.ISSUER_TITLE)
    s = d[d.series.notna()]
    # `fund_complex.confirmations` is the rule; it is asserted against this aggregation in
    # `tests/test_round_dates.py` rather than called five thousand times inside a groupby.
    g = (s.groupby(["company", "series"])
           .agg(first_dt=("dt", "min"), funds=("fund", "nunique"),
                houses=("house", "nunique")).reset_index())
    # A series first seen on the panel's own first date is censored, not dated: it existed
    # before the window and the sensor has no information about when.
    g["censored"] = g.first_dt == d.dt.min()
    g["dated"] = (g.houses >= MIN_HOUSES) & ~g.censored
    # Stable sort. 42 companies have two or more series on their earliest date, and everything
    # downstream ranks these rows to decide which round is the first one, so an unstable order
    # would decide it differently between runs. `ncsr_acquisitions.fetch` sorts this way for
    # the same reason.
    return g.sort_values(["company", "first_dt"], kind="mergesort").reset_index(drop=True)


PRICE_TOLERANCE = 0.02   # "prices agree" for the coordination rule below


def coordination_dated(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """The alternative round-dating rule: the first month two houses agree on a price.

    A round creates a price, so a round month should be the first month in which two or more
    houses report the new series at prices within `PRICE_TOLERANCE` of each other. That rule
    is self-validating in a way a count is not, and §8.5 reports that it dates worse.

    It lived only in `notes/round_dates.md` until now, computed once by hand, which is how its
    half of Table 10 kept a p-value from before the tie tolerance while the count-rule half was
    corrected everywhere else. Both halves are computed here so the table is recomputed rather
    than remembered.
    """
    if d is None:
        d = pop.comparable(pop.load_marks())
    d = d.dropna(subset=["dt"]).copy()
    d["series"] = pop.extract_series(d.ISSUER_TITLE)
    s = d[d.series.notna()].copy()
    # One price per house per company-series-date: a house is one opinion (§4.1).
    h = (s.groupby(["company", "series", "dt", "house"]).pps.median().reset_index())
    rows = []
    for (co, ser), g in h.groupby(["company", "series"]):
        for dt, gd in g.groupby("dt"):
            p = gd.pps.sort_values().to_numpy()
            if len(p) < MIN_HOUSES:
                continue
            # any two houses within the tolerance of each other
            if ((p[1:] - p[:-1]) / p[:-1] <= PRICE_TOLERANCE).any():
                rows.append({"company": co, "series": ser, "first_dt": dt,
                             "houses": gd.house.nunique()})
                break
    out = pd.DataFrame(rows, columns=["company", "series", "first_dt", "houses"])
    if out.empty:
        return out
    out["censored"] = out.first_dt == d.dt.min()
    out["dated"] = ~out.censored
    return out.sort_values(["company", "first_dt"]).reset_index(drop=True)


def calibrate(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """The N-PORT date against the earliest N-CSR acquisition date for the same series.

    Two document types, one structured and already downloaded, the other parsed out of an HTML
    schedule. Where both name a series, the distance between them is the sensor's error — with
    the caveat in the module docstring that neither quantity is the round close.
    """
    n = na.load()
    n = n[n.series.notna()]
    ncsr = (n.groupby(["company", "series"]).acq.min().reset_index()
              .rename(columns={"acq": "ncsr_dt", "company": "ncsr_company"}))
    ncsr["company"] = ncsr.ncsr_company.map(NCSR_KEYS)
    m = first_seen(d).merge(ncsr, on=["company", "series"], how="inner")
    m["gap_days"] = (m.first_dt - m.ncsr_dt).dt.days
    m["inside_tolerance"] = m.gap_days.abs() <= TOLERANCE_DAYS
    return m.sort_values(["ncsr_company", "ncsr_dt"]).reset_index(drop=True)


_SHARE: dict[str, float] = {}


def letter_row_share_pct(d: pd.DataFrame | None = None) -> float:
    """Share of population rows whose security title names a series or class letter.

    Memoised on the panel key beside `first_seen`, because the manuscript guard was
    recomputing it from the raw marks file on every run and paying a second full resolve for
    one number.
    """
    if d is None:
        key = pop._cache_key()
        if key not in _SHARE:
            _SHARE.clear()
            d = pop.comparable(pop.load_marks()).dropna(subset=["dt"])
            _SHARE[key] = float(pop.extract_series(d.ISSUER_TITLE).notna().mean() * 100)
        return _SHARE[key]
    return float(pop.extract_series(d.ISSUER_TITLE).notna().mean() * 100)


def summary(d: pd.DataFrame | None = None) -> dict:
    f, c = first_seen(d), calibrate(d)
    ok = c[c.dated]
    return {"series_pairs": len(f), "companies": int(f.company.nunique()),
            "letter_row_share_pct": letter_row_share_pct(d),
            "dated_pairs": int(f.dated.sum()),
            "dated_companies": int(f[f.dated].company.nunique()),
            "calibration_pairs": len(c),
            "calibration_pairs_dated": len(ok),
            "inside_tolerance": int(ok.inside_tolerance.sum()),
            "median_gap_days": float(ok.gap_days.median()),
            "worst_inside": int(ok[ok.inside_tolerance].gap_days.abs().max()),
            "nearest_outside": int(ok[~ok.inside_tolerance].gap_days.abs().min())
            if (~ok.inside_tolerance).any() else -1}


def main() -> None:
    f = first_seen()
    f.to_csv(OUT, index=False)
    s = summary()
    c = calibrate()
    print(f"company-series pairs carrying a letter: {s['series_pairs']} on {s['companies']} "
          f"companies; {s['dated_pairs']} on {s['dated_companies']} clear the two-house bar "
          f"and are not censored.")
    print(f"\ncalibration against N-CSR: {s['calibration_pairs']} pairs, "
          f"{s['calibration_pairs_dated']} of them dated")
    print(c[["ncsr_company", "series", "ncsr_dt", "first_dt", "gap_days", "funds", "houses",
             "censored", "dated"]].to_string(index=False))
    print(f"\n{s['inside_tolerance']} of {s['calibration_pairs_dated']} dated pairs land inside "
          f"{TOLERANCE_DAYS} days; median gap {s['median_gap_days']:.0f}, worst inside "
          f"{s['worst_inside']}, nearest outside {s['nearest_outside']}.")
    print("  The two negatives are structural, not noise: SpaceX Series A is censored at the "
          "panel's first date, and Anthropic Series G appears in N-PORT before any of the ten "
          "companies' N-CSR filers records buying it. Neither date is the round close.")
    print(f"  wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
