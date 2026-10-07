"""§4.3's ten anatomies, recomputed on every filing rather than the first eighteen per name.

The harvest behind Table 4 walked EDGAR company by company and stopped after eighteen
filings each, which was a sensible way to build an anatomy and a poor way to measure one.
`reconcile_versions` shows the cost as coverage: every published cell returns at least as
many funds from the bulk data, nine of ten return more, none returns fewer. This module
turns that into the quantity the paper actually reports — the spread — by recomputing the
same cells with nothing capped.

The date is held fixed at the published one, and that choice is the whole design. The
first attempt re-selected each company's date by the modal-report-date rule Table 4 already
uses, on the theory that applying the paper's own rule to a completer table needs no
defence. It does. Over seven years of filings that rule lands wherever a company happened
to be most widely held, which for Epic Games is a December-2024 cell where First Trust
files $1.00 against everyone else's $640-680, and for Anthropic a March-2026 cell where six
houses agree to the cent — and the median across the ten came out at 3.6% rather than
34.7%. Re-selecting dates moves the answer by more than lifting the cap does, because a
name's spread depends heavily on where it sits in a repricing: Anthropic is unanimous on 31
March and spans 49.8% on 30 April, when some houses had taken the new round and others had
not. So the comparison here changes one thing only. Same companies, same dates, same
family unit, same guard; the eighteen-filing cap lifted and nothing else.

  the family     the fund complex, as everywhere in §5, so one house filing thirty series
                 cannot widen a spread by itself.
  the guard      the same 4x ratio between extreme house marks. It removes exactly one of
                 the ten cells and the removal is reported rather than absorbed.

What the recomputation is NOT is a replacement for Table 4. Each mark in Table 4 was read
against its filing; these are read against a bulk extract of the same filings. The bound
belongs in the paper because a reader is owed the direction of the missing data. The
anatomy stays where the reading was done.

Run:  python3 src/fund_marks_bulk.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop
import reconcile_versions as rv

OUT = ROOT / "data" / "fund_marks_bulk.csv"


def table() -> pd.DataFrame:
    """One row per published §4.3 name, recomputed on the complete filing set."""
    joint, keymap = rv.joint_resolution()
    joint = joint.assign(ser=pop.series_letters(joint))
    pub = rv.compare().set_index("company")

    rows = []
    for name, key in keymap.items():
        if name not in pub.index:
            continue
        md = pd.to_datetime(pub.loc[name, "date"], format="%d-%b-%Y")
        cell = joint[(joint.company == key) & (joint["dt"] == md)]
        if cell.empty:
            continue
        hm = cell.groupby("house").pps.median()
        if len(hm) < 2:
            continue
        ratio = float(hm.max() / hm.min())
        letters = sorted(set().union(*cell.ser)) if len(cell) else []
        rows.append({
            "company": name,
            "date": md.date().isoformat(),
            "funds": int(cell.fund.nunique()),
            "houses": len(hm),
            "low": float(hm.min()), "high": float(hm.max()),
            "spread_pct": (ratio - 1) * 100,
            "guarded": ratio <= pop.CLASS_GUARD,
            "letters": "/".join(letters),
            "published_spread_pct": float(pub.loc[name, "paper_spread"]),
            "published_funds": int(pub.loc[name, "paper_funds"]),
        })
    return pd.DataFrame(rows).sort_values("spread_pct", ascending=False).reset_index(drop=True)


def letter_restricted(t: pd.DataFrame | None = None) -> pd.DataFrame:
    """The like-for-like cut: within one named series, where two houses name the same one.

    The standing objection to a wide cross-house spread is that the houses hold different
    rounds. Where filers name the round this can be tested directly rather than bounded in
    aggregate, and the answer is per cell rather than on average. The series chosen is the
    one covering the most funds, so the comparison is made on the best-populated slice
    rather than the most convenient.
    """
    if t is None:
        t = table()
    joint, keymap = rv.joint_resolution()
    joint = joint.assign(ser=pop.series_letters(joint))
    rows = []
    for _, r in t.iterrows():
        cell = joint[(joint.company == keymap[r.company])
                     & (joint["dt"] == pd.Timestamp(r["date"]))]
        named = cell[[len(v) > 0 for v in cell.ser]]
        sig = pd.Series(["/".join(sorted(v)) for v in named.ser], index=named.index)
        best = None
        for lab, grp in named.groupby(sig):
            if grp.house.nunique() < 2:
                continue
            hm = grp.groupby("house").pps.median()
            cand = {"company": r.company, "series": lab,
                    "spread_pct": float((hm.max() / hm.min() - 1) * 100),
                    "houses": int(grp.house.nunique()), "funds": int(grp.fund.nunique())}
            if best is None or cand["funds"] > best["funds"]:
                best = cand
        rows.append(best or {"company": r.company, "series": None, "spread_pct": np.nan,
                             "houses": 0, "funds": 0})
    return pd.DataFrame(rows)


def summary() -> dict:
    """The three medians a reader needs to place the published figure."""
    t = table()
    k = t[t.guarded]
    lr = letter_restricted(t).set_index("company")
    # Where a named series is shared, the like-for-like spread replaces the cell's; where no
    # filer names one, the cell's own figure stands, because there is nothing to restrict to.
    blend = [lr.loc[r.company, "spread_pct"] if not np.isnan(lr.loc[r.company, "spread_pct"])
             else r.spread_pct for _, r in k.iterrows()]
    unchanged = sum(1 for _, r in k.iterrows()
                    if not np.isnan(lr.loc[r.company, "spread_pct"])
                    and abs(lr.loc[r.company, "spread_pct"] - r.spread_pct) < 0.05)
    return {
        "cells": len(t), "guarded": len(k),
        "dropped": sorted(t.loc[~t.guarded, "company"]),
        "published_median": float(np.median(t.published_spread_pct)),
        "bulk_median": float(np.median(k.spread_pct)),
        "letter_median": float(np.median(blend)),
        "published_funds_median": float(np.median(t.published_funds)),
        "bulk_funds_median": float(np.median(k.funds)),
        "letters_shared": int((lr.houses >= 2).sum()),
        "letters_unchanged": unchanged,
    }


def main() -> None:
    t = table()
    t.to_csv(OUT, index=False)
    lr = letter_restricted(t).set_index("company")
    s = summary()
    print(f"{'company':13}{'date':12}{'funds':>6}{'houses':>7}{'spread':>9}{'published':>11}  "
          f"{'guard':6}{'same-series'}")
    for _, r in t.iterrows():
        ls = lr.loc[r.company]
        sub = "" if np.isnan(ls.spread_pct) else f"{ls.spread_pct:6.1f}% on '{ls.series}' ({ls.houses}h/{ls.funds}f)"
        print(f"  {r.company:13}{r['date']:12}{r.funds:6}{r.houses:7}{r.spread_pct:8.1f}%"
              f"{r.published_spread_pct:10.0f}%  {'keep' if r.guarded else 'DROP':6}{sub}")
    print(f"\nmedian spread: published {s['published_median']:.1f}% · complete filings "
          f"{s['bulk_median']:.1f}% · restricted to one named series {s['letter_median']:.1f}%")
    print(f"  guarded {s['guarded']} of {s['cells']} (dropped {', '.join(s['dropped']) or 'none'}) · "
          f"funds per cell {s['published_funds_median']:.0f} -> {s['bulk_funds_median']:.0f}")
    print(f"  a shared named series exists in {s['letters_shared']} cells and leaves the spread "
          f"unchanged in {s['letters_unchanged']}")
    print(f"  wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
