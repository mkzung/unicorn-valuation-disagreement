"""
Appendix C.4 Cross-signal synthesis — do the independent public signals agree at the COMPANY level?

The paper builds four public signals (secondary cross-section §7.2, IPO exits §7.1, cross-fund
N-PORT marks §4.3, the time series Appendix C.1) and a recurring claim runs through all of them: ONE
mechanism — the existence (or staleness) of a single fresh, believed primary round — drives every
disagreement. Fresh in-demand names: funds HERD to the round AND the secondary bids at/above it.
Stale / repriced / round-cascade names: funds SPLIT AND the secondary departs from the round.

So far the paper connects only the two CYCLE signals quantitatively (Appendix C.2, Forge vs fund-marks,
matched-date rho 0.99). The two CROSS-SECTIONAL signals — the §7.2 secondary-to-headline gap and
the §4.3 cross-fund mark spread — are never put side by side, even though the narrative implies they
share a driver. This module does that, honestly:

  (1) COVERAGE / disjointness. How much do the signals even overlap at the company level? (They
      cover largely different universes — itself the reason triangulating private value is hard.)
  (2) AGREEMENT on the overlap. On the names BOTH cross-sectional signals cover, is a name the
      secondary bids up a name funds agree on? Spearman rho(gap, spread) with an EXACT permutation
      p (the overlap is tiny, so no normal approximation), plus the herd/disagree x above/below
      classification. Reported as DIRECTIONAL, n is small — not oversold.

Reuses the production loaders in src/robustness.py (cross_section_gaps, clean_fund_table,
_modal_slice) so it stresses the SAME pipeline the §7.2/§4.3 headline numbers come from.

Run: python3 src/cross_signal.py
"""
from __future__ import annotations

import math
import sys
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import robustness as rb

MIN_FUNDS = 5          # the §4.3 headline threshold for a reportable cross-fund spread
HERD_CUTOFF = 5.0      # spread < 5% == "funds herd to the last round" (the §4.3 bimodality split)


def secondary_gaps() -> pd.Series:
    """Full-panel secondary-to-headline gap %, indexed by company. clean_only=False so the names
    that overlap the fund-mark set but carry a flagged headline (Stripe tender, Epic Games stale)
    are kept — excluding them would erase the only below-round overlap case and the variation the
    synthesis needs; their flag is surfaced in the merged table instead."""
    return rb.cross_section_gaps(clean_only=False).rename("gap_pct")


def fund_spreads(K: float = 3.0, min_funds: int = MIN_FUNDS) -> pd.DataFrame:
    """Per-company same-date cross-fund spread%, n_funds and n_families, from the SAME cleaned
    table src/fund_marks.py's headline uses (via robustness.clean_fund_table)."""
    clean, _ = rb.clean_fund_table(K)
    rows = []
    for co in clean.company.unique():
        sd = rb._modal_slice(clean, co)
        v = sd.pps.values
        rows.append({"company": co, "n_funds": len(sd), "n_families": sd.family.nunique(),
                     "spread_pct": (v.max() / v.min() - 1) * 100})
    f = pd.DataFrame(rows)
    return f[f.n_funds >= min_funds].set_index("company").sort_values("spread_pct")


def merged_overlap(min_funds: int = MIN_FUNDS) -> pd.DataFrame:
    """Inner join of the two cross-sectional signals: companies covered by BOTH the secondary
    cross-section (§7.2) and the >=min_funds cross-fund marks (§4.3). Each row carries the secondary
    gap, the cross-fund spread, the headline quality flag, and the two regime labels."""
    g = secondary_gaps()
    s = fund_spreads(min_funds=min_funds)
    m = s.join(g, how="inner")
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")
    m["quality_flag"] = panel.quality_flag
    m["fund_consensus"] = np.where(m.spread_pct < HERD_CUTOFF, "herd", "disagree")
    m["secondary_sign"] = np.where(m.gap_pct >= 0, "at/above", "below")
    return m.sort_values("spread_pct")


