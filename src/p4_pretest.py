"""P4 — does cross-house dispersion collapse as a company approaches its listing?

**This is an exploratory pre-test, not the registered test.** `notes/registration.md` fixes
P4 on listings completed after the registration is filed, pooled cumulatively. The 2020-21
cohort below sits inside data that was examined while §5 was written, so no result here can
be described as predating its data. It is run and reported because a hypothesis nobody has
ever computed is a hypothesis nobody can size, and because a null here neither falsifies P4
nor licenses dropping it from the registration.

Why this exists at all: an earlier draft recorded P4 as unanswerable on the current panel,
on the ground that only three of §7.1's ten exits have four qualifying report dates within
eighteen months of listing. That was a fact about those ten names, not about the data.
§7.1's ten are the exits with a verified *offer price*, which P4 does not need. P4 needs a
listing *date*, and `src/listing_dates.py` now reads one off EDGAR for every cluster whose
classification records a listing.

THE WINDOW ENDS BEFORE THE LISTING, AND THAT IS NOT A DETAIL
P4 is a claim about dispersion *into* an event, so a window that reaches past the event
tests something else. The first version of this module took each company's last four cells
and Palantir's last cell is 30 September 2020, nine days after it began trading — a mark on
a security that already had a public price, carried at Level 3 because reclassification
lags the event rather than because anybody was uncertain. One name in twelve, and it was
the name whose anchor was strongest, which is how it survived a reading. The window is now
the last four report dates strictly before the listing date, and `posted_after()` reports
how much of the panel sits on the wrong side of it.

MEMBERSHIP IS THE FILING'S, NOT MINE
The earlier cohort rule read my own classification notes for the phrase "cells end at the
... listing", which made the sample depend on how carefully I had worded a comment. It also
filtered on the year of the last *cell* rather than of the listing, which let in ServiceTitan
and Cava — names whose cells stop two years before they list. Membership is now: a listing
date validated against the panel exit in `listing_dates`, before 2023, with four qualifying
cells ahead of it. `legacy_cohort()` reproduces both earlier rules, because their results
were seen before the rule was tightened and deleting them would be worse than the inclusion
was.

A NULL IS WORTH ONLY AS MUCH AS ITS POWER, SO THE POWER IS PRINTED
`power()` resamples the observed changes to ask what collapse this design could actually
have detected. The answer is a large one. Reporting a null without that number invites the
reading that P4 is dead, when what the sample supports is much weaker.

Run:  python3 src/p4_pretest.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import company_class as ccl
import listing_dates as ld
import population as pop

OUT = ROOT / "data" / "p4_pretest.csv"

MIN_CELLS = 4              # P4's window: the four report dates preceding the listing
COHORT_END = "2023-01-01"  # later listings are reserved for the registered test
SEED = 20260806
LOCKUP_DAYS = 180          # the customary underwriter lock-up. Not a threshold anything is
                           # tested against — a yardstick, so that a Level-3 mark shortly
                           # after a listing is read as the accounting for an unsaleable
                           # share rather than as a fund being slow.


def _guarded():
    _, c = pop.panel()
    return c[c.guarded]


def _rho(v: np.ndarray) -> float:
    """Spearman of spread against date order, with a flat series read as no trend.

    Two names hold one number across the whole window, and `spearmanr` answers NaN for a
    constant series — correctly, since a rank correlation is undefined without variation.
    Dropping those names would drop the two clearest cases of dispersion not collapsing, so
    a flat series scores zero, the same way the endpoint test treats it as a tie.
    """
    if pop.same_number(v.max(), v.min()):
        return 0.0
    return float(spearmanr(np.arange(len(v)), v).statistic)


def validate() -> pd.DataFrame:
    """The listing dates this test runs on, each against its company's panel exit."""
    v = ld.validate()
    return v[v.validated & (v.listing_date < COHORT_END)].reset_index(drop=True)


def posted_after() -> dict:
    """How many cells in the old windows sat on the far side of the listing.

    Kept as a measurement rather than a comment because the answer decides whether the
    correction matters: one cell on one name, and it changes that name's reading.
    """
    g = _guarded()
    dts = ld.dates()
    late = {k: int((g[g.company == k].dt > d).sum()) for k, d in dts.items()}
    return {"names_with_post_listing_cells": sum(1 for v in late.values() if v),
            "post_listing_cells": sum(late.values()),
            "which": sorted(k for k, v in late.items() if v)}


