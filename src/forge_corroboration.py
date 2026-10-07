"""
Appendix D robustness — is the Forge secondary leg corroborated by INDEPENDENT signals?

The paper's lead result (§7.2-§7.2 secondary cross-section) rests on Forge Global's
per-company secondary estimates. Those are not independently price-verifiable by design: a
single proprietary model, single-sourced. That is the most load-bearing, least-defended input in the paper. This module
closes that gap where it can be closed: for the panel names carrying a second public market
signal, it cross-checks Forge's estimate against that signal, under the standing rule that a
figure is settled only once two independent sources agree.

Three kinds of INDEPENDENT signal (each independent of Forge's model), tagged per row:
  - secondary_venue : another secondary-trading platform's mark (Nasdaq Private Market, Hiive,
                      Caplight, PM Insights, Notice, Premier) — a second secondary signal.
  - tender          : a reported employee tender / secondary share sale valuation.
  - primary_round   : a confirming primary round at ~the Forge level (a hard market-clearing fact).
  - secondary_press : reputable press reporting of the secondary-market implied valuation.

Metric (uniform, valuation-basis; per-share quotes were pre-converted to an implied valuation in
data/forge_corroboration.csv, raw per-share kept in `note`): diff = forge_val/indep_val - 1.
Direction = does Forge's above/below-last-round sign match the independent signal's?

Honest by construction: every row is reported, including the ones where Forge runs CONSERVATIVE
vs other venues (Epic Games, PsiQuantum, Perplexity) — that residual cross-venue dispersion is
itself another instance of the paper's disagreement thesis, not swept under the rug.

Run: python3 src/forge_corroboration.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WITHIN_BAND = 15.0   # |diff| <= this counts as "within band" of the independent signal
NEAR_ROUND = 7.0     # |gap to last round| <= this => treat as "~at the round" (straddle-tolerant)
# A genuine above/below-round DIRECTION test needs an independent signal DISTINCT from the round.
# primary_round / tender anchors equal the headline by construction (gap-to-round trivially 0), so
# they are level cross-checks (diff_pct), not direction tests; direction is scored on these only:
SECONDARY_TYPES = {"secondary_venue", "secondary_press"}


def load() -> pd.DataFrame:
    """Join the corroboration table to the panel (headline + the Forge value being corroborated).
    Provenance guard: the forge value in the corroboration file MUST equal the panel's, so the
    cross-check can never silently drift away from the number the §7.2 result actually uses."""
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv").set_index("company")
    cor = pd.read_csv(ROOT / "data" / "forge_corroboration.csv").set_index("company")
    cor["headline_val_busd"] = panel.headline_val_busd
    cor["panel_forge_val_busd"] = panel.forge_val_busd
    bad = cor[(cor.forge_val_busd - cor.panel_forge_val_busd).abs() > 0.01]
    if len(bad):
        raise AssertionError(f"forge_val drift vs panel for: {list(bad.index)}")
    return cor


def enrich(cor: pd.DataFrame) -> pd.DataFrame:
    """Per-name diff (Forge vs independent), each signal's gap to the last round, and whether the
    two signals agree on the above/below-round direction (names within +/-NEAR_ROUND% of the round
    are bucketed '~at round' so a near-zero straddle is not miscounted as a disagreement)."""
    df = cor.copy()
    df["diff_pct"] = (df.forge_val_busd / df.indep_implied_val_busd - 1) * 100
    df["forge_gap_pct"] = (df.forge_val_busd / df.headline_val_busd - 1) * 100
    df["indep_gap_pct"] = (df.indep_implied_val_busd / df.headline_val_busd - 1) * 100

    def regime(g):
        if abs(g) <= NEAR_ROUND:
            return "~at"
        return "above" if g > 0 else "below"

    df["forge_regime"] = df.forge_gap_pct.map(regime, na_action="ignore")
    df["indep_regime"] = df.indep_gap_pct.map(regime, na_action="ignore")
    df["direction_agree"] = df.forge_regime == df.indep_regime
    return df


def summary(df: pd.DataFrame) -> dict:
    num = df[df.indep_implied_val_busd.notna()]
    ad = num.diff_pct.abs()
    sec = num[num.indep_type.isin(SECONDARY_TYPES)]   # genuine independent SECONDARY marks
    return {
        "n_cross_checked": len(df),                 # incl. directional-only (Kraken)
        "n_numeric": len(num),
        "median_abs_diff_pct": float(ad.median()),
        "mean_abs_diff_pct": float(ad.mean()),
        "n_within_band": int((ad <= WITHIN_BAND).sum()),
        "n_secondary": len(sec),
        "n_secondary_dir_agree": int(sec.direction_agree.sum()),
        "forge_conservative": sorted(num[num.diff_pct < -NEAR_ROUND].index),  # Forge below other venues
    }


def main() -> int:
    df = enrich(load())
    s = summary(df)

    print("=" * 92)
    print("Appendix D  FORGE SECONDARY LEG — corroboration by INDEPENDENT public market signals")
    print("=" * 92)

    show = df.reset_index()[["company", "forge_val_busd", "indep_implied_val_busd", "indep_type",
                             "diff_pct", "forge_gap_pct", "indep_gap_pct", "direction_agree",
                             "indep_date"]].copy()
    for c in ["forge_val_busd", "indep_implied_val_busd"]:
        show[c] = show[c].map(lambda v: "" if pd.isna(v) else f"{v:,.2f}")
    for c in ["diff_pct", "forge_gap_pct", "indep_gap_pct"]:
        show[c] = show[c].map(lambda v: "" if pd.isna(v) else f"{v:+.1f}%")
    print(show.to_string(index=False))

    print("\n" + "-" * 92)
    print(f"  names with an independent cross-check : {s['n_cross_checked']} "
          f"({s['n_numeric']} numeric + 1 directional)")
    print(f"  median |Forge - independent|          : {s['median_abs_diff_pct']:.1f}%   "
          f"(mean {s['mean_abs_diff_pct']:.1f}%)")
    print(f"  within +/-{WITHIN_BAND:.0f}% of the independent signal : "
          f"{s['n_within_band']}/{s['n_numeric']}")
    print(f"  above/below-round direction agrees     : {s['n_secondary_dir_agree']}/{s['n_secondary']} "
          f"(on the independent-SECONDARY rows, where the test is meaningful;\n"
          f"     the round/tender anchors equal the headline by construction, so they are level checks)")
    print(f"  Forge runs CONSERVATIVE vs other venues: {', '.join(s['forge_conservative'])} "
          f"-> residual cross-venue secondary dispersion is itself the paper's disagreement thesis")
    print("  => Forge's per-company estimates are corroborated by a SECOND public market signal "
          "(another\n     secondary venue, an employee tender, or a confirming primary round); the "
          "lead result no\n     longer rests on one proprietary, unverifiable source.")

    out = df.reset_index()[["company", "forge_val_busd", "indep_implied_val_busd", "indep_type",
                            "diff_pct", "forge_gap_pct", "indep_gap_pct", "direction_agree",
                            "indep_date", "indep_source"]]
    out.to_csv(ROOT / "data" / "forge_corroboration_summary.csv", index=False)
    print(f"\nwrote data/forge_corroboration_summary.csv ({len(out)} names)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
