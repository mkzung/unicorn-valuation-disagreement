"""Offline analyzer for `data/ipo_premarks_byfund.csv` (harvested by src/family_forecast.py):
which fund FAMILY's last pre-IPO N-PORT mark was closest to the realized IPO price?

STATUS (2026-07-02, second pass): the harvest is COMPLETE — all 7 fund-held exits, 18
family-company rows, after `family_forecast.marks_for` was fixed to PAGINATE the EDGAR
full-text search (the v1 single-page pull missed the now-public names whose pre-IPO
filings sit beyond the first 100 hits).

VERDICT (what the paper prints, §7.1): a family RANKING is still not supportable — each
family scores only 1–4 exits — so the printed results are (i) the anti-result ("no house
is a systematically better forecaster"), (ii) the one directional regularity: Fidelity's
last pre-IPO marks undershot in all three of its clean exits (Reddit −5%, Circle −25%,
Figma −28%), and (iii) the exit-scale mirror structure: five insurance platforms /
twenty-two sub-advised funds carried Instacart at T. Rowe's identical $32.50 (the same
platforms mirror T. Rowe's ServiceTitan mark), other sleeves at the higher class levels
($37.18, $41.62). A junk row (Fidelity's $0.00 Chime placeholder, n=1) is filtered here.

Run: python3 src/family_accuracy.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Major named houses (per src/family_forecast.py FAM map); everything else in the CSV is
# treated as a sub-advised / variable-insurance sleeve registrant.
MAJOR_FAMILIES = {"Fidelity", "T. Rowe Price", "Alger", "ClearBridge", "American Funds",
                  "Nuveen", "BlackRock", "Morgan Stanley", "Baron", "Franklin", "JPMorgan",
                  "Wellington", "Vanguard", "Destiny Tech100", "Principal"}


def load() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "ipo_premarks_byfund.csv")
    df = df[df.mark_pps > 0].copy()      # drop $0.00 written-off placeholders (junk marks)
    df["abs_err_pct"] = df.err_pct.abs()
    df["is_sleeve"] = ~df.family.isin(MAJOR_FAMILIES)
    return df


# Sleeve registrant -> insurer group (MML Series Investment is MassMutual's second trust:
# counting it separately would repeat, at platform level, the exact count-funds-not-houses
# error the paper warns against).
INSURER_OF = {"LINCOLN": "Lincoln", "Voya": "Voya", "Brighthouse": "Brighthouse",
              "MASSMUTUAL": "MassMutual", "MML": "MassMutual"}


def instacart_sleeve_counts(df: pd.DataFrame | None = None) -> tuple[int, int, int]:
    """(#sleeve trusts, #funds, #insurer groups) carrying Instacart at the sub-advisor's
    identical $32.50 — the §7.1/§4.3 claims. Filtering to sleeves keeps the counts stable if
    the harvest later adds the T. Rowe / American Funds rows themselves (also $32.50)."""
    d = load() if df is None else df
    ic = d[(d.company == "Instacart") & (d.mark_pps == 32.5) & d.is_sleeve]
    insurers = {v for k, v in INSURER_OF.items() if ic.family.str.contains(k).any()}
    return len(ic), int(ic.n_funds.sum()), len(insurers)


def family_table(df: pd.DataFrame | None = None) -> pd.DataFrame:
    d = load() if df is None else df
    return (d.groupby("family")
              .agg(exits=("company", "nunique"), median_abs_err_pct=("abs_err_pct", "median"),
                   companies=("company", lambda s: ", ".join(sorted(set(s)))),
                   sleeve=("is_sleeve", "first"))
              .sort_values("median_abs_err_pct"))


def main() -> None:
    d = load()
    print("Per-exit family marks vs realized IPO (err = mark/IPO - 1):")
    for co, g in d.groupby("company"):
        print(f"  {co} (IPO ${g.ipo_pps.iloc[0]:.0f}/sh):")
        for _, r in g.sort_values("abs_err_pct").iterrows():
            tag = " [sleeve]" if r.is_sleeve else ""
            print(f"     {r.family:24s} ${r.mark_pps:>7.2f}  err {r.err_pct:+6.1f}%  "
                  f"(n={r.n_funds}){tag}")
    print("\nFamily accuracy (median |err| across exits — see docstring caveat):")
    print("  " + family_table(d).to_string().replace("\n", "\n  "))
    t, f, ins = instacart_sleeve_counts(d)
    print(f"\n§7.1/§4.3 sleeve-mirroring counts: {f} funds across {t} variable-insurance trusts "
          f"of {ins} insurers carried Instacart at the sub-advisor's identical $32.50.")
    exits = d.company.nunique()
    print(f"\nHARVEST STATUS: {exits}/7 fund-held exits present"
          + ("" if exits == 7 else " — PARTIAL; re-run src/family_forecast.py with SEC access "
             "before drawing any family-ranking conclusion."))


if __name__ == "__main__":
    main()