def cohort() -> pd.DataFrame:
    """Pre-2023 listings with four guarded cells strictly before the listing date."""
    g = _guarded()
    v = validate()
    rows = []
    for _, r in v.iterrows():
        listing = pd.Timestamp(r.listing_date)
        s = g[(g.company == r.key) & (g.dt < listing)].sort_values("dt")
        if len(s) < MIN_CELLS:
            continue
        w = s.tail(MIN_CELLS)
        rows.append({
            "key": r.key, "company": r.company, "listing": r.listing_date,
            "anchor": r.form or r.mechanism, "cells_before": len(s),
            "window_from": w.dt.min().date().isoformat(),
            "window_to": w.dt.max().date().isoformat(),
            "days_to_listing": int((listing - w.dt.max()).days),
            "first_spread": float(w.spread_pct.iloc[0]),
            "last_spread": float(w.spread_pct.iloc[-1]),
            "change_pts": float(w.spread_pct.iloc[-1] - w.spread_pct.iloc[0]),
            "rho": _rho(w.spread_pct.to_numpy()),
        })
    return pd.DataFrame(rows).sort_values("change_pts").reset_index(drop=True)


def legacy_cohort(loose: bool = False) -> pd.DataFrame:
    """The two note-text rules this module used before the dates were fetched.

    Neither is a defensible sample — the strict one depends on the wording of my own
    comments and the loose one admits names that listed two years after their cells stop —
    but both produced a published number, so both stay runnable.
    """
    import re
    g = _guarded()
    ends_at = re.compile(r"cells end at the .* listing", re.I)
    loose_re = re.compile(r"listing|listed|pre-IPO|pre-merger", re.I)
    rows = []
    for key, (label, note) in ccl.VERIFIED.items():
        if label != ccl.VENTURE:
            continue
        member = bool(ends_at.search(note))
        if loose and not member:
            member = bool(loose_re.search(note))
        if not member:
            continue
        s = g[g.company == key].sort_values("dt")
        if len(s) < MIN_CELLS or s.dt.max().year > 2022:
            continue
        w = s.tail(MIN_CELLS)
        rows.append({"key": key, "change_pts": float(w.spread_pct.iloc[-1] - w.spread_pct.iloc[0]),
                     "rho": _rho(w.spread_pct.to_numpy())})
    return pd.DataFrame(rows)


def test(t: pd.DataFrame | None = None, col: str = "change_pts") -> dict:
    """P4 as the registration words it: one-sided signed-rank that the change is negative.

    Ties are dropped by `same_number`, not by float equality — several of these names end
    the window exactly where they started, and whether that counts is a tie rule rather
    than an observation.
    """
    if t is None:
        t = cohort()
    ch = t[col].to_numpy(float)
    ch = np.where(pop.same_number(ch, 0.0), 0.0, ch)
    nz = ch[ch != 0]
    return {
        "names": len(ch), "ties": int((ch == 0).sum()), "untied": len(nz),
        "declined": int((nz < 0).sum()), "widened": int((nz > 0).sum()),
        "median": float(np.median(ch)),
        "wilcoxon_p_less": float(wilcoxon(ch, alternative="less").pvalue) if len(nz) else float("nan"),
    }


def _reject(x: np.ndarray) -> bool:
    x = np.where(pop.same_number(x, 0.0), 0.0, x)
    return bool((x != 0).any() and wilcoxon(x, alternative="less").pvalue < 0.05)


def power(t: pd.DataFrame | None = None, effects=(0, 10, 20, 30, 40, 50),
          reps: int = 4000, model: str = "empirical") -> pd.DataFrame:
    """What size of collapse would this design have caught?

    Three models, because which one is used changes the answer by a factor of three and the
    disagreement is informative rather than a nuisance.

      normal       draws the change from N(-effect, s) with the observed s. It is the
                   textbook calculation and it is the pessimistic one here.
      empirical    resamples the observed changes, centred so that P4 is false, then shifts
                   them. This is the one to quote: the observed changes are nowhere near
                   normal — a third of the names sit within a point of zero and two names
                   carry most of the variance — and a signed-rank test reads the mass near
                   zero, not the spread of the tails, so the normal calculation understates
                   what the test can see by about a factor of three at ten points.
      proportional puts P4 in its own units. An additive collapse of ten points cannot
                   happen to a name whose spread is already zero, and three names here are
                   at or near zero, so the additive models describe an alternative the data
                   forbid. This one narrows each name's spread by a fraction of where it
                   started, which is what "dispersion collapses into liquidity" means, and
                   `effects` is read as that fraction in percent.
    """
    if t is None:
        t = cohort()
    ch = t.change_pts.to_numpy(float)
    base, n = ch - np.median(ch), len(ch)
    s = float(ch.std(ddof=1))
    first = t.first_spread.to_numpy(float)
    rng = np.random.default_rng(SEED)
    rows = []
    for eff in effects:
        hit = 0
        for _ in range(reps):
            if model == "normal":
                x = rng.normal(-eff, s, n)
            elif model == "proportional":
                x = rng.choice(base, n, replace=True) - first * (eff / 100)
            else:
                x = rng.choice(base, n, replace=True) - eff
            hit += _reject(x)
        rows.append({"effect": eff, "power": hit / reps})
    return pd.DataFrame(rows)


