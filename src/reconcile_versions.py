"""Every published §4.3 cell, recomputed from the bulk data set.

The first version harvested EDGAR one company at a time and stopped after eighteen
filings. The bulk data set has no such cap, so each published cell should reappear with at
least as many funds and families. A cell that comes back *smaller* is a resolution failure
and has to be fixed before any population figure is quoted; a cell that comes back larger
is the cap, measured.

The spreads printed here are raw. The 4x unit and share-class guard that every reported
figure applies is deliberately switched off, so a cell whose wider coverage pulls in a
second share class shows its unguarded ratio — Discord and Stripe both do. That is the
point of the comparison: it shows what the bulk data contain before any filtering, not
what the analysis keeps.

Run:  python3 src/reconcile_versions.py
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import entity_resolution as er
import population as pop

# company -> (report date as filed in the bulk set, funds and families the paper reported,
#             the spread the paper reported)
CLASS_GUARD = pop.CLASS_GUARD

PUBLISHED = {
    "Discord":    ("31-MAR-2026", 8, 53),
    "Anthropic":  ("30-APR-2026", 14, 39),
    "Revolut":    ("30-APR-2026", 11, 35),
    "Epic Games": ("31-MAR-2026", 7, 33),
    "Gusto":      ("31-MAR-2026", 8, 32),
    "Databricks": ("30-APR-2026", 12, 15),
    "Canva":      ("31-MAR-2026", 5, 10),
    "Anduril":    ("31-MAR-2026", 7, 4),
    "Stripe":     ("31-MAR-2026", 8, 1),
    "OpenAI":     ("30-APR-2026", 13, 0),
}


@lru_cache(maxsize=1)
def joint_resolution() -> tuple[pd.DataFrame, dict[str, str]]:
    """Resolve the hand-labelled rows and the population together, once.

    Cached: resolving the union costs an entity-resolution pass over the whole panel, and the
    number registry the test suite runs calls this once per invocation.

    Two separate calls cannot be compared. A cluster's key is its union-find root, and
    which member becomes the root depends on the order rows are joined, so the same
    company gets one key in the small hand-labelled file and another in the population.
    Resolving
    the union is what puts both versions on one identity, and skipping it made four
    published companies look absent from data that plainly contained them.
    """
    hand = er.hand_labelled()[["company", "ISSUER_NAME", "ISSUER_CUSIP", "ISSUER_LEI"]]
    marks = pop.load_marks()
    cols = ["ISSUER_NAME", "ISSUER_CUSIP", "ISSUER_LEI"]
    both = pd.concat([hand[cols], marks[cols]], ignore_index=True)
    keys, _, wrapper = er.resolve(both)

    n = len(hand)
    hand = hand.assign(key=keys.iloc[:n].values)
    marks = marks.assign(company=keys.iloc[n:].values, is_wrapper=wrapper.iloc[n:].values)
    lookup = hand.groupby("company").key.agg(er.modal).to_dict()
    return marks, lookup


@lru_cache(maxsize=1)
def compare() -> pd.DataFrame:
    d, lab = joint_resolution()
    x = pop.comparable(d)

    rows = []
    for co, (date, paper_funds, paper_spread) in PUBLISHED.items():
        key = lab.get(co)
        s = x[(x.company == key) & (date == x.REPORT_DATE)] if key else x.iloc[0:0]
        if s.empty:
            rows.append(dict(company=co, date=date, bulk_funds=0, bulk_fams=0,
                             bulk_spread=float("nan"), paper_funds=paper_funds,
                             paper_spread=paper_spread, verdict="absent"))
            continue
        # Group by house, matching the panel these cells are being compared against. The
        # spreads are identical either way here, because the extreme marks sit in different
        # houses in every one of the ten cells, but the two sides must measure one object.
        fam = s.groupby("house").pps.median()
        spread = (fam.max() / fam.min() - 1) * 100 if len(fam) > 1 else 0.0
        funds = s.fund.nunique()
        verdict = ("wider coverage" if funds > paper_funds else
                   "matches" if funds == paper_funds else "NARROWER - investigate")
        rows.append(dict(company=co, date=date, bulk_funds=funds, bulk_fams=len(fam),
                         bulk_spread=spread, paper_funds=paper_funds,
                         paper_spread=paper_spread, verdict=verdict))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    t = compare()
    print(f"{'company':12s} {'date':12s} {'funds':>13s} {'houses':>9s} "
          f"{'spread':>16s}   verdict")
    for _, r in t.iterrows():
        print(f"{r.company:12s} {r.date:12s} "
              f"{int(r.bulk_funds):5d} vs {int(r.paper_funds):<4d} "
              f"{int(r.bulk_fams):9d} "
              f"{r.bulk_spread:8.1f}% vs {int(r.paper_spread):3d}%   {r.verdict}")
    narrower = t[t.verdict.str.startswith("NARROWER")]
    absent = t[t.verdict == "absent"]
    print(f"\n  wider {int((t.verdict == 'wider coverage').sum())} · "
          f"matches {int((t.verdict == 'matches').sum())} · "
          f"narrower {len(narrower)} · absent {len(absent)}")
    med_paper = t.paper_funds.median()
    med_bulk = t[t.bulk_funds > 0].bulk_funds.median()
    print(f"  median funds per cell: {med_paper:.1f} published -> {med_bulk:.1f} in the bulk set")
    out = ROOT / "data" / "version_reconciliation.csv"
    t.to_csv(out, index=False)
    print(f"  wrote {out.relative_to(ROOT)}")


def bound_from_the_complete_filing_set() -> dict:
    """How much the §4.3 harvest's eighteen-filing cap cost, in the units the paper quotes.

    `compare` establishes that every published cell returns at least as many funds from the
    bulk data. That is a statement about coverage. This one turns it into a statement about
    the number the abstract quotes: the median spread across the same ten cells, computed on
    the complete filing set rather than the capped harvest.

    The paper's own 4x share-class guard applies here as everywhere else. Discord's bulk cell
    puts BlackRock's mark ten times above Fidelity's and is excluded by it, so the bound is
    taken over the nine cells that survive rather than quietly over ten.
    """
    d = compare()
    kept = d[d.bulk_spread <= (CLASS_GUARD - 1) * 100]
    return {
        "published_median": float(np.median(d.paper_spread)),
        "bulk_median_guarded": float(np.median(kept.bulk_spread)),
        "cells": len(d), "cells_guarded": len(kept),
        "dropped": sorted(set(d.company) - set(kept.company)),
    }


def same_series_exemplar(company: str = "NM:STRIPE", date: str = "2026-03-31") -> dict:
    """The cleanest cell in the data: one company, one NAMED series, four houses, one date.

    Every deflationary reading of a wide spread is available somewhere in this panel — a
    share class, a unit convention, a stale mark. This cell has none of them. Four fund
    houses each name Stripe's Series I preferred in the security title, on the same report
    date, and the prices they file differ by seventy per cent. The arithmetic is checkable
    from the filing itself: value divided by balance returns the filed price per share to
    four decimals for every row, in units of shares.
    """
    d, _ = pop.panel()
    s = pop.comparable(d)
    s = s[(s.company == company) & (s.dt.astype(str).str.startswith(date))].copy()
    letters = pop.series_letters(s)
    named = s[[("I" in v) for v in letters]]
    h = named.groupby("house").pps.median().sort_values()
    # Compared with a tolerance, not by rounding both sides to two places: filers state the
    # price to a varying number of decimals, and rounding-vs-rounding is the float-equality
    # mistake this repository has now made three times. A tenth of a cent on prices in the
    # tens of dollars is a filing convention, not a disagreement.
    bal = pd.to_numeric(named.balance, errors="coerce")
    implied = named.val_usd / bal
    return {
        "houses": int(h.size), "funds": int(named.fund.nunique()),
        "low_house": h.index[0], "low_pps": float(h.iloc[0]),
        "high_house": h.index[-1], "high_pps": float(h.iloc[-1]),
        "spread_pct": float((h.iloc[-1] / h.iloc[0] - 1) * 100),
        "arithmetic_checks": int(np.isclose(implied, named.pps, rtol=0, atol=0.005).sum()),
        "rows": len(named),
    }


def exemplar_history(company: str = "NM:STRIPE", house: str = "Morgan Stanley") -> dict:
    """Is the outlying house carrying an old number, or its own?

    The obvious reading of one house seventy per cent below three others is that it has not
    repriced. The filings say otherwise, and the check is worth making before the claim: at
    every date this house reports, compare its mark with the median of the houses that report
    the same date, and ask whether its current number was ever anyone else's.
    """
    d, _ = pop.panel()
    x = pop.comparable(d)
    x = x[x.company == company]
    h = x.groupby([x.dt, "house"]).pps.median().unstack()
    if house not in h:
        return {}
    obs = h[h[house].notna()]
    others = obs.drop(columns=[house]).median(axis=1)
    gap = (others / obs[house] - 1) * 100
    mine = obs[house]
    consensus = h.drop(columns=[house]).median(axis=1).dropna()
    latest = float(mine.iloc[-1])
    # The run of consecutive dates ending at the last one on which this house sits below the
    # others. "Always below" was the first thing checked and it is false — the house tracked
    # the others through 2024 — so the reportable fact is the length of the current run, not
    # a claim about the whole history.
    run = 0
    for v in gap.values[::-1]:
        if v <= 0:
            break
        run += 1
    return {
        "observations": len(obs),
        "discount_run": run,
        "own_marks_rising": bool((mine.diff().dropna().tail(run) > 0).all()),
        "gap_first_pct": float(gap.iloc[0]), "gap_prev_pct": float(gap.iloc[-2]),
        "gap_last_pct": float(gap.iloc[-1]),
        "own_move_pct": float((mine.iloc[-1] / mine.iloc[-2] - 1) * 100),
        "others_move_pct": float((others.iloc[-1] / others.iloc[-2] - 1) * 100),
        # was the outlier's current mark ever the consensus at any earlier date?
        "ever_the_consensus": bool(np.isclose(consensus.values, latest, rtol=0, atol=0.01).any()),
    }
