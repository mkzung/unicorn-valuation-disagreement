"""
Appendix D Level-1 placebo — the cross-fund DISPERSION is a private-mark phenomenon, not a
reporting/units artifact.

If the §4.3 cross-fund spread were an artifact of how funds report (units, fiscal timing,
stale model updates), it would also appear for *public* holdings. It does not. On a common
report date, two funds from DIFFERENT families price five shared PUBLIC (Level-1) securities at
the identical market close (0.00% spread), while the same two houses disagree on PRIVATE
(Level-3) names filed the same day.

WHAT THIS FILE IS AND IS NOT AN EXHAUSTIVE LIST OF
It is five securities both funds hold, each verified to the cent against both filings. It is NOT
the whole intersection of two large portfolios, and the manuscript says so: the claim is that on
these five the two houses do not differ at all, not that they never differ on any public
holding. The Level-1 marks are harvested from the SAME SEC N-PORT filings as the
Level-3 marks (accessions recorded in data/level1_placebo.csv); this script recomputes the
cross-family spread offline so the falsification is reproducible.

Run: python3 src/level1_placebo.py
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    return pd.read_csv(ROOT / "data" / "level1_placebo.csv")


def cross_family_spread():
    """Per common public security, the cross-family spread = max/min price/share - 1.
    Returns (per-security table, median spread %)."""
    d = load()
    rows = []
    for (sec, cusip), g in d.groupby(["security", "cusip"]):
        lo, hi = g.price_per_share.min(), g.price_per_share.max()
        rows.append({"security": sec, "cusip": cusip, "n_families": g.family.nunique(),
                     "min": lo, "max": hi, "spread_pct": (hi / lo - 1) * 100})
    r = pd.DataFrame(rows)
    return r, float(r.spread_pct.median())


def main():
    r, med = cross_family_spread()
    print("Level-1 PLACEBO — cross-family pricing of common PUBLIC holdings, 2026-03-31")
    print("  funds: Fidelity Contrafund vs T. Rowe Price Blue Chip Growth (different families)")
    print("=" * 72)
    print(r.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\nLevel-1 cross-family spread: median {med:.2f}% across {len(r)} common public names.")
    print("Contrast: the same families' Level-3 PRIVATE marks disagree by a median 24% (up to 53%),")
    print("so the dispersion is a property of private-mark discretion, not fund reporting.")


if __name__ == "__main__":
    main()