def mde(p: pd.DataFrame | None = None, target: float = 0.80) -> float:
    """The smallest collapse this design detects four times in five."""
    p = power() if p is None else p
    ok = p[p.power >= target]
    return float(ok.effect.iloc[0]) if len(ok) else float("nan")


def _post_listing_marks() -> pd.DataFrame:
    """Every panel mark dated after its own company's listing, one row per holding."""
    m = pop.comparable(pop.load_marks())
    dts = ld.dates()
    m = m[m.company.isin(dts)].copy()
    m["listing"] = m.company.map(dts)
    p = m[m.dt > m.listing].copy()
    p["days"] = (p.dt - p.listing).dt.days
    p["res"] = p.IS_RESTRICTED_SECURITY.astype(str).str.upper().eq("Y")
    return p


def reclassification_lag() -> pd.DataFrame:
    """How long a company that has listed is still carried as a Level-3 restricted holding.

    The panel is Level 3 by construction, so the promotion out of Level 3 is never seen and
    the lag is measured as persistence of the old classification: a mark still at Level 3 at a
    report date after the shares began trading. A lower bound on the interval either way.

    The window column is what keeps this from reading as "the funds are late". A lock-up makes
    shares unsaleable for the usual 180 days and ASC 820 prices that restriction, so a Level-3
    mark inside it is the accounting rather than a lag. `notes/post_listing_marks.md` carries
    the distribution and the three names in its tail.
    """
    p = _post_listing_marks()
    g = p.groupby("company").agg(
        listing=("listing", "first"), marks=("dt", "size"), holders=("fund", "nunique"),
        dates=("dt", "nunique"), first_days=("days", "min"), last_days=("days", "max"),
        restricted=("res", "sum"), value_usd=("val_usd", "sum")).reset_index()
    g["past_lockup"] = [int((p[(p.company == c) & (p.days > LOCKUP_DAYS)]).shape[0])
                        for c in g.company]
    return g.sort_values("last_days").reset_index(drop=True)


def lag_summary() -> dict:
    p, g = _post_listing_marks(), reclassification_lag()
    late = p[p.days > LOCKUP_DAYS]
    return {"post_listing_marks": int(g.marks.sum()), "post_listing_names": len(g),
            "marks_inside_lockup": int(g.marks.sum() - g.past_lockup.sum()),
            "marks_past_lockup": len(late), "names_past_lockup": int(late.company.nunique()),
            "longest_days": int(g.last_days.max()),
            "longest_name": g.loc[g.last_days.idxmax(), "company"],
            # The tail is not a policy finding; it is a handful of residual positions, and
            # the dollar figure is what says so. Quoting the day count without it would let
            # a $10,314 stub read as a fund carrying a listed company at Level 3.
            "largest_late_mark_usd": float(late.val_usd.max()),
            "late_share_restricted": float(late.res.mean())}


def summary() -> dict:
    t = cohort()
    r, tr = test(t), test(t, col="rho")
    p = power(t)
    return {
        "names": r["names"], "ties": r["ties"], "declined": r["declined"],
        "widened": r["widened"], "median_change_pts": r["median"],
        "p_endpoint": r["wilcoxon_p_less"], "p_trend": tr["wilcoxon_p_less"],
        "median_rho": tr["median"], "rho_declined": tr["declined"],
        "mde_pts": mde(p),
        "power_at_10": float(p.set_index("effect").power.loc[10]),
        "power_normal_at_10": float(power(t, effects=(10,), model="normal").power.iloc[0]),
        "power_total_collapse": float(power(t, effects=(100,), model="proportional").power.iloc[0]),
        "sd_change_pts": float(t.change_pts.std(ddof=1)),
        "verified_anchors": int(t.anchor.str.startswith("8-").sum()),
        "post_listing_cells": posted_after()["post_listing_cells"],
        "legacy_strict_p": float(test(legacy_cohort())["wilcoxon_p_less"]),
        "legacy_loose_p": float(test(legacy_cohort(loose=True))["wilcoxon_p_less"]),
        "legacy_strict_n": len(legacy_cohort()),
        "legacy_loose_n": len(legacy_cohort(loose=True)),
    }