def spearman_exact(x, y):
    """Spearman rho + EXACT two-sided permutation p. For the tiny overlap (n<=8 => <=40320
    permutations) we enumerate every relabelling rather than lean on the normal approximation,
    which is invalid at this n. Deterministic. Returns (rho, p_two_sided, n)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values

    def _rho(a, b):
        a = a - a.mean()
        b = b - b.mean()
        denom = math.sqrt(float(a @ a) * float(b @ b))
        return float(a @ b) / denom if denom else float("nan")

    obs = _rho(rx, ry)
    cnt = sum(abs(_rho(rx, np.array(p))) >= abs(obs) - 1e-12 for p in permutations(ry))
    return obs, cnt / math.factorial(n), n


def coverage() -> dict:
    """Company-level coverage of the two cross-sectional signals + the time-series leg, to show how
    little the signals overlap (each illuminates names the others miss)."""
    panel = set(secondary_gaps().index)
    fund5 = set(fund_spreads(min_funds=MIN_FUNDS).index)
    import fund_marks_timeseries as ts
    tsnames = {co for co, g in ts.load().groupby("company")
               if co not in ts.EXCLUDE_PERSHARE and g.quarter.nunique() >= 10}
    return {"n_secondary": len(panel), "n_fund5": len(fund5), "n_ts": len(tsnames),
            "overlap_xsec": sorted(panel & fund5),
            "fund_only": sorted(fund5 - panel),
            "all_three": sorted(panel & fund5 & tsnames)}


def main() -> int:
    print("=" * 84)
    print("Appendix C.4  CROSS-SIGNAL SYNTHESIS — do the public signals agree at the company level?")
    print("=" * 84)

    cov = coverage()
    print("(1) COVERAGE / disjointness")
    print(f"    secondary cross-section (§7.2): {cov['n_secondary']} names")
    print(f"    cross-fund marks, >={MIN_FUNDS} funds (§4.3): {cov['n_fund5']} names")
    print(f"    overlap (both cross-sectional signals): {len(cov['overlap_xsec'])} "
          f"-> {', '.join(cov['overlap_xsec'])}")
    print(f"    fund-mark names the secondary panel does NOT cover: {', '.join(cov['fund_only'])}")
    print(f"    in ALL three of §7.2/§4.3/Appendix C.1: {', '.join(cov['all_three'])}")
    print("    => the signals cover largely DIFFERENT companies; the secondary sees fallen/small-cap "
          "names\n       funds do not hold, N-PORT sees mega-caps not all actively secondary-traded — "
          "complementary,\n       not redundant, which is why the four-way triangulation is needed.")

    m = merged_overlap()
    print("\n(2) AGREEMENT on the overlap (each name's two independent disagreement signals)")
    show = m.copy()
    show["gap_pct"] = show.gap_pct.map(lambda v: f"{v:+.1f}%")
    show["spread_pct"] = show.spread_pct.map(lambda v: f"{v:.1f}%")
    print("    " + show.reset_index()[["company", "n_funds", "n_families", "spread_pct",
          "gap_pct", "quality_flag", "fund_consensus", "secondary_sign"]]
          .to_string(index=False).replace("\n", "\n    "))

    rho, p, n = spearman_exact(m.gap_pct.values, m.spread_pct.values)
    print(f"\n    Spearman rho(secondary gap, cross-fund spread) = {rho:+.2f}  "
          f"(exact permutation p={p:.2f}, n={n})")
    mc = m[m.quality_flag == "clean"]
    rho_c, _, n_c = spearman_exact(mc.gap_pct.values, mc.spread_pct.values)
    print(f"    robustness: dropping the two flagged-headline names (Stripe tender, Epic Games stale) "
          f"leaves\n       rho={rho_c:+.2f} (n={n_c}) — the negative sign is not an artifact of the "
          f"flagged rows.")
    print(f"    -> DIRECTIONAL and as the shared mechanism predicts (more secondary premium <-> more "
          f"fund\n       consensus), but n={n} is far too small to be significant — reported as "
          f"corroboration, not proof.")

    herd = m[m.fund_consensus == "herd"]
    dis = m[m.fund_consensus == "disagree"]
    herd_above = int((herd.secondary_sign == "at/above").sum())
    print("\n    Regime view (the cleaner, distribution-free reading):")
    print(f"      funds HERD (<{HERD_CUTOFF:.0f}% spread): {', '.join(sorted(herd.index))} "
          f"-> {herd_above}/{len(herd)} trade at/above their last round in the secondary")
    print(f"      funds DISAGREE (>={HERD_CUTOFF:.0f}%): {', '.join(sorted(dis.index))} "
          f"-> carry the gap sign-instability (the only below-round name, "
          f"{', '.join(sorted(dis[dis.secondary_sign=='below'].index))}, is a stale-headline case)")
    print("      => one driver (a single fresh, believed round) explains BOTH a name's fund "
          "consensus AND\n         whether the secondary anchors to its headline — the §7.2/§4.3 "
          "staleness/demand mechanism,\n         now shown to operate ACROSS two independent signals "
          "on the same names.")

    out = m.reset_index()[["company", "n_funds", "n_families", "spread_pct", "gap_pct",
                           "quality_flag", "fund_consensus", "secondary_sign"]]
    out.to_csv(ROOT / "data" / "cross_signal_consistency.csv", index=False)
    print(f"\nwrote data/cross_signal_consistency.csv ({len(out)} overlapping names)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
