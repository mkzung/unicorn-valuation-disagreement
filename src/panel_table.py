#!/usr/bin/env python3
"""Render the secondary-market cross-section (`data/valuation_panel.csv`) as a table.

SECOND-PAPER SEED. The section this table belonged to — the secondary-market estimate
against the last headline round — left with the Forge and prediction-market legs, so this
paper renders no such table and nothing here calls this module. It ships as part of that
seed, beside `analyze.py` and `forge_index.py`, and `tests/test_package_integrity.py` names
it on `PAPER_TWO` so that "nothing calls it" stays a stated decision rather than a discovery.

The `--check` mode compares its output against `paper/draft.md`. In THIS repository that
comparison has nothing to find and nothing runs it. An earlier version of this docstring
promised the manuscript was held against this output and could not drift from it, which was a
guarantee this package does not provide — a claim of the same kind as a budget set too high to
fail. Its own test file went with the section. The guard that objects to such a promise reads
this file too, so the retracted wording is described here rather than quoted.

The renderer itself is unchanged and correct: the gap column is the metric `analyze.py`
computes for the headline numbers (`forge/headline - 1`), at the same rounding.

Pure local read, no network.
  python3 src/panel_table.py           # print the rendered table
  python3 src/panel_table.py --check   # compare against paper/draft.md (nothing runs this)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "valuation_panel.csv"
DRAFT = ROOT / "paper" / "draft.md"

# Short, scannable labels for the CSV `quality_flag` values. "clean" rows are the
# unflagged primary-round subset the headline statistics use.
FLAG_LABEL = {
    "clean": "clean",
    "stale_headline": "stale",
    "tender_not_primary": "tender",
    "contested_headline": "contested",
    "xrp_treasury_caveat": "treasury",
}

def caption(df: "pd.DataFrame | None" = None) -> str:
    """Table B.1 caption, with the panel sizes computed live from the CSV (so the
    quoted n never drifts from the data the rows are rendered from)."""
    if df is None:
        df = load()
    n, n_clean = len(df), int((df["quality_flag"] == "clean").sum())
    n_multi = outlet_counts(df).ge(2).sum()
    return _CAPTION_TMPL.format(n=n, n_clean=n_clean, n_multi=n_multi,
                                n_single=_word(n - n_multi))


def outlet_counts(df: "pd.DataFrame | None" = None) -> "pd.Series":
    """How many independent outlets each headline round cites.

    Sources are recorded one per row as a delimited list, so the count is delimiters
    plus one. §2 and the caption both quote the tally; they read it from here.
    """
    if df is None:
        df = load()
    return df.headline_source.astype(str).str.count(r"[/,+]").add(1)


def _word(k: int) -> str:
    """Small counts read better spelled out mid-sentence; large ones do not."""
    names = ["zero", "one", "two", "three", "four", "five", "six",
             "seven", "eight", "nine", "ten", "eleven", "twelve"]
    return names[k] if k < len(names) else f"{k}"


_CAPTION_TMPL = (
    # Bold covers the label and nothing else, as in the other twenty-five captions. This
    # used to bold the whole title, which set a paragraph of bold in the PDF; the assembler
    # normalises the one remaining stray, and the generator has to agree with it or
    # `test_table_is_in_sync_with_draft` fails on a caption nobody edited.
    "**Table B.1.** Secondary-market estimate vs the last headline round, June 2026 "
    "(full panel n={n}; clean primary-round subset n={n_clean}). "
    "Gap = Forge secondary estimate / last headline round − 1 (positive ⇒ secondary "
    "above the last round); Forge per-company estimates are attributed inputs (Forge "
    "Global, as of 24 June 2026) and {n_multi} of the {n} headline rounds carry two or "
    "more independent outlets and {n_single} carry one, recorded per row "
    "(`data/valuation_panel.csv`). Rows are sorted by gap. *Flags:* stale = last priced "
    "round >12 months old; tender = last benchmark is a secondary tender, not a primary "
    "round; contested = a newer round is reported but not yet closed; treasury = a large "
    "token treasury complicates equity value. Headline statistics use the unflagged "
    '("clean") rows.'
)

COLUMNS = ["Company", "Sector", "Headline $B", "Round", "Forge $B", "Gap", "Flag"]


def _num(x: float) -> str:
    """Compact $B string: trim trailing zeros (965.0 -> '965', 170.70 -> '170.7',
    0.913 -> '0.91'), matching how the panel reports each level."""
    s = f"{round(float(x), 2):.2f}".rstrip("0").rstrip(".")
    return s


def _gap(g: float) -> str:
    """Integer-percent gap with the manuscript's Unicode minus (U+2212), e.g. '+69%',
    '−40%' — the rounding the §7.2/§7.2 prose and Appendix C.4 table already use per name."""
    return f"{g:+.0f}%".replace("-", "−")


def load() -> pd.DataFrame:
    df = pd.read_csv(PANEL)
    # OUR derived metric, identical to src/analyze.py.
    df["gap_pct"] = (df["forge_val_busd"] / df["headline_val_busd"] - 1.0) * 100.0
    return df.sort_values("gap_pct", ascending=False).reset_index(drop=True)


def render_rows(df: pd.DataFrame | None = None) -> list[str]:
    if df is None:
        df = load()
    rows = []
    for _, r in df.iterrows():
        flag = FLAG_LABEL.get(r["quality_flag"], r["quality_flag"])
        rows.append(
            f"| {r['company']} | {r['sector']} | {_num(r['headline_val_busd'])} | "
            f"{r['headline_date']} | {_num(r['forge_val_busd'])} | "
            f"{_gap(r['gap_pct'])} | {flag} |"
        )
    return rows


def render_table(df: pd.DataFrame | None = None) -> str:
    """The full Table B.1 block: caption + header + separator + 24 rows."""
    if df is None:
        df = load()
    header = "| " + " | ".join(COLUMNS) + " |"
    sep = "| " + " | ".join(["---"] * len(COLUMNS)) + " |"
    return "\n".join([caption(df), "", header, sep, *render_rows(df)])


def main(argv: list[str]) -> int:
    table = render_table()
    if "--check" in argv:
        draft = DRAFT.read_text(encoding="utf-8")
        if table in draft:
            print(f"OK: Table B.1 ({len(render_rows())} rows) present and in sync in draft.md")
            return 0
        sys.stderr.write(
            "draft.md Table B.1 out of sync with data/valuation_panel.csv — "
            "regenerate with `python3 src/panel_table.py` and paste into §7.2.\n"
        )
        return 1
    print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