def main() -> None:
    v = validate()
    print("listing dates, each validated against the company's own last private mark")
    print(v[["company", "listing_date", "form", "mechanism", "gap_days"]].to_string(index=False))

    pa = posted_after()
    print(f"\ncells sitting after their own listing: {pa['post_listing_cells']} on "
          f"{pa['names_with_post_listing_cells']} name(s) — {', '.join(pa['which'])}. "
          f"The window now stops before the listing, so they are out.")

    t = cohort()
    t.to_csv(OUT, index=False)
    print(f"\nexploratory cohort: {len(t)} names listing before {COHORT_END}")
    print(t[["company", "listing", "anchor", "window_from", "window_to", "days_to_listing",
             "first_spread", "last_spread", "change_pts"]].round(1).to_string(index=False))

    s = summary()
    print("\nP4 (exploratory, NOT the registered test): does dispersion decline into the listing?")
    print(f"  {s['names']} names · {s['ties']} unchanged · of the rest, {s['declined']} narrow "
          f"and {s['widened']} widen · median {s['median_change_pts']:+.1f} points")
    print(f"  endpoints:  one-sided signed-rank p={s['p_endpoint']:.3f}")
    print(f"  full trend: per-name Spearman over all four dates, {s['rho_declined']} of "
          f"{s['names']} negative, median rho {s['median_rho']:+.2f}, p={s['p_trend']:.3f}")
    print("  power, three models (rows: effect in points, or in % of the starting spread):")
    for m in ("normal", "empirical", "proportional"):
        eff = (0, 25, 50, 75, 100) if m == "proportional" else (0, 10, 20, 30, 40, 50)
        pw = power(t, effects=eff, model=m)
        print(f"    {m:13} " + "  ".join(f"{int(r.effect):>3}:{r.power:.2f}"
                                         for _, r in pw.iterrows()))
    print(f"  so: 80% power needs a collapse of {s['mde_pts']:.0f} points, and even a total "
          f"collapse — every name's spread to zero — is caught "
          f"{s['power_total_collapse'] * 100:.0f}% of the time")
    print(f"  the two note-text rules this replaced: strict {s['legacy_strict_n']} names "
          f"p={s['legacy_strict_p']:.3f}, loose {s['legacy_loose_n']} names "
          f"p={s['legacy_loose_p']:.3f} — same verdict, reported because they were seen first")
    verdict = "supported" if s["p_endpoint"] < 0.05 else "NOT supported"
    print(f"  -> {verdict} on this cohort, and underpowered against anything smaller than "
          f"{s['mde_pts']:.0f} points. A null here does not falsify P4; the registered test "
          f"runs on listings completed after the registration is filed.")
    print(f"  wrote {OUT.relative_to(ROOT)}")

    g, ls = reclassification_lag(), lag_summary()
    print("\nthe other side of that line: marks still Level 3 AFTER their company listed")
    print(g[["company", "listing", "marks", "holders", "first_days", "last_days",
             "restricted", "past_lockup"]].to_string(index=False))
    print(f"  {ls['post_listing_marks']} marks on {ls['post_listing_names']} names. "
          f"{ls['marks_inside_lockup']} land inside a {LOCKUP_DAYS}-day lock-up, where a "
          f"Level-3 mark is the accounting rather than a delay.")
    print(f"  {ls['marks_past_lockup']} run past it, on {ls['names_past_lockup']} names, the "
          f"longest {ls['longest_days']} days ({ls['longest_name']}). Largest of those marks "
          f"${ls['largest_late_mark_usd']:,.0f} — residual positions, not house policy.")
    print("  The promotion out of Level 3 is not observable: the panel is Level 3 by "
          "construction, so this is persistence of the old classification, not latency of "
          "the new one, and a lower bound either way.")


if __name__ == "__main__":
    main()
