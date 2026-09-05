"""
Canonical headline-numbers registry — the single source of truth that ties the
paper's PROSE to the code that produces it.

Every load-bearing figure quoted in `paper/draft.md` / `README.md` is listed here
exactly once, paired with (a) the value RECOMPUTED live from the production loaders
(`robustness`, `validation`, `fund_marks`, `fund_marks_timeseries`, `forge_index`,
`prediction_markets`) and (b) the literal token the paper uses to state it.

Two consumers share this registry:
  - `src/reproduce.py`         — one-command pipeline run + `notes/reproduction_manifest.md`.
  - `tests/test_paper_consistency.py` — fails CI if any number drifts in the CODE
                                        *or* in the PROSE.

Why this exists: the code-only `tests/test_metrics.py` pins metrics against the
loaders but never reads the manuscript, so it cannot catch PROSE drift — the exact
failure mode that bit this project twice (the v0.11 stale n=9 numbers left in the
README, and the v0.12 stale result-#7 block). A number quoted in the text that no
longer matches the code is the cheapest possible way to lose a referee's trust;
this module makes that a build failure instead of a manual catch.

This file NEVER re-implements a metric — it only calls the production functions and
reads the committed data files, so it cannot quietly disagree with the pipeline.

Run directly to print the registry:  python3 src/paper_numbers.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest as _binomtest
from scipy.stats import mannwhitneyu as _mannwhitneyu
from scipy.stats import wilcoxon as _scipy_wilcoxon


def _wilcoxon(values) -> float:
    """Wilcoxon signed-rank p vs 0, matching robustness.py's R1 call (default zero handling)."""
    try:
        return float(_scipy_wilcoxon(values).pvalue)
    except ValueError:
        return float("nan")


def _wilcoxon_stat(values) -> float:
    """Wilcoxon signed-rank W statistic (same call as _wilcoxon)."""
    try:
        return float(_scipy_wilcoxon(values).statistic)
    except ValueError:
        return float("nan")


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import company_class as ccl
import family_accuracy as fa
import level1_placebo as l1p
import listing_dates as ld
import cross_signal as cs
import forge_corroboration as fcor
import fund_marks as fm
import fund_marks_bulk as fmb
import p4_pretest as p4
import reconcile_versions as _rvmod
import robustness as rb
import validation as val

DRAFT = ROOT / "paper" / "draft.md"
README = ROOT / "README.md"
DATA_DICT = ROOT / "notes" / "data_dictionary.md"
# Figure captions do not live in the manuscript: they are assembled in the build script and
# printed under the image, which is why Figure 9 kept quoting a superseded median through a
# full rebuild of the section it illustrates. The build script is a prose file for this
# purpose and is checked as one.
CAPTIONS = ROOT / "src" / "build_pdf.py"
_FILE = {"draft": DRAFT, "readme": README, "dict": DATA_DICT, "caption": CAPTIONS}


@dataclass
class Number:
    """One canonical figure: computed from code, quoted in the prose."""
    section: str          # paper section, e.g. "4.4"
    label: str            # human description
    computed: float       # value recomputed live from the production code
    value: float          # value the paper states (the claim)
    tol: float            # |computed - value| must be <= tol
    claim: str | None     # exact prose token, e.g. "24%"; None => numeric-only (no prose check)
    in_files: tuple = field(default=())   # which of _FILE must contain `claim`
    # For tokens too common for bare-substring presence to be tight (e.g. "24%"), an optional
    # per-file CONTEXT phrase (which also pins the number to its role) that must ALSO appear,
    # so PARTIAL drift — one stale mention among several — is still caught.
    context: dict = field(default_factory=dict)   # {"draft": phrase, "readme": phrase}

    @property
    def code_ok(self) -> bool:
        return abs(self.computed - self.value) <= self.tol


def prose_missing(n: "Number") -> list[str]:
    """Human-readable list of prose checks that FAIL for `n` (empty => prose is consistent):
    the bare claim token must be present in each `in_files`, and any per-file `context` phrase
    must be present in that file."""
    miss = []
    if n.claim:
        for w in n.in_files:
            if not appears_in(n.claim, w):
                miss.append(f"token '{n.claim}' absent from {w}")
    for w, phrase in n.context.items():
        if not appears_in(phrase, w):
            miss.append(f"context '{phrase}' absent from {w}")
    return miss


def _norm(s: str) -> str:
    """Normalise the Unicode minus (U+2212) the prose uses to an ASCII hyphen so an
    ASCII claim like '-62%' matches the manuscript's '−62%'. (En-dash is left alone.)"""
    return s.replace("−", "-")


def _demark(s: str) -> str:
    """Drop emphasis markers, so a check asserts the claim and not the markup.

    Seventy-six of the registered tokens carried `**` around the figure, which tied the
    guard to a typographic choice: de-bolding a sentence broke the build even though every
    number in it was unchanged. The manuscript now bolds only run-in paragraph labels, the
    way a journal does, and that would have been impossible to do while the checks read the
    asterisks. Both sides are stripped, so an entry may still be written with the emphasis
    it has in the prose without pinning it there.
    """
    return s.replace("**", "").replace("*", "")


_TEXT_CACHE: dict[str, tuple[tuple, str]] = {}


def _prose(which: str) -> str:
    """The named file, minus-normalised and stripped of emphasis, read once.

    Four hundred and fifty tokens each re-reading and re-scanning a 230 KB file put the
    guard over the two-minute mark on its own. Keyed on mtime and size so an edit mid-session
    is picked up.
    """
    p = _FILE[which]
    st = p.stat()
    key = (st.st_mtime_ns, st.st_size)
    hit = _TEXT_CACHE.get(which)
    if hit is None or hit[0] != key:
        _TEXT_CACHE[which] = (key, _demark(_norm(p.read_text(encoding="utf-8"))))
    return _TEXT_CACHE[which][1]


def appears_in(claim: str, which: str) -> bool:
    """True iff `claim` is a substring of the named manuscript file, ignoring emphasis."""
    return _demark(_norm(claim)) in _prose(which)


_REGISTRY_MEMO: dict[tuple, list["Number"]] = {}


def _inputs_key() -> tuple:
    """Everything `canonical_numbers` is a function of: the four prose files and the panel.

    The registry is rebuilt by nineteen separate tests in `tests/test_paper_consistency.py`,
    and each rebuild re-runs a 20,000-draw permutation and a 2,032-partition specification
    curve — about a minute and a half of work to answer the same question nineteen times.
    Memoising on the inputs makes the guard fast enough to run on every commit without making
    it weaker: touch any of the four files, or the marks file behind the panel, and the key
    moves, so an edit can never be checked against a registry built before it.
    """
    import population as pop
    files = tuple((f.stat().st_mtime_ns, f.stat().st_size) for f in
                  (DRAFT, README, DATA_DICT, CAPTIONS))
    return files + (pop._cache_key(),)


def canonical_numbers() -> list[Number]:
    """Recompute every headline number from the production code. Heavy permutation
    tests (sector contrast/confound) run once each here."""
    key = _inputs_key()
    if key in _REGISTRY_MEMO:
        return list(_REGISTRY_MEMO[key])
    _REGISTRY_MEMO.clear()
    out = _build()
    _REGISTRY_MEMO[key] = out
    return list(out)


# The registry was written against the paper's PRE-REFRAME numbering and the calls below still
# carry it: `add("5.6", ...)` names a section the manuscript has not had for four rounds. That
# is not cosmetic. Every failure message quotes the section, so a reader chasing a drift is sent
# to a section that does not exist; and six entries belonging to legs that were cut kept passing
# partly because nothing could see that their section had gone. Translated once, here, rather
# than by editing three hundred call sites — the call sites are where the numbers are computed,
# and each edit to one of them is a chance to move a number by accident.
#
# `tests/test_registry_sections.py` asserts that every value on the right is a heading the paper
# actually has, so a future cut cannot leave an entry pointing at nothing.
SECTION_ALIASES = {
    "3": "2.1",          # the N-CSR lot with a disclosed entry price
    "4.1": "paper2",     # secondary-panel data-dictionary rows; the leg is a second paper
    "4.3": "7",          # the IPO exits
    "4.4": "4.3",        # cross-fund marks on ten names
    "4.8": "B",          # robustness
    "4.9": "4.3",        # coverage of the ten-name panel
    "4.12": "5.6",       # booked value at the by-company scale
    "5.2": "3.1",        # the population harvest
    "5.3": "3.2",        # identity resolution
    "5.4": "4.1",        # a filer is a trust, the opinion belongs to the house
    "5.5": "5.1",        # the population panel
    "5.6": "5.5",        # what kind of company the mark is on
    "5.7": "5.6",        # where the booked value sits
    # §5.1 carried four results under one heading — the level, the coverage mixture, the
    # calendar and the dissenter — and 40% of section 5 sat in one block. Splitting it gave
    # the last three their own numbers, and these three keys are how the registry follows.
    # They are written in the live numbering because they postdate the reframe entirely.
    "5.5-mix": "5.2",    # what the median is made of
    "5.5-cal": "5.3",    # the same median, year by year
    "5.5-out": "5.4",    # a consensus, and a dissenter
    "5.8": "6.1",        # a trait of the company, not of the date
    "5.9": "6.2",        # the stood-pat cells
    "5.10": "4.2",       # within a house the mark is one number
    "5.11": "6.3",       # the size relationship the paper disowned
    "5.12": "C.3",       # every published cell, harvest cap lifted
    # §5.4 has no pre-reframe ancestor — it was written after the reframe, to say which
    # of the three medians to quote — and its own label collides with a pre-reframe key,
    # because "5.4" used to be the filer-is-a-trust subsection. A figure stated there is
    # therefore addressed by a name that cannot collide.
    "5.4-current": "5.7",
    # The microscope and the data section changed places: the lot a reader can check now
    # comes before the rules that make the population comparable, which removes the two
    # forward references §3 used to make and creates none. These three keys are written in
    # the live numbering rather than the pre-reframe numbering, so they moved with it.
    "2.3": "3.3",        # which security the mark is of
    "3.2": "2.2",        # is the microscope's lot unusual
    "3.3": "2.3",        # the Level-1 placebo
    "A": "A.1",          # the data appendix
}


def _build() -> list[Number]:
    out: list[Number] = []

    def add(section, label, computed, value, tol, claim, in_files=(), context=None):
        out.append(Number(SECTION_ALIASES.get(section, section), label,
                          float(computed), float(value), float(tol),
                          claim, tuple(in_files), context or {}))

    # ---- §2 coverage (the "small n, majority of the dollars" defense) ----------------
    panel = pd.read_csv(ROOT / "data" / "valuation_panel.csv")
    # The paper used to claim every headline carried two independent outlets. The file says
    # otherwise for seven rows, so the count is pinned rather than the claim asserted.
    # How coarse the round dates really are. §10.3 called them "coarse, month- or
    # quarter-level, for a few names", which understates the base case (month-level is 25 of
    # 28, not an exception) and misses the one year-only row. Counted here so the sentence
    # cannot drift back: Table B.1 prints four different date formats in one column and
    # nothing was checking how many of each.

    # ---- §7.2 secondary cross-section ------------------------------------------------
    gc = rb.cross_section_gaps(clean_only=True)
    gf = rb.cross_section_gaps(clean_only=False)
    # The data dictionary states the same two counts in its own words. Pinning them here is
    # what catches the drift that a panel expansion introduces if only the paper is updated.
    add("4.1", "full panel size (data dictionary)", len(gf), 28, 0, "**28 names**", ["dict"])
    add("4.1", "clean subset size (data dictionary)", len(gc), 17, 0,
        "clean primary-round subset **17**", ["dict"])
    # The Table 1 rows are pinned verbatim by the second paper's own suite, but the sentence
    # that describes their range is separate prose: change the panel and the table updates
    # while the sentence quietly does not. These pin the sentence to the same data.
    # "+4.0%" appears twice in the paper meaning two different things: the upper bootstrap
    # bound above, and the favoured-sector median here. A bare token pins only one of them,
    # so both sector medians are tied to the sentence they belong to.

    # ---- §7.1 IPO-exit validation (the differentiator) -------------------------------
    ve = val.add_errors(val.load())
    fmrows = ve[ve.preipo_signal_type == "fund_mark"]
    wins = int((fmrows.least_wrong == "fund mark").sum())
    add("4.3", "fund-held exits scored", len(fmrows), 7, 0, None)
    add("4.3", "exits where the fund mark is least-wrong", wins, 5, 0, "five of", ["draft", "readme"])
    # honest power on the IPO leg: the count cannot carry the claim, the magnitudes can
    add("4.3", "sign-test p on the win count", _binomtest(wins, len(fmrows), 0.5,
        alternative="greater").pvalue, 0.227, 0.01, "p=0.23", ["draft"])
    add("4.3", "paired Wilcoxon p on |errors|",
        float(_scipy_wilcoxon(fmrows.signal_err_pct.abs(), fmrows.overshoot_pct.abs(),
                              alternative="less")[1]), 0.078, 0.005, "0.078", ["draft"])
    _cln = fmrows[fmrows.quality_flag == "clean"]
    add("B", "clean-flag exits where the mark wins",
        int((_cln.signal_err_pct.abs() < _cln.overshoot_pct.abs()).sum()), 4, 0,
        "four of five", ["draft"])
    add("4.3", "median |fund-mark error| %", fmrows.signal_err_pct.abs().median(), 11, 1.5,
        "11%", ["draft", "readme"],
        {"draft": "absolute error of **11%**", "readme": "median |error| **11% vs 48%**"})
    add("4.3", "median |headline error| %", fmrows.overshoot_pct.abs().median(), 48, 1.5,
        "48%", ["draft", "readme"],
        {"draft": "**48%** for the headline", "readme": "11% vs 48%"})
    # With seven exits the median is the fourth-ranked error, so both of the figures above are
    # a single named exit rather than a summary of anything. §7.1 says so, and says it at the
    # precision that makes the identity checkable, which is what these two entries pin. They
    # exist because the prose figure guard would otherwise see 48.19% and 11.06% as loose
    # numbers, and the honest way past that guard is to register a number, not to round it
    # until it disappears.
    _byco = fmrows.set_index("company")
    add("4.3", "the headline median IS Figma's own error (%)",
        abs(float(_byco.overshoot_pct["Figma"])), 48.19, 0.005, "−48.19%", ["draft"])
    add("4.3", "the mark median IS ServiceTitan's own error (%)",
        abs(float(_byco.signal_err_pct["ServiceTitan"])), 11.06, 0.005, "+11.06%", ["draft"])
    add("D", "2021-peak-vintage headline overshoot median %",
        ve[ve.vintage == "2021-peak"].overshoot_pct.median(), 160, 2, "+160%", ["draft", "readme"])

    # ---- §7.1 cross-fund N-PORT marks ------------------------------------------------
    m = fm.load()
    add("A.1", "clean Level-3 holdings", len(m), 386, 0, "386 Level-3", ["draft", "readme"])
    add("A.1", "distinct funds", m.fund.nunique(), 104, 0, "104 mutual funds", ["draft", "readme"])
    add("A.1", "distinct companies", m.company.nunique(), 15, 0, "15 companies", ["draft", "readme"])
    add("4.4", "median cross-fund spread %", rb.dispersion_median(4.0, 5)[0], 24, 1.0,
        "24%", ["draft", "readme"],
        {"draft": "median of **24%**", "readme": "median **24%**"})
    clean_ft, _ = rb.clean_fund_table(3.0)
    anth = rb._modal_slice(clean_ft, "Anthropic").pps
    add("4.4", "Anthropic cross-fund spread %", (anth.max() / anth.min() - 1) * 100, 39, 1.5,
        "39%", ["draft", "readme"],
        {"draft": "Anthropic **39%**", "readme": "+39% Anthropic"})
    add("4.4", "OpenAI single herded mark $/sh",
        rb._modal_slice(clean_ft, "OpenAI").pps.median(), 687.69, 0.02, "$687.69", ["draft", "readme"])
    slv_trusts, slv_funds, slv_insurers = fa.instacart_sleeve_counts()
    add("D", "Instacart mirror-sleeve trusts at $32.50", slv_trusts, 5, 0,
        "five variable-insurance trusts", ["draft"])
    add("D", "Instacart mirror-sleeve funds at $32.50", slv_funds, 22, 0,
        "twenty-two sub-advised funds", ["draft"])
    add("D", "Instacart mirror-sleeve insurer groups", slv_insurers, 4, 0,
        "four insurers", ["draft"])

    # ---- Appendix D is the cross-family spread just staleness? ------------------------------
    import mark_staleness as ms
    _fq = ms.load()
    _rates, _cells = ms.remark_rates(_fq), ms.cells(_fq)
    _adj = _fq[_fq.adjacent]
    _ok = _cells[_cells.judgeable]          # freshness determinable for every family present
    _fresh = _ok[_ok.all_remarked]
    _stale = _ok[~_ok.all_remarked]
    add("4.8", "overall family remark rate (%)", _adj.remarked.mean() * 100, 79, 1.0,
        "79%", ["draft", "readme"])
    add("4.8", "lowest family remark rate (%)", _rates.remark_rate.min() * 100, 58, 1.0,
        "58%", ["draft", "readme"])
    add("4.8", "highest family remark rate (%)", _rates.remark_rate.max() * 100, 92, 1.0,
        "92%", ["draft", "readme"])
    add("4.8", "cells where freshness is determinable", len(_ok), 105, 0, "105", ["draft"])
    # The three family-collapsed spreads and the median remark move are restated in the
    # robustness appendix in bold, which the "no bolded figure escapes the registry" guard now
    # reaches. Pinned to the code that produces them rather than left as prose.
    _fc = rb.family_collapsed_dispersion().set_index("company").family_spread_pct
    add("4.8", "family-collapsed spread, Gusto (%)", _fc["Gusto"], 32, 0.5,
        "Gusto **32%** across 3", ["draft"])
    add("4.8", "family-collapsed spread, Databricks (%)", _fc["Databricks"], 15, 0.5,
        "Databricks **15%** across 6", ["draft"])
    _moves = _adj[_adj.remarked]
    add("4.8", "median size of a family's remark move (%)",
        (_moves.pps / _moves.prev_pps - 1).abs().median() * 100, 12, 0.5,
        "the median move is **12%**", ["draft"])
    add("4.8", "freshly-remarked cells", len(_fresh), 67, 0, "67", ["draft"])
    add("4.8", "median spread, every family remarked (%)", _fresh.spread_pct.median(), 12.1,
        0.3, "12.1%", ["draft", "readme"])
    add("4.8", "median spread, someone stood pat (%)", _stale.spread_pct.median(), 6.7, 0.3,
        "6.7%", ["draft", "readme"])
    add("4.8", "cells where a house stood pat", len(_stale), 38, 0, "38", ["draft"])
    _sens = ms.sensitivity()
    add("4.8", "fresh-cell median, lowest over remark tolerances (%)",
        min(r["fresh"] for r in _sens["tol"]), 12.0, 0.15, "12.0%", ["draft"])
    add("4.8", "fresh-cell median, highest over remark tolerances (%)",
        max(r["fresh"] for r in _sens["tol"]), 12.3, 0.15, "12.3%", ["draft"])
    add("4.8", "companies with cells of both kinds", _sens["companies_compared"], 6, 0,
        "six", ["draft"])
    add("4.8", "companies where fresh cells are wider", _sens["companies_fresh_wider"], 5, 0,
        "five of the six", ["draft"])
    add("4.8", "companies behind the judgeable cells", _sens["n_companies"], 7, 0, "seven",
        ["draft"])
    _quiet = _ok[_ok.none_remarked]
    add("4.8", "quiet cells (no family moved a mark)", len(_quiet), 5, 0, "five", ["draft"])
    add("4.8", "quiet cells at a zero spread", int((_quiet.spread_pct < 0.5).sum()), 3, 0,
        "three sit at a 0% spread", ["draft"])
    add("4.8", "one-sided p that fresh cells are tighter",
        float(_mannwhitneyu(_fresh.spread_pct, _stale.spread_pct, alternative="less")[1]),
        0.966, 0.02, "p=0.97", ["draft"])
    # coverage asymmetry: which side of the §7.2 split the fund record actually sees
    _held = set(pd.read_csv(ROOT / "data" / "fund_marks.csv").company)
    _rest = panel[~panel.sector.isin(ms.FAVORED_SECTORS)]
    _deep = panel[panel.sector.isin(ms.DEEP_DISCOUNT_SECTORS)]
    add("4.8", "rest-bucket names with an N-PORT mark",
        _rest.company.isin(_held).sum(), 3, 0, None)
    add("4.8", "deep-discount names with an N-PORT mark",
        _deep.company.isin(_held).sum(), 0, 0, None)

    # ---- §7.1 family-level adjudication facts (completed per-series harvest) ----------
    pm_fam = fa.load()
    fid = pm_fam[(pm_fam.family == "Fidelity")]
    add("4.3", "Fidelity clean fund-mark exits", len(fid), 3, 0, None)
    add("D", "Fidelity pre-IPO marks all undershot (1=yes)", float((fid.err_pct < 0).all()),
        1, 0, "undershot in all three", ["draft"])
    add("D", "T. Rowe sister series filing Instacart's $32.50",
        int(pm_fam[(pm_fam.company == "Instacart")
                   & (pm_fam.family == "T. Rowe Price")].n_funds.sum()),
        22, 0, "twenty-two T. Rowe series", ["draft"])
    add("D", "Fidelity sister series filing Reddit's $32.37",
        int(pm_fam[(pm_fam.company == "Reddit")
                   & (pm_fam.family == "Fidelity")].n_funds.sum()),
        22, 0, "twenty-two Fidelity series", ["draft"])
    ic_levels = sorted(pm_fam[pm_fam.company == "Instacart"].mark_pps.unique())
    add("D", "Instacart second class level $/sh", ic_levels[1], 37.18, 0.01, "$37.18", ["draft"])
    add("D", "Instacart top class level $/sh", ic_levels[2], 41.62, 0.01, "$41.62", ["draft"])

    # ---- Appendix D out-of-panel replication (expansion probe) ------------------------------
    probe = pd.read_csv(ROOT / "data" / "nport_expansion_probe.csv")
    probe = probe[probe.fair_val_level == 3]
    add("4.8", "expansion-probe names", probe.company.nunique(), 5, 0,
        "five-name expansion probe", ["draft"])
    fan = probe[probe.company == "Fanatics"]
    fan_md = fan[fan.report_date == fan.report_date.max()]
    add("4.8", "Fanatics same-date funds", fan_md.fund.nunique(), 7, 0,
        "7 same-date funds", ["draft"])
    add("4.8", "Fanatics same-date registrant families", fan_md.registrant.nunique(), 3, 0,
        "three families", ["draft"], {"draft": "Fanatics"})
    fan_spread = (fan_md.price_per_share.max() / fan_md.price_per_share.min() - 1) * 100
    add("4.8", "Fanatics cross-family spread %", fan_spread, 75, 1.5, "75%", ["draft"],
        {"draft": "cross-family spread of **75%**"})

    # ---- Appendix A dataset-coverage counts (Table A.1 must not silently go stale) -----
    add("A", "expansion-probe marks", len(pd.read_csv(ROOT / "data" / "nport_expansion_probe.csv")),
        29, 0, "29 marks", ["draft"])
    add("A", "family-exit premark rows", len(pd.read_csv(ROOT / "data" / "ipo_premarks_byfund.csv")),
        18, 0, "18 family-exit rows", ["draft"])
    add("A", "placebo rows (5 securities x 2 families)",
        len(pd.read_csv(ROOT / "data" / "level1_placebo.csv")), 10, 0, None)

    # ---- Appendix C.1 fund marks through time ------------------------------------------------

    # Counts written as words escape a digit scan, and these two come from a live EDGAR
    # sweep whose per-family counts move between harvests: the ServiceTitan row shifted
    # from 21 to 17 during one refresh. Pinned so the prose cannot outlive the data.
    pmk = pd.read_csv(ROOT / "data" / "ipo_premarks_byfund.csv")

    def _series(co, fam):
        r = pmk[(pmk.company == co) & (pmk.family.str.contains(fam, case=False, na=False))]
        return float(r.n_funds.iloc[0]) if len(r) else float("nan")

    add("4.3", "T. Rowe series filing Instacart's mark", _series("Instacart", "T. Rowe"),
        22, 0, None, (), {"draft": "twenty-two T. Rowe series file Instacart's $32.50"})
    add("4.3", "Fidelity series filing Reddit's mark", _series("Reddit", "Fidelity"),
        22, 0, None, (), {"draft": "twenty-two Fidelity series Reddit's $32.37"})

    # Sample sizes are the first thing a referee checks, and in this manuscript they are
    # spelled out in words, where no digit scan reaches them.
    ivd = pd.read_csv(ROOT / "data" / "ipo_validation.csv")
    add("4.3", "exits scored", len(ivd), 10, 0, None, (),
        {"draft": "ten unicorns that listed"})
    add("4.3", "exits with a pre-IPO fund mark", (ivd.preipo_signal_type == "fund_mark").sum(),
        7, 0, None, (), {"draft": "seven were broadly mutual-fund-held"})

    # Appendix C.2's Forge corroboration was cut with the secondary leg; the loads that fed
    # it went on running on every registry build and their results went nowhere.

    # ---- Appendix D robustness -------------------------------------------------------------
    # §7.2's specification curve, with the joint inference Simonsohn-Simmons-Nelson require.
    # The null is what makes these numbers worth printing: an earlier version quoted the
    # count and the composition as evidence, and both sit inside their own null.
    import sector_specification_curve as scv
    _sc = scv.summary(scv.curve())
    add("F.4", "alternative sector partitions evaluated", _sc["n_splits"], 2032, 0,
        "**2,032**", ["draft"])
    # The other six specification-curve figures were registered against a section that is now in
    # the second paper, and they went on passing because a bare number matches anywhere in the
    # manuscript: `82` was landing on the listing-date gap in §9.1, `p=0.43` on the P4 pre-test,
    # `first` on fifty-six unrelated sentences, and `112` on the event-study ladder's "65 / 112"
    # until that count changed. Only the partition count is still stated in the prose (§10.1),
    # so only it stays registered. The rest travel with the sector leg.

    cf = rb.sector_confound(clean_only=True)
    add("4.8", "confound-adjusted favored coef p (rank gap)", cf["p_rank"], 0.002, 0.0025, None)
    vd = rb.family_variance_decomp()
    eta_material = vd[vd.total_spread_pct >= 5].eta2_between_family.median()
    add("4.8", "between-family variance share (material names)", eta_material, 1.00, 0.02, "η²", ["draft", "readme"])
    wf = rb.within_family_spreads()
    add("4.8", "share of family-cells bit-identical (%)",
        (wf.within_spread_pct < 0.5).mean() * 100, 89, 3, "89%", ["draft", "readme"],
        {"draft": "in **89%", "readme": "89% of family"})

    # ---- Appendix D Forge-leg independent corroboration ------------------------------------
    fcs = fcor.summary(fcor.enrich(fcor.load()))
    add("4.8", "panel names with an independent secondary cross-check",
        fcs["n_cross_checked"], 11, 0, None)
    add("4.8", "Level-1 cross-family spread % (placebo)", l1p.cross_family_spread()[1], 0.0, 0.01,
        "0.00%", ["draft"])

    # ---- Appendix C.4 cross-signal synthesis -------------------------------------------------
    add("4.9", "cross-fund >=5-fund names (§4.3 coverage)", len(cs.fund_spreads()), 10, 0, None)

    md_nav = fm.load()
    add("4.12", "total mutual-fund NAV booked across the names ($B)",
        md_nav.val_usd.sum() / 1e9, 24.7, 0.25, "$24.7B", ["draft"])
    _hi = set(pd.read_csv(ROOT / "data" / "fund_marks_dispersion.csv")
              .query("spread_pct >= 15").company)
    add("4.12", "high-disagreement booked NAV ($B)",
        md_nav[md_nav.company.isin(_hi)].val_usd.sum() / 1e9, 1.9, 0.2, "$1.9B", ["draft"])

    _population(add)
    _microscope(add)
    _dynamic(add)
    _instruments(add)
    _cost(add)
    return out


def _cost(add) -> None:
    """§11 — what the disagreement costs in the NAV investors transact at.

    Pinned against `data/nav_wedge_stats.csv` for the reason `_dynamic` gives, and that file
    carries a content hash of the marks file, the classification and every constant the
    measure is a function of.
    """
    import nav_wedge as nw
    s = nw.load_stats()
    add("G", "fund-positions in the wedge panel", s["positions"], 8529, 0,
        "Across 8,529 fund-positions", ["draft"])
    add("G", "companies in the wedge panel", s["companies"], 100, 0,
        "100 venture-backed companies", ["draft"])
    add("G", "funds in the wedge panel", s["funds"], 296, 0, "held by 296 funds", ["draft"])
    add("G", "houses in the wedge panel", s["houses"], 57, 0, "across 57 houses", ["draft"])
    add("G", "fund-dates in the wedge panel", s["fund_dates"], 3590, 0,
        "over 3,590 fund-dates", ["draft"])
    add("G", "booked value in the wedge panel ($B)", s["booked_busd"], 101.6, 0.05,
        "funds booked $101.6B", ["draft"])
    add("G", "gross wedge ($B)", s["gross_wedge_busd"], 6.6, 0.05,
        "moves $6.6B of booked value", ["draft"])
    add("G", "median wedge (bps of the fund's own net assets)", s["median_abs_bps"],
        0.33, 0.005, "a wedge of 0.33 basis points", ["draft"])
    add("G", "max wedge (bps)", s["max_abs_bps"], 161.1, 0.05,
        "The largest is 161 basis points", ["draft"])
    add("G", "median private book as a share of net assets (%)",
        s["median_private_pct_of_nav"], 0.22, 0.005, "a median 0.22% of its net assets",
        ["draft"])
    add("G", "largest private book as a share of net assets (%)",
        s["max_private_pct_of_nav"], 11.9, 0.05, "at most 11.9%", ["draft"])
    add("G", "fund-dates over 10 bps", s["n_over_material"], 258, 0,
        "258 fund-dates on 75 distinct funds", ["draft"],
        {"draft": "| 10 bp | 258 | 7.2% | 75 |"})
    add("G", "share of fund-dates over 10 bps (%)", s["share_over_material_pct"], 7.2, 0.05,
        "| 10 bp | 258 | 7.2% | 75 |", ["draft"])
    add("G", "distinct funds over 10 bps", s["funds_over_material"], 75, 0, None)
    # The line the drop was hiding. Before the group key was fixed this read zero, and §11.2
    # and the conclusion both printed "no fund-date in this panel reaches a hundred".
    add("G", "fund-dates over 100 bps", s["n_over_100bps"], 12, 0,
        "| 100 bp | 12 | 0.3% | 5 |", ["draft"])
    add("G", "distinct funds over 100 bps", s["funds_over_100bps"], 5, 0, None)
    # Who those funds are. A vehicle with no series identifier is an interval, closed-end or
    # tender-offer fund, and those are three-quarters of the fund-dates above a hundred bps.
    # There are 258 of them and there are also 258 fund-dates above ten basis points, two
    # different sets of the same size overlapping in 109. The prose names both counts, because
    # two sentences apart an unqualified "they" reads as the first set and means the second.
    add("G", "fund-dates filed with no series identifier",
        s["no_series_fund_dates"], 258, 0, "are 258 fund-dates themselves", ["draft"])
    add("G", "fund-dates filed with no series identifier (%)",
        s["no_series_fund_dates_pct"], 7.2, 0.05, "they are 7.2% of the fund-dates here",
        ["draft"])
    add("G", "fund-dates over 100 bps filed with no series identifier",
        s["no_series_over_100bps"], 9, 0, None)
    add("G", "median wedge among no-series-identifier fund-dates (bps)",
        s["no_series_median_abs_bps"], 5.3, 0.05, "a median wedge of 5.3 basis points",
        ["draft"])
    # The two designs, and the gap between them, which is the point of running both.
    add("G", "reversion cells, unbiased design", s["rev_lagged_cells"], 421, 0,
        "| selected on the previous date (unbiased) | 421 |", ["draft"])
    # Averaging over houses tied at the extreme, not picking one of them: the shipped figures
    # were 226 of 415 at p=0.039, and `idxmax` chose between near-equal deviations by
    # bit-equality, which a 1e-15 perturbation moves to 223 of 412 at p=0.052.
    add("G", "reversion, high house moves less (unbiased)", s["rev_lagged_negative"], 223, 0,
        "223 of 417", ["draft"])
    add("G", "reversion share, unbiased (%)", s["rev_lagged_neg_share_pct"], 53.5, 0.1,
        "53.5%, not the 56.9%", ["draft"])
    add("G", "reversion sign p, unbiased, one-sided", s["rev_lagged_p_sign"], 0.085, 0.0005,
        "| 0.085 |", ["draft"])
    add("G", "reversion sign p, unbiased, two-sided", s["rev_lagged_p_sign_two_sided"],
        0.170, 0.0005, "| 0.170 |", ["draft"])
    add("G", "reversion cells, biased design", s["rev_same_cells"], 483, 0,
        "| selected on the same date (mechanically negative) | 483 |", ["draft"])
    add("G", "reversion, high house moves less (biased)", s["rev_same_negative"], 275, 0,
        "275 of 483", ["draft"])
    add("G", "reversion share, biased design (%)", s["rev_same_neg_share_pct"], 56.9, 0.1,
        "56.9%", ["draft"])
    add("G", "persistence slope, all house-dates", s["persistence_slope"], 0.76, 0.005,
        "gives 0.76 across all house-dates", ["draft"])
    add("G", "persistence slope, house-dates with a side", s["persistence_slope_sided"],
        0.84, 0.005, "0.84 among those with a side at all", ["draft"])
    add("G", "house-dates with a side", s["persistence_n_sided"], 1071, 0,
        "the 1,071 house-dates with a side", ["draft"])
    add("G", "share of sided deviations on the same side one step later (%)",
        s["persistence_same_side_pct"], 85, 0.5, "85% are on the same side", ["draft"])
    # The two quantities that say WHY the median is small. The first draft of the section
    # named the wrong one and its own arithmetic disagreed by a factor of thirty.
    add("G", "positions sitting at the consensus (%)", s["at_consensus_pct"], 56.4, 0.05,
        "56.4% of the 8,529 positions sit at the consensus", ["draft"])
    add("G", "fund-dates with exactly zero wedge (%)", s["zero_wedge_fund_dates_pct"],
        22.5, 0.05, "22.5% of fund-dates carry a wedge of exactly zero", ["draft"])
    add("G", "median cell spread in the wedge panel (%)", s["median_cell_spread_pct"],
        5.9, 0.05, "a spread of 5.9%", ["draft"])
    # §11.1's worked example of the position-level class guard. Recomputed rather than
    # remembered: the guard removes these rows, so nothing downstream can see them, and an
    # example that justifies a filter is exactly the number most likely to go stale.
    add("F.2", "positions removed by the position-level class guard",
        s["class_guard_removed_positions"], 3, 0, None)
    add("F.2", "the unit-convention row: share count", s["class_guard_worst_shares"],
        2145462, 0, "2,145,462 Epic Games \"shares\"", ["draft"])
    add("F.2", "the unit-convention row: price per share", s["class_guard_worst_pps"],
        1.0, 0.005, "at $1.00 against a", ["draft"])
    add("F.2", "the unit-convention row: consensus", s["class_guard_worst_consensus_pps"],
        637, 0.5, "against a $637 consensus", ["draft"])
    add("F.2", "the unit-convention row: fund net assets ($m)",
        s["class_guard_worst_net_assets_musd"], 32, 0.5, "on a $32m fund", ["draft"])
    add("F.2", "the unit-convention row: wedge (bps)", s["class_guard_worst_wedge_bps"],
        -421062, 1, "a wedge of 421,062 basis points", ["draft"])
    # Table 16: what each filter removes. The max column is why the filters exist.
    # Every cell of Table 16, including the "over 10 bps" column the first version computed
    # and then did not register: two of its fifteen cells were unguarded. Read from the
    # committed statistics rather than recomputed — `filter_cost` rebuilds the panel three
    # times and put ninety seconds into a guard that runs on every commit.
    for i, (pos, fd, med, mx, over) in enumerate(
            [(40361, 14853, 0.08, 460.0, 976), (26790, 13160, 0.04, 444.4, 620),
             (8529, 3590, 0.33, 161.1, 258)]):
        add("G", f"filter {i}: fund-positions", s[f"filter{i}_positions"], pos, 0, None)
        add("G", f"filter {i}: fund-dates", s[f"filter{i}_fund_dates"], fd, 0, None)
        add("G", f"filter {i}: median |wedge| (bps)", s[f"filter{i}_median_abs_bps"],
            med, 0.005, None)
        add("G", f"filter {i}: max |wedge| (bps)", s[f"filter{i}_max_abs_bps"], mx, 0.05, None)
        add("G", f"filter {i}: fund-dates over 10 bps", s[f"filter{i}_over_10bps"], over, 0,
            None)
    add("F.2", "fund-positions the one-series filter removes",
        s["filter0_positions"] - s["filter1_positions"], 13571, 0,
        "removes 13,571 of 40,361 fund-positions", ["draft"])


def _microscope(add) -> None:
    """§2 — the N-CSR lot with a disclosed entry price, and the sensor's own distribution."""
    import ncsr_acquisitions as na
    d = na.load()
    cov = na.coverage(d).set_index("fact").n
    add("E.4", "N-CSR schedule rows", cov["schedule rows"], 767, 0,
        "**767 schedule rows, 10 companies, 44 registrants, 429 lot-period-series**", ["draft"])
    add("3", "N-CSR registrants", cov["filers"], 44, 0, None)
    add("E.4", "N-CSR rows carrying a share count", cov["rows carrying a share count"], 155, 0,
        "| rows with a share count | 29 | **155** |", ["draft"])
    a = na.agreement(d)
    add("3", "lot-period-series", len(a), 429, 0, None)
    add("3.2", "lots with two or more house labels", int((a.houses >= 2).sum()), 76, 0,
        "**76 carry two or more house labels and 45 carry two or more independent books.**",
        ["draft"])
    b = a[a.books >= 2]
    add("3.2", "cross-book comparisons at a fixed valuation date", len(b), 45, 0,
        "There are **45** such comparisons", ["draft"])
    add("3.2", "cross-book comparisons agreeing to a hundredth of a point",
        int((b.markup_gap_pts.abs() <= 0.01).sum()), 37, 0,
        "**37 agree to within a hundredth of a point", ["draft"])
    # The Series J lot itself. Cost and value are filed; the entry price and the June marks are
    # arithmetic on them, and both are recomputed here rather than transcribed from the note.
    j = na.series_j(d)
    dec = j[j.period.astype(str) == "2025-12-31"]
    entry = float(dec.entry_pps.dropna().unique()[0])
    add("3", "Series J entry price per share", entry, 92.50, 0.005, "**$92.50**", ["draft"])
    add("3", "Series J year-end mark per share", float(dec.mark_pps.dropna().unique()[0]),
        190.00, 0.005, "**$190.00**", ["draft"])
    add("3", "Series J filers printing one ratio at 31 December 2025", len(dec), 4, 0, None)
    add("3", "Series J year-end value/cost ratio", float(dec.ratio.max()), 76 / 37, 1e-6,
        "2.054054054", ["draft"])
    # Both filers that disclose a share count print the same entry price, which is what fixes
    # WHICH pair the common ratio is: equal ratios alone prove only proportionality.
    add("3", "Series J disclosed entry prices agree", float(dec.entry_pps.dropna().std()),
        0.0, 1e-6, None)
    jun = j[j.period.astype(str) == "2025-06-30"]
    hi, lo = entry * float(jun.ratio.max()), entry * float(jun.ratio.min())
    add("3", "Series J implied price at 30 June 2025, higher book", hi, 119.19, 0.01,
        "**$119.19**", ["draft"])
    add("3", "Series J implied price at 30 June 2025, lower book", lo, 108.18, 0.01,
        "**$108.18**", ["draft"])
    add("3", "Series J spread at 30 June 2025 (%)", (hi / lo - 1) * 100, 10.2, 0.05,
        "a 10.2% spread", ["draft"])
    # §4.2's lot-spanning qualification. All three figures were in the prose and none was
    # registered, which is the registry's blind direction: it requires every registered figure
    # to appear in the paper and says nothing about a figure typed into the paper and never
    # registered. `within_house` already computed both halves; only the pinning was missing.
    _wh, _wb = na.within_house(d), na.within_house(d, single_lot=False)
    add("4.2", "largest within-house spread, blended rows included (pts)",
        float(_wb.spread_pts.max()), 13.8, 0.05, "by as much as 13.8 points", ["draft"])
    add("4.2", "largest within-house spread, single-lot rows only (pts)",
        float(_wh.spread_pts.max()), 1.2, 0.05, "from 13.8 points to 1.2", ["draft"])
    # The prose said "four ten-thousandths". It is one: 0.000109. That error survived because
    # the figure had never been registered, which is the whole argument for registering the
    # other two beside it.
    add("4.2", "median within-house spread, single-lot rows (pts)",
        float(_wh.spread_pts.median()), 0.0001, 0.00005,
        "a median of 0.0001 of a point", ["draft"])
    # §2.3's one single-pair sentence. It read "12%" against a computed 12.45, which rounds
    # the wrong way and understates the only number in that paragraph doing any work. It was
    # unregistered, which is why nothing objected.
    _gu = fm.load()
    _gu = _gu[_gu.company == "Gusto"]
    _gu = _gu[_gu.report_date == _gu.report_date.mode().iloc[0]]
    _gf = _gu.groupby("family").pps.median()
    add("3.3", "Gusto: Fidelity against T. Rowe on the modal date (%)",
        (_gf["T. Rowe Price"] / _gf["Fidelity"] - 1) * 100, 12.45, 0.02, "is 12.5%", ["draft"])


def _dynamic(add) -> None:
    """§8 — the event study, pinned against the committed statistics file.

    These are read from `data/round_event_study_stats.csv` rather than recomputed, because the
    statistics behind them take a minute and a half of permutation work and the guard runs on
    every commit. The staleness that a committed artifact would otherwise let in is closed on
    the other side: the file carries a content hash of the marks file and of every design
    constant, and `test_the_committed_statistics_match_the_current_design` fails if it drifts.
    """
    import round_event_study as res
    s = res.load_stats()
    # Table 7's own cells. The profile is the one thing this module commits to disk as a table,
    # so the three months the prose calls out are pinned to that file rather than retyped.
    prof = pd.read_csv(ROOT / "data" / "round_event_study.csv").set_index("m")
    add("8", "pooled median at the round month (%)", prof.pooled_median[0], 0.01, 0.005,
        "| 0 | 46 | 29 | 0.01% |", ["draft"])
    add("8", "pooled median one month after (%)", prof.pooled_median[1], 0.00, 0.005,
        "| 1 | 35 | 20 | 0.00% |", ["draft"])
    add("8", "pooled median two months after (%)", prof.pooled_median[2], 0.46, 0.005,
        "| 2 | 33 | 21 | 0.46% |", ["draft"])
    add("8", "cells in the symmetric window", s["cells"], 462, 0, "462 guarded cells", ["draft"])
    add("8", "companies in the symmetric window", s["companies"], 43, 0, None)
    add("8", "cells if first rounds are kept", s["cells_with_first_rounds"], 858, 0,
        "858 cells on 123 companies", ["draft"])
    add("8", "median spread before the round (%)", s["step_median_pre"], 5.22, 0.01,
        "median **5.22%** before", ["draft"])
    add("8", "the step at zero (pts)", s["step_pts"], -2.52, 0.01,
        "a step of **−2.52 points**", ["draft"])
    # The README restates this count and it went stale there when the tie tolerance moved it
    # from 24 of 30; the registry now requires both copies, with the README's own wording.
    add("8", "companies narrower after / untied", s["step_narrower_after"], 22, 0,
        "narrower after in 22 of 29 untied companies", ["draft"],
        {"readme": "narrower afterwards in 22 of 29 companies"})
    add("8", "sign test on the step", s["step_p_sign"], 0.0041, 0.00005,
        "sign test p=0.0041", ["draft"])
    add("8", "share of phase-null draws matching the step", s["step_null_share"], 0.0, 0.0,
        "**0 of 400**", ["draft"])
    add("8", "near-far statistic (pts)", s["nearfar_pts"], -7.77, 0.01, "−7.77 points", ["draft"])
    add("8", "share of phase-null draws matching near-far", s["nearfar_null_share"] * 100,
        31, 0.5, "reproduced by 31% of random anchor placements", ["draft"])
    add("F.1", "round-month cells", s["round_month_cells"], 46, 0,
        "the 46 round-month cells", ["draft"])
    add("F.1", "median share of the round-month cell that is the new series (%)",
        s["new_series_share_median"] * 100, 26, 0.5, "a median 26% of the rows", ["draft"])
    add("F.1", "round-month cells that are entirely the new series",
        s["round_month_cells_all_new_series"], 0, 0, None)
    add("F.1", "median houses per cell before the round", s["width_houses_pre"], 4.0, 0.01,
        "**4.0 before the round against 4.0 after**", ["draft"])
    add("F.1", "Mann-Whitney p on cell width", s["width_mwu_p"], 0.60, 0.01,
        "Mann–Whitney p=0.60", ["draft"])
    add("8", "rebuild slope (pts/month)", s["rebuild_slope"], 1.11, 0.01,
        "+1.11 points a month", ["draft"])
    # §8.6 states the rebuild slope with its sign test and its denominator, and only the slope
    # was pinned. All three came out of `stats()` already; the omission was the pinning, which
    # is the direction `tests/test_prose_statistics_are_registered.py` bounds.
    add("8", "rebuild: companies rising", s["rebuild_rising"], 24, 0,
        "rising in 24 of 36 companies", ["draft"])
    add("8", "rebuild: companies measured", s["rebuild_companies"], 36, 0, None)
    add("8", "rebuild: sign p", s["rebuild_p_sign"], 0.033, 0.002, "sign p=0.033", ["draft"])
    add("8", "phase-null median slope (pts/month)", s["rebuild_null_median"], 0.05, 0.01,
        "+0.05 points a month", ["draft"])
    # The p-value the slope is cleared against. `rebuild_null()` returned it and `stats()`
    # exported it, and §8.6 quoted it, and nothing pinned it: it was reachable only because
    # "4%" happened to sit inside "42.4%" elsewhere in the registry. That is a p-value in the
    # body of the paper with no check behind it, which is what the boundary match in
    # `test_paper_consistency.py::test_no_bold_figure_in_section_5_escapes_the_registry` was
    # tightened to surface.
    add("8", "phase-null share at least as extreme", s["rebuild_null_share"] * 100, 4.0, 0.5,
        "4% of random placements", ["draft"])
    add("8", "multi-round events", s["multi_events"], 30, 0,
        "30 rounds on 12 companies", ["draft"])
    add("8", "multi-round median step (pts)", s["multi_step_pts"], -8.81, 0.01,
        "Median step −8.81 points", ["draft"])
    add("8", "multi-round sign p", s["multi_p_sign"], 0.0012, 0.0002,
        "sign test p=0.0012", ["draft"])
    # §8.4's decomposition, on cells carrying three houses or more. At two houses the median is
    # the midpoint, both gaps are one number, and the table would print the spread twice; the
    # bar is identification, not robustness, and `tests/test_round_event_study.py` measures the
    # identity it removes. The top house narrowing is the half good news cannot produce, and
    # the three placebo rows are what separate it from the mean reversion §G.3 warns about.
    # The bottom-house column is registered because it is printed, NOT because it is a result:
    # it does not clear five percent at the round and §8.4 says so in as many words.
    add("8", "two-sided: top house narrows at the round", s["twosided_+0_top_narrowed"], 29, 0,
        "| the round itself | 42 | 29 / 34 |", ["draft"])
    add("8", "two-sided: top house untied at the round", s["twosided_+0_top_untied"], 34, 0, None)
    add("8", "two-sided: top house sign p at the round", s["twosided_+0_top_p_sign"],
        1.9e-05, 3e-06, None)
    add("8", "two-sided: bottom house narrows at the round", s["twosided_+0_bottom_narrowed"],
        23, 0, "23 / 37 | 0.094 |", ["draft"])
    add("8", "two-sided: bottom house sign p at the round", s["twosided_+0_bottom_p_sign"],
        0.0939, 0.002, None)
    add("8", "two-sided: top house narrows six months before",
        s["twosided_-6_top_narrowed"], 14, 0, "| six months earlier | 31 | 14 / 22 |", ["draft"])
    # §8.4 quotes this p in prose, against the round's, to say the nearest placebo leans the
    # same way without clearing five percent. It was the one number I added last round and did
    # not pin, which is the defect `tests/test_prose_statistics_are_registered.py` now bounds.
    add("8", "two-sided: top house sign p six months before",
        s["twosided_-6_top_p_sign"], 0.143, 0.002, "p=0.143", ["draft"])
    add("8", "two-sided: top house narrows six months after",
        s["twosided_+6_top_narrowed"], 14, 0, "| six months later | 43 | 14 / 30 |", ["draft"])
    add("8", "two-sided: top house narrows twelve months after",
        s["twosided_+12_top_narrowed"], 10, 0,
        "| a year later | 32 | 10 / 24 |", ["draft"])
    # The three placebo anchors pooled. §8.4 quotes this instead of claiming the top-house
    # movement is "absent at all three", which the six-month-before anchor contradicts on its
    # own at 14 of 22.
    add("8", "two-sided: top house narrows, three placebos pooled",
        s["twosided_placebo_top_narrowed"], 38, 0, "38 of 76 untied anchors", ["draft"])
    add("8", "two-sided: untied anchors, three placebos pooled",
        s["twosided_placebo_top_untied"], 76, 0, None)
    # The share of cells the decomposition can speak about at all, quoted in §8.4 as the price
    # the identification bar charges.
    add("8", "share of cells carrying three houses or more",
        s["side_identified_cell_pct"], 60.5, 0.1,
        "60.5% of the panel's guarded cells", ["draft"])
    # Registered separately from its own complement because Appendix C.5 quotes the two-house
    # share while §8.4 quotes the identified share, and an unregistered complement is exactly
    # the kind of figure that survives a change to the panel by not being recomputed.
    add("C", "share of cells carrying exactly two houses",
        s["side_two_house_cell_pct"], 39.5, 0.1,
        "39.5% of cells carry exactly two houses", ["draft"])
    add("8", "placebo at +6 months, negative", s["placebo_+6_negative"], 17, 0,
        "| six months after | 49 | 35 | 0.000 | 17 / 41 | 0.894 |", ["draft"])
    add("8", "placebo at +12 months, negative", s["placebo_+12_negative"], 13, 0,
        "| twelve months after | 37 | 29 | 0.000 | 13 / 31 | 0.859 |", ["draft"])
    # The ladder rung that carries the paper's stated limit. Rung 4 is "drop the two-house bar".
    add("8", "widest-selection events", s["ladder4_events"], 103, 0,
        "| drop the two-house bar | 103 |", ["draft"])
    add("8", "widest-selection negative", s["ladder4_negative"], 55, 0,
        "55 of 93 untied anchors", ["draft"])
    add("8", "widest-selection sign p", s["ladder4_p_sign"], 0.048, 0.001,
        "p=0.048", ["draft"])
    add("8", "down rounds", s["updown_down_events"], 7, 0,
        "| down | 7 |", ["draft"])
    add("8", "up rounds", s["updown_up_events"], 43, 0, "| up | 43 |", ["draft"])


def _instruments(add) -> None:
    """§9 — the four filing-derived sensors."""
    import round_dates as rdt
    import split_events as se
    r = rdt.summary()
    add("E.3", "share of population rows naming a series letter (%)",
        r["letter_row_share_pct"], 32.5, 0.1,
        "**32.5%** of population rows carry a letter", ["draft"])
    add("8.5", "company-series pairs carrying a letter", r["series_pairs"], 5885, 0,
        "**5,885** company-series pairs", ["draft"])
    add("9", "dated pairs", r["dated_pairs"], 434, 0,
        "**434 company-series pairs on 287 companies**", ["draft"])
    # The pool §8.6's repetition test draws from, and the reason it is registered. Appendix E.3
    # said 23 companies with three or more dated rounds and §8.7 said 21; the truth is 24. One
    # quantity, two statements, neither of them right and nothing able to notice, because a
    # figure that reaches the prose without an `add` is checked by nothing in either direction.
    _per_co = rdt.first_seen()
    _per_co = _per_co[_per_co.dated].groupby("company").size()
    add("E.3", "companies with two or more dated rounds", int((_per_co >= 2).sum()), 97, 0,
        "Ninety-seven companies carry two or more dated rounds", ["draft"])
    add("E.3", "companies with three or more dated rounds", int((_per_co >= 3).sum()), 24, 0,
        "24 carry three or more", ["draft"])
    # Table 11's coordination-rule column. It lived only in a note, hand-computed, and its
    # count-rule neighbour kept a pre-tolerance p-value for two rounds because nothing here
    # recomputed either half. Both halves are registered now.
    import round_event_study as res
    _co = rdt.coordination_dated()
    _co_nonfirst = res._one_row_per_anchor(_co[_co.dated])
    _co_steps = res._steps_for(_co_nonfirst)
    add("E.3", "coordination rule: pairs dated", len(_co), 406, 0,
        "| pairs dated | 434 | 406 (333 uncensored) |", ["draft"])
    # These two said "8.4" until the section that number named was renumbered out from under
    # them by an insertion. Both carry no claim, so the locality guard never looked at them and
    # the mislabelling was silent. `test_a_topic_is_not_split_across_sections` is what sees it.
    add("E.3", "coordination rule: uncensored pairs", int(_co.dated.sum()), 333, 0, None)
    add("E.3", "coordination rule: non-first anchors", len(_co_nonfirst), 56, 0,
        "| non-first anchors | 75 | 56 |", ["draft"])
    add("E.3", "coordination rule: step on the non-first set (pts)",
        float(np.median(_co_steps)), -0.06, 0.005, None)
    add("E.3", "coordination rule: sign p", float(_binomtest(
        res._neg(_co_steps), res._untied(_co_steps), alternative="greater").pvalue),
        0.022, 0.001, "| step on the non-first set | \u22121.94, p=0.0008 | \u22120.06, p=0.022 |",
        ["draft"])
    add("9", "dated companies", r["dated_companies"], 287, 0, None)
    add("E.3", "calibration pairs inside the tolerance", r["inside_tolerance"], 14, 0,
        "**Fourteen of fifteen dated pairs land inside 35 days", ["draft"])
    add("E.3", "median calibration gap (days)", r["median_gap_days"], 16, 0,
        "the median gap is 16", ["draft"])
    add("E.3", "worst gap inside the tolerance (days)", r["worst_inside"], 33, 0,
        "the worst inside the tolerance is 33", ["draft"])
    add("E.3", "nearest gap outside the tolerance (days)", r["nearest_outside"], 59, 0,
        "the nearest outside it is 59", ["draft"])
    lag = se.restatement_lag()
    add("E.2", "confirmed split events", lag["events"], 29, 0,
        "confirms **29 events** by two or more houses", ["draft"])
    add("E.2", "split events at a canonical ratio", lag["events_at_a_canonical_ratio"], 26, 0,
        "**26** of them at a ratio companies actually split at", ["draft"])
    add("F.3", "median restatement span (days)", lag["median_span_days"], 30, 0,
        "median restatement span is **30 days**", ["draft"])
    add("F.3", "longest restatement span (days)", lag["max_span_days"], 92, 0,
        "the longest is **92**", ["draft"])
    add("F.3", "split events fitting inside one month", lag["events_inside_one_month"], 18, 0,
        "only **18 of 29** fit inside a single month", ["draft"])
    add("F.3", "registrant inflation factor at the median event",
        lag["houses_inflated_by_counting_registrants"], 1.7, 0.05,
        "multiplies the count by **1.7×**", ["draft"])
    g = se.guard_overlap()
    add("E.2", "cells dropped by the 4x guard", g["cells_dropped_by_guard"], 1945, 0,
        "The guard drops 1,945 cells", ["draft"])
    add("E.2", "guard drops inside a restatement window", g["inside_a_restatement_window"], 22, 0,
        "**22 of them (1.1%)** sit inside a restatement window", ["draft"])


def _population(add) -> None:
    """§5, the population panel. Every figure here comes off one cached build of the bulk
    N-PORT file, so the section costs a single load rather than one per number.

    Families are fund COMPLEXES, not registrants. The registrant-level figures are also
    pinned, because §5.1 quotes them as the lower bound on the correction."""
    import population as pop
    import reconcile_versions as rv
    import entity_resolution as _er
    import fund_complex as fx

    d, c = pop.panel()
    g = c[c.guarded]
    k = pop.concentration(c)
    per = pop.persistence(c)
    hp = pop.house_policy(d, c)
    hz = pop.size_effect_by_horizon(c).set_index("dates")

    # -- 5.2 what the harvest contains ---------------------------------------------------
    add("5.2", "population marks harvested", len(d), 309654, 0, "309,654", ["draft", "readme"])
    add("5.2", "distinct issuer strings", d.ISSUER_NAME.nunique(), 15443, 0, "15,443", ["draft", "readme"])
    add("5.2", "US-domiciled marks", (d.INVESTMENT_COUNTRY == "US").sum(), 200002, 0,
        "200,002", ["draft"])
    add("5.2", "bulk data sets downloaded", d.src_quarter.nunique(), 27, 0, None)
    _rec = rv.compare().set_index("company")
    add("5.2", "Revolut spread recovered without the restricted flag (%)",
        _rec.loc["Revolut", "bulk_spread"], 34.7, 0.15, "34.7%", ["draft"])

    # -- 5.3 identity ---------------------------------------------------------------------
    add("5.3", "feeder rows held out of price comparison", int(d.is_wrapper.sum()), 262, 0,
        "262 feeder rows", ["draft"])
    add("5.3", "hand-written alias entries", len(_er.ALIASES), 13, 0, "**thirteen**", ["draft"])

    # -- 5.4 the family unit ----------------------------------------------------------------
    x = pop.comparable(d)
    _keys = set(zip(g.company, g.dt))
    xc = x[[kk in _keys for kk in zip(x.company, x.dt)]]
    # Counted over the whole harvest rather than the cell subset: the claim is about how a
    # house files, not about which of its trusts happen to clear the five-fund bar.
    for house, n_cik, tok in [("Fidelity", 36, "**36**"), ("T. Rowe Price", 40, "40"),
                              ("BlackRock", 56, "56")]:
        add("5.4", f"registrant CIKs used by {house}",
            d[d.house == house].CIK.nunique(), n_cik, 0, tok, ["draft"])
    add("5.4", "share of cell NAV mapped to a named house (%)",
        xc[xc.house.isin(set(fx.RULES and [n for _, n in fx.RULES]))].val_usd.sum()
        / xc.val_usd.sum() * 100, 98, 1, "**98%**", ["draft"])
    # The share of multi-fund house groups filing one identical price is registered once, at
    # §5.10, where `population.house_policy` computes it. It used to be registered here too,
    # recomputed inline, and the two entries carried different expected values — 89.0 with a
    # 0.2 tolerance here, 88.8 with a 0.3 tolerance there — whose bands straddled the true
    # 89.0119% from opposite sides. Both passed, three places in the shipped text printed the
    # stale 88.8%, and the registry's whole purpose was defeated by having two of them.
    # `tests/test_paper_consistency.py::test_no_two_entries_compute_the_same_number_differently`
    # now fails on that pattern.
    _wr = xc.groupby(["company", "dt", "CIK"]).pps.agg(["min", "max", "size"])
    _wr = _wr[_wr["size"] > 1]
    add("5.4", "multi-fund groups identical within a registrant (%)",
        float(((_wr["max"] / _wr["min"]) <= 1.0001).mean() * 100), 87.5, 0.2,
        "87.5%", ["draft"])

    # -- 5.5 the distribution --------------------------------------------------------------
    add("5.5", "report dates in the harvest", d.dt.nunique(), 104, 0,
        "104 distinct report dates", ["draft"])
    # Claim instruments: an issuer identifier joins a CVR or an escrow line to the stock, and
    # their prices have nothing to say to each other. Counted so the exclusion is a number a
    # reader can check rather than a sentence.
    _nc = d[~d.is_wrapper & (d.INVESTMENT_COUNTRY != "RU")]
    add("5.3", "claim-instrument rows excluded", int(pop.is_claim(_nc).sum()), 25482, 0,
        "**25,482**", ["draft"])
    add("5.3", "companies touched by a claim instrument",
        int(d[pop.is_claim(d)].company.nunique()), 1599, 0, "1,599", ["draft"])
    # The guard removes a third of the qualifying cells at house level. That is large enough
    # that a reader should see it rather than discover it in the code.
    add("5.5", "share-class guard drop rate, house level (%)",
        (1 - len(g) / len(c)) * 100, 31, 1, "**31%**", ["draft"],
        # §6 quotes the same figure in its own words; it was left at 33% through the rebuild
        # that moved it, so both mentions are pinned rather than only the one in §5.1.
        {"draft": "guard discards **31%** of otherwise qualifying"})
    _cr_all = pop.cells(d, family="CIK")
    add("5.5", "share-class guard drop rate, registrant level (%)",
        (1 - len(_cr_all[_cr_all.guarded]) / len(_cr_all)) * 100, 22, 1, "against 22%", ["draft"])
    add("5.5", "report dates yielding a cell", g.dt.nunique(), 92, 0, "of which 92 yield", ["draft"])
    add("5.5", "population cells", k["cells"], 4271, 0, "4,271", ["draft", "readme", "caption"])
    add("5.5", "population companies", k["companies"], 656, 0, "656",
        ["draft", "readme", "caption"])
    add("5.5", "cells with an identical mark (%)", k["identical_pct"], 17.0, 0.2,
        "17.0%", ["draft", "readme"])
    add("5.5", "cells agreeing within a basis point (%)", k["within_1bp_pct"], 28.4, 0.2,
        "28.4%", ["draft", "readme"])
    add("5.5", "population median spread (%)", k["median"], 12.1, 0.1, "12.1%",
        ["draft", "readme", "caption"])
    add("5.5", "population p75 spread (%)", k["p75"], 49.5, 0.2, "49.5%", ["draft"])
    add("5.5", "population p90 spread (%)", k["p90"], 120.7, 0.3, "120.7%", ["draft"])
    add("5.5", "cells above 24% (%)", k["share_above_24"], 40.2, 0.2, "40.2%", ["draft", "readme"])
    add("5.5", "percentile at which 24% sits",
        float((g.spread_pct < 24).mean() * 100), 60, 1, "**60th percentile**",
        ["draft", "readme"], {"caption": "sits at the 60th "})
    _co_med = g.groupby("company").spread_pct.median()
    add("5.5", "companies whose median spread exceeds 24% (%)",
        (_co_med > 24).mean() * 100, 32.5, 0.2, "**32.5%**", ["draft"])
    # the registrant-level bound the section quotes so the correction is bounded from below
    # The ten §7.1 cells scored the population's own way, so the percentile compares like
    # with like: 24% is a spread across funds, this is a spread across house medians.
    import robustness as _rb
    _clean, _ = _rb.clean_fund_table(3.0)
    _tf, _th = [], []
    for _co in _clean.company.unique():
        _sd = _rb._modal_slice(_clean, _co)
        if _sd.fund.nunique() < 5:
            continue
        _h = _sd.groupby("family").pps.median()
        _tf.append((_sd.pps.max() / _sd.pps.min() - 1) * 100)
        _th.append((_h.max() / _h.min() - 1) * 100 if len(_h) > 1 else 0.0)
    _mh = float(np.median(_th))
    add("5.5", "ten §4.3 cells scored between houses (%)", _mh, 23.7, 0.15, "**23.7%**", ["draft"])
    add("5.5", "percentile of the house-level ten-name median",
        float((g.spread_pct < _mh).mean() * 100), 60, 1, "**60th percentile**", ["draft"])
    _cr = pop.cells(d, family="CIK")
    _kr = pop.concentration(_cr)
    # §5.4 rather than §5.1: the duplicate statement in §5.1 was cut, and this figure is
    # now stated only where the paper says which of its three medians to quote.
    add("5.4-current", "registrant-level median spread (%)", _kr["median"], 0.004, 0.003,
        "0.004%", ["draft"])
    add("5.5", "registrant-level percentile of 24%",
        float((_cr[_cr.guarded].spread_pct < 24).mean() * 100), 75, 1, "75th percentile", ["draft"])

    # Table 11 rows, bucketed once in population.spread_buckets so the table, the figure and
    # this registry cannot disagree about a cell sitting exactly on an edge.
    want = {"identical": (725, 80.2, 15.5), "0-10%": (1300, 168.7, 32.6),
            "10-24%": (531, 88.4, 17.1), "24-50%": (660, 105.9, 20.5),
            "50-100%": (499, 51.0, 9.9), ">100%": (556, 23.0, 4.4)}
    for _, row in pop.spread_buckets(g).iterrows():
        n_cells, nav_b, nav_pct = want[row.bucket]
        add("5.5", f"Table 11 {row.bucket}: cells", row.cells, n_cells, 0,
            f"| {n_cells:,} |", ["draft"])
        add("5.5", f"Table 11 {row.bucket}: NAV ($B)", row.nav_busd, nav_b, 0.06,
            f"| {nav_b} |", ["draft"])
        # The >100% band's share of value is quoted a second time in 5.7's prose. That
        # duplicate is exactly the kind that outlived a rebuild in section 6, so where a
        # bucket figure is restated in words the restatement is pinned too.
        _ctx = {"draft": f"**{nav_pct}%** of the value"} if row.bucket == ">100%" else {}
        add("5.5", f"Table 11 {row.bucket}: share of NAV (%)", row.nav_pct, nav_pct, 0.06,
            f"| {nav_pct}% |", ["draft"], _ctx)
        # The share-of-cells column, which was the one column of this table nothing checked.
        # §5.3 restates the >100% band's share in prose, so that restatement is pinned too.
        _cp = {"identical": 17.0, "0-10%": 30.4, "10-24%": 12.4, "24-50%": 15.5,
               "50-100%": 11.7, ">100%": 13.0}[row.bucket]
        _cctx = ({"draft": "more than 100% are 13.0% of the count"}
                 if row.bucket == ">100%" else {})
        add("5.5", f"Table 11 {row.bucket}: share of cells (%)", row.cells_pct, _cp, 0.06,
            f"| {_cp}% |", ["draft"], _cctx)

    # -- 5.1 what the headline median is made of ------------------------------------------
    # A referee recomputed the panel by house count and found the 12.1% is a mixture: 1,685 of
    # the 4,271 guarded cells hold exactly two houses at a median of 0.94%, and six-house cells
    # sit at 29.63%. The paper's own Appendix H.1 already says why — the spread is a maximum
    # over a minimum and grows with the count — but used it only to defend §8. Every cell of
    # both new tables is registered, because the last table that was not had two stale rows.
    import coverage_regimes as _cov
    _cg = _cov.coverage_gradient(d, c)
    _cgi = _cg.set_index("band")
    _CG = {2: (1685, 343, 0.94, 0.94, 26.2, 113.2),
           3: (971, 233, 17.64, 15.38, 44.2, 94.8),
           4: (630, 173, 20.57, 10.68, 47.5, 79.1),
           5: (370, 114, 29.16, 4.71, 55.1, 50.6),
           6: (615, 142, 29.63, 2.84, 55.6, 179.5)}
    # Wrapped in a function, and that is not style. A `for` target leaks into the enclosing
    # scope, this builder is thirteen hundred lines long, and its locals are all `_x`. The
    # first version of this loop bound `_mh`, which line 1017 had already set to the ten-name
    # house-level median and line 1379 reads back — so a table of mean house counts silently
    # replaced a median 276 lines away and the C.2 percentile came out 40.8 instead of 63.
    # The registry's own code-drift check caught it, which is the only reason it is not in the
    # paper. Nothing here escapes now.
    def _add_bands() -> None:
        for band, (ce, co, ms, mp, a24, nv) in _CG.items():
            r = _cgi.loc[band]
            add("5.5-mix", f"coverage band {band}: cells", r.cells, ce, 0, f"| {ce:,} |", ["draft"])
            add("5.5-mix", f"coverage band {band}: companies", r.companies, co, 0, f"| {co} |",
                ["draft"])
            add("5.5-mix", f"coverage band {band}: median spread (%)", r.median_spread, ms, 0.005,
                f"| {ms:.2f}% |", ["draft"])
            add("5.5-mix", f"coverage band {band}: median pair (%)", r.median_pairwise, mp, 0.005,
                f"| {mp:.2f}% |", ["draft"])
            add("5.5-mix", f"coverage band {band}: above 24% (%)", r.above_24, a24, 0.05,
                f"| {a24:.1f}% |", ["draft"])
            add("5.5-mix", f"coverage band {band}: booked NAV ($B)", r.nav_busd, nv, 0.05,
                f"| {nv:.1f} |", ["draft"])
    _add_bands()

    # The four figures §5.1's prose states in words, which is where drift would land.
    add("5.5-mix", "two-house cells", _cgi.loc[2, "cells"], 1685, 0, "1,685 of the 4,271", ["draft"])
    add("5.5-mix", "two-house NAV ($B)", _cgi.loc[2, "nav_busd"], 113.2, 0.05, "$113.2B", ["draft"])
    add("5.5-mix", "two-house median spread (%)", _cgi.loc[2, "median_spread"], 0.94, 0.005,
        "median spread is 0.94%", ["draft"])
    add("5.5-mix", "six-house median spread (%)", _cgi.loc[6, "median_spread"], 29.63, 0.005,
        "sit at 29.63%", ["draft"])

    _ps = _cov.pairwise_spread(d, c)
    add("5.5-mix", "panel median pair (%)", _ps.pairwise_pct.median(), 5.88, 0.005,
        "median pair is 5.88%", ["draft"])
    add("5.5-mix", "panel pair above 24% (%)", float((_ps.pairwise_pct > 24).mean() * 100), 29.1,
        0.05, "puts 29.1% of cells", ["draft"])

    # -- 5.1 the calendar path ---------------------------------------------------------------
    _cp = _cov.calendar_path(c).set_index("year")
    _CP = {2019: (191, 8.22, 4.14, 129, 12.50), 2020: (564, 10.68, 3.84, 356, 18.65),
           2021: (670, 4.82, 3.73, 408, 7.06), 2022: (735, 13.30, 3.72, 448, 26.78),
           2023: (659, 17.45, 3.58, 395, 33.29), 2024: (609, 18.04, 3.49, 359, 32.00),
           2025: (643, 17.42, 3.45, 373, 29.80), 2026: (200, 11.10, 3.40, 118, 17.45)}
    def _add_years() -> None:
        for yr, (ce, ms, mh, c3, m3) in _CP.items():
            r = _cp.loc[yr]
            add("5.5-cal", f"{yr}: cells", r.cells, ce, 0, f"| {yr} | {ce} |", ["draft"])
            add("5.5-cal", f"{yr}: median spread (%)", r.median_spread, ms, 0.005,
                f"| {ms:.2f}% |", ["draft"])
            add("5.5-cal", f"{yr}: mean houses", r.mean_houses, mh, 0.005, f"| {mh:.2f} |",
                ["draft"])
            add("5.5-cal", f"{yr}: cells with 3+ houses", r.cells_3plus, c3, 0, f"| {c3} |",
                ["draft"])
            add("5.5-cal", f"{yr}: median spread, 3+ houses (%)", r.median_3plus, m3, 0.005,
                f"| {m3:.2f}% |", ["draft"])
    _add_years()

    # The path as §5.1 states it in prose.
    add("5.5-cal", "2021 trough (%)", _cp.loc[2021, "median_spread"], 4.82, 0.005,
        "falls to 4.82% in 2021", ["draft"])
    add("5.5-cal", "mean houses 2019", _cp.loc[2019, "mean_houses"], 4.14, 0.005,
        "from 4.14 to 3.45", ["draft"])

    # -- 5.1 what an outlier is, and whether it is a house -----------------------------------
    # The inversion says a wide cell is a consensus plus a dissenter. That is testable and the
    # referee was right that it stops being optional once the inversion is printed: if the
    # dissenter is the same house next quarter, disagreement is a standing position.
    _ol = _cov.outlier_structure(d, c)
    # Cells with three or more houses AND a dissenter. 260 of the 2,586 have every house on
    # one price, so there is no furthest house to name and no direction to report; they were
    # being handed an arbitrary one by the tie-break, which is where the platform
    # sensitivity was worst.
    add("5.5-out", "cells with a dissenter", _ol["cells"], 2326, 0, "the 2,326 that have one",
        ["draft"])
    add("5.5-out", "cells where every house files one price", _ol["unanimous_cells"], 260, 0,
        "260 of the 2,586", ["draft"])
    # Arithmetic, like every other spread here. It was the raw log ratio, printed beside an
    # arithmetic 0.35% under one per-cent sign; 18.23 log points is 20.0%.
    add("5.5-out", "outlier deviation from the rest (%)", _ol["outlier_dev"], 25.54, 0.005,
        "median 25.54%", ["draft"])
    add("5.5-out", "outlier deviation, log points", _ol["outlier_dev_log_points"], 22.75,
        0.005, None)
    add("5.5-out", "spread among the houses the outlier leaves (%)", _ol["rest_spread"], 1.57,
        0.005, "1.57% apart at their widest", ["draft"])
    add("5.5-out", "outliers sitting above the rest (%)", _ol["above_pct"], 45.5, 0.05,
        "45.5% of outliers", ["draft"])
    add("5.5-out", "pairs where a repeat was possible", _ol["pairs"], 1334, 0,
        "1,334 consecutive pairs", ["draft"])
    add("5.5-out", "same house is the outlier again (%)", _ol["repeat_pct"], 65.07, 0.05,
        "outlier again in 65.1%", ["draft"])
    add("5.5-out", "resampled outlier null (%)", _ol["null_mean"], 25.39, 0.05,
        "null at 25.4%", ["draft"])
    add("5.5-out", "houses in a hundred or more such cells", _ol["houses"], 27, 0,
        "27 houses appearing", ["draft"])
    add("5.5-out", "outlier ratio, lowest house", _ol["ratio_min"], 0.08, 0.005, "0.08 to 2.36",
        ["draft"])
    add("5.5-out", "outlier ratio, highest house", _ol["ratio_max"], 2.36, 0.005, None)
    # Not quoted: the permutation's own ceiling, which is the sentence "no draw reached 30%".
    add("5.5-out", "highest of two thousand resampled draws (%)", _ol["null_max"], 29.61,
        0.05, None)

    # -- 6.1 company identity against house-pair identity ------------------------------------
    # The naive comparison favours the pair, and the artifact behind that is the finding: a
    # pair seen on one company IS that company. Both restrictions are registered so the paper
    # can print the trap as well as the answer.
    _pc = _cov.pair_vs_company(d, c)
    add("5.8", "house-pair observations", _pc["observations"], 31358, 0, "31,358 pairs",
        ["draft"])
    add("5.8", "distinct house pairs", _pc["pairs"], 3010, 0, "3,010 distinct pairs", ["draft"])
    add("5.8", "company share of pair variance (%)", _pc["company_share"] * 100, 29.0, 0.05,
        "reproduces 29.0% of the variance", ["draft"])
    add("5.8", "pair share of pair variance (%)", _pc["pair_share"] * 100, 35.2, 0.05,
        "pair identity 35.2%", ["draft"])
    add("5.8", "pairs on three or more companies", _pc["pairs_on_several_companies"], 754, 0,
        "the 754 pairs", ["draft"])
    add("5.8", "company share, pairs on 3+ companies (%)", _pc["company_share_restricted"] * 100,
        31.7, 0.05, "company reproduces 31.7%", ["draft"])
    add("5.8", "pair share, pairs on 3+ companies (%)", _pc["pair_share_restricted"] * 100,
        25.1, 0.05, "the pair 25.1%", ["draft"])

    # -- 6.2 the one place both escapes are shut ---------------------------------------------
    # The quiet cells answer staleness and leave composition open; the same-letter cells answer
    # composition and leave staleness open. Their intersection is the only subsample in the
    # paper where neither reading is available, and it is small enough that the count matters
    # more than the median.
    _nm = _cov.no_move_one_letter(d, c)
    add("5.9", "quiet and fully named: cells", _nm["both"], 132, 0, "132 cells on 40 companies",
        ["draft"])
    add("5.9", "quiet and fully named: companies", _nm["both_companies"], 40, 0, None)
    add("5.9", "quiet and fully named: not unanimous", _nm["both_nonzero"], 76, 0,
        "76 are not unanimous", ["draft"])
    add("5.9", "quiet and fully named: above 24%", _nm["both_above_24"], 6, 0,
        "six differ by more than 24%", ["draft"])
    add("5.9", "quiet and fully named: widest (%)", _nm["widest"], 232.9, 0.05,
        "the widest by 233%", ["draft"])
    # Not quoted: the two denominators the intersection is taken from. They are already in the
    # paper as §6.2's 760 and Table C.1's 366, and a third statement of either is a place for
    # them to disagree.
    add("5.9", "quiet cells, rebuilt outside the pinned module", _nm["quiet"], 760, 0, None)
    add("5.9", "fully named cells, rebuilt outside the pinned module", _nm["fully_named"], 366,
        0, None)

    # -- 4.1 the house map against Form N-CEN, an SEC source it never saw -------------------
    # Keyed "5.4", not "4.1". `SECTION_ALIASES` sends the literal "4.1" to `paper2`, because
    # before the reframe that number belonged to the secondary panel, and the pre-reframe key
    # for this paper's §4.1 is "5.4". Registering these under "4.1" filed eleven numbers in
    # the second paper's section space, where `test_registry_sections` does not look for
    # them: every one passed its value check and none was ever required to appear inside the
    # section that states it. The sibling entry two hundred lines above, §4.1's 87.5%, uses
    # "5.4" and is what this was checked against.
    # Reads the committed extract, so it runs offline like everything else here; the harvest
    # that wrote the extract needs a network and is not part of this pipeline. The reading of
    # the twenty-two split houses is pinned too, because "not one fuses two unrelated firms"
    # is a sentence about a set that the code recomputes on every run.
    import ncen_advisers as nc
    _nc = nc.compare()
    add("5.4", "registrants checked against N-CEN", _nc["registrants"], 1166, 0,
        "1,166 registrants", ["draft"])
    add("5.4", "registrants with an adviser named", _nc["with_adviser_ciks"], 1161, 0,
        "1,161 of the panel's", ["draft"])
    # Not quoted in the body: the §4.1 paragraph sits at the 150-word ceiling and these two
    # are the ones a reader does not need to follow the argument. They are recomputed on
    # every run and stated in `notes/ncen_validation.md`, which is where a reader who wants
    # the shape of the coverage goes.
    add("5.4", "houses the N-CEN adviser covers", _nc["houses_covered"], 655, 0, None)
    add("5.4", "multi-registrant houses", _nc["multi_registrant_houses"], 55, 0,
        "55 houses this map merges", ["draft"])
    add("5.4", "registrants naming several advisers",
        _nc["registrants_naming_several_advisers"], 69, 0, None)
    add("5.4", "houses filing more than one adviser", _nc["houses_with_two_advisers"], 22, 0,
        "22 file more than one adviser", ["draft"])
    add("5.4", "split houses that are one firm's entities",
        _nc["split_kinds"]["subsidiary"], 13, 0, "13 are one firm's", ["draft"])
    add("5.4", "split houses that are acquisitions", _nc["split_kinds"]["acquired"], 8, 0,
        "8 are firms the house bought", ["draft"])
    add("5.4", "split houses that delegate", _nc["split_kinds"]["delegated"], 1, 0,
        "1 is an outside manager", ["draft"])
    add("5.4", "advisers appearing under more than one house",
        _nc["advisers_split_across_houses"], 96, 0, "96 advisers appear", ["draft"])
    # Not quoted in the paper, and the reason the sentence above is safe to write: a split
    # house nobody has read, or a reading whose house no longer splits, is a defect.
    add("5.4", "split houses with no reading", len(_nc["unread_splits"]), 0, 0, None)
    add("5.4", "readings whose house no longer splits", len(_nc["stale_readings"]), 0, 0, None)

    # -- 5.6 the bound the filings put on security identification --------------------------
    _ss = pop.same_security(d, c)
    add("C.5", "cells naming at most one series or class", _ss["cells"], 2897, 0, "2,897", ["draft"])
    add("C.5", "companies in the one-series panel", _ss["companies"], 606, 0, "606", ["draft"])
    add("C.5", "median spread, one-series panel (%)", _ss["median"], 11.6, 0.1, "**11.6%**", ["draft"])
    add("C.5", "above 24%, one-series panel (%)", _ss["share_above_24"], 39.9, 0.2, "39.9%", ["draft"])
    # This entry is the other half of the Table C.1 defect, and it shows the tolerance was as
    # much to blame as the missing pin. `same_security["mixed_median"]` and
    # `series_composition["mixed"]["median"]` return the same float to the last bit — one
    # quantity, two expressions — and it is 12.8968. Pinned at 12.88 with a tolerance of 0.02
    # the value check passed by 0.0032, so the only thing that could have caught the stale
    # table was the token, and the token agreed with the stale table. Tightened to the
    # precision the paper prints.
    add("2.3", "median spread where two or more letters appear (%)", _ss["mixed_median"], 12.90,
        0.005, "12.90%", ["draft"])
    # The counter-example the section leans on: the most widely held private company is held
    # almost entirely on letter-mixed cells and the houses still file one price.
    add("2.3", "SpaceX letter-mixed cells", _ss["spacex_cells"], 32, 0, "32 letter-mixed cells",
        ["draft"])
    add("5.6", "SpaceX letter-mixed median spread (%)", _ss["spacex_median"], 0.0, 0.001, None)

    # -- 5.6b what kind of company is on the other side of the mark ------------------------
    _cls = ccl.classify()
    _tot = ccl.totals(_cls).set_index("label")
    _acc = ccl.rule_accuracy(_cls)
    _ic = ccl.issuer_counts(_cls)
    _mm = ccl.mismatch_stats()
    # The cluster-by-cluster arithmetic is Appendix C.2's, not §5.2's. It was in both until the
    # assembler was found lifting one source line into two sections, so §5.2 ran the long
    # version and then summarised it in the next breath. §5.2 keeps only the share, which is
    # the part a reader of the body needs.
    add("C.2", "clusters with a verified label", int((_cls.basis == "verified").sum()), 118, 0,
        "**118**", ["draft"])
    add("5.6", "share of booked value carrying a verified label (%)",
        float(_cls[_cls.basis == "verified"].nav.sum() / _cls.nav.sum() * 100), 93.6, 0.2,
        "**93.6%**", ["draft"])
    add("C.2", "clusters labelled by rule", int((_cls.basis == "rule").sum()), 390, 0,
        "390", ["draft"])
    add("C.2", "clusters left unclassified", int((_cls.basis == "unclassified").sum()), 147, 0,
        "147", ["draft"])
    add("C.2", "rule accuracy where it fires (%)", _acc["accuracy_where_fired"], 94, 1,
        "**94%**", ["draft"])
    add("C.2", "verified clusters the rule declines to call", _acc["rule_abstained"], 32, 0,
        "32 of them", ["draft"])
    # `unclassified` was outside this loop and outside the registry, so Table 12's fourth row
    # sat still through two panel rebuilds while the other three moved — and the table's own
    # column then summed to 4,297 cells and 660 clusters against §5.1's 4,271 and 656 on the
    # facing page. Adding a column is the first thing a referee does to a decomposition.
    # Every cell of Table 12 is registered now, and the row tokens are required in the draft.
    _T12 = {"venture": (142, 2113, 402.2, 10.1, 37.0, 152.8),
            "private_nonventure": (18, 314, 72.8, 16.1, 36.9, 17.0),
            "listed": (348, 967, 28.0, 19.0, 47.9, 4.8),
            "unclassified": (148, 877, 14.3, 10.6, 40.5, 5.3)}
    for _lab, _tok in [("venture", "venture"), ("private_nonventure", "non-venture"),
                       ("listed", "listed"), ("unclassified", "unclassified")]:
        r = _tot.loc[_lab]
        # Not `_co`: that name is a company key in the ten-name loop two hundred lines
        # above, and one loop target overwriting another is how the C.2 percentile came
        # out 40.8 instead of 63 once.
        _ncomp, _ncell, _nnav = _T12[_lab][:3]
        add("5.6", f"{_tok}: companies", r.companies, _ncomp, 0, None)
        add("5.6", f"{_tok}: cells", r.cells, _ncell, 0, None)
        add("5.6", f"{_tok}: booked NAV ($B)", r.nav_busd, _nnav, 0.1, None)
    _u = _tot.loc["unclassified"]
    add("5.6", "Table 12 unclassified: clusters", _u.companies, 148, 0, "| unclassified | 148 |",
        ["draft"])
    add("5.6", "Table 12 unclassified: cells", _u.cells, 877, 0, "| 877 |", ["draft"])
    add("5.6", "Table 12 unclassified: median spread (%)", _u.median_spread_pct, 10.6, 0.1,
        "| 10.6% |", ["draft"])
    add("5.6", "Table 12 unclassified: above 24% (%)", _u.above_24_pct, 40.5, 0.2, "| 40.5% |",
        ["draft"])
    # Table 12 has to sum to §5.1's panel, and that is a check rather than a coincidence.
    add("5.6", "Table 12 rows sum to the panel's cells", float(_tot.cells.sum()), 4271, 0, None)
    add("5.6", "Table 12 rows sum to the panel's clusters", float(_tot.companies.sum()), 656, 0,
        None)
    add("C.2", "clusters carried into the venture split", float(len(_cls)), 656, 0,
        "656 clusters", ["draft"])
    # §3.2's own summary of what its last two corrections cost. It was prose for three rounds
    # and drifted twice in silence; `population.correction_cost` recomputes it.
    _corr = pop.correction_cost(d)
    add("A.2", "cells the DUMMY and expiry corrections cost", float(_corr["cells"]), -15, 0,
        "costs fifteen cells", ["draft"])
    add("A.2", "points they move the population median", _corr["median_pts"], 0.34, 0.02,
        "a third of a point", ["draft"])
    add("5.3", "rows the two corrections remove", float(_corr["rows_removed"]), 3701, 0, None)
    # §3.3, rebuilt. The old bound restricted to cells naming fewer than two DIFFERENT letters
    # and read the gap to 12.1% as "the round-mixing objection is worth a third of a point".
    # The restriction passes two ways and only one fixes the security: the median share of
    # rows carrying any letter inside that subset is ZERO.
    #
    # This comment used to say every cell of the decomposition was registered. It was
    # false when it was written: `bound`, `unnamed` and `fully_named` were pinned and
    # `partial` and `mixed` were not, and the two unpinned bands are exactly the two
    # that went stale — Table C.1 shipped 591 and 1,373 against the 590 and 1,374 the
    # code returns, two cells swapping bands after the series-regex correction. Both
    # readings sum to 4,271, so the arithmetic audit passed as well. A claim that a
    # figure cannot drift from the prose holds only where the prose is pinned, and the
    # first release of the figures is what proved it. All five bands are pinned now.
    _sc = pop.series_composition(d, c)
    add("C.5", "old bound: cells", _sc["bound"]["cells"], 2897, 0, "2,897 cells", ["draft"])
    add("C.5", "old bound: median (%)", _sc["bound"]["median"], 11.61, 0.05, "11.6%", ["draft"])
    add("2.3", "median named-row share inside the old bound",
        _sc["median_named_share_in_bound"], 0.0, 0, None)
    add("C.5", "cells where no filing names a letter", _sc["unnamed"]["cells"], 1941, 0,
        "1,941 of them", ["draft"])
    add("C.5", "median spread, cells naming no letter (%)", _sc["unnamed"]["median"], 16.42, 0.05,
        "16.42%", ["draft"])
    add("C.5", "cells where every filing names the same letter",
        _sc["fully_named"]["cells"], 366, 0, "Only 366 pass", ["draft"])
    # The two bands that were not pinned, and were therefore the two that went stale. Every
    # cell of Table C.1 is a claim, so every cell of Table C.1 is registered: the count, the
    # company count, the median and the share above 24%, for both.
    add("C.5", "partial: cells", _sc["partial"]["cells"], 590, 0, "| 590 |", ["draft"])
    add("C.5", "partial: companies", _sc["partial"]["companies"], 92, 0, "| 92 |", ["draft"])
    add("C.5", "partial: median (%)", _sc["partial"]["median"], 15.34, 0.005, "15.34%",
        ["draft"])
    add("C.5", "partial: above 24% (%)", _sc["partial"]["above_24"], 42.4, 0.05, "42.4%",
        ["draft"])
    add("C.5", "mixed: cells", _sc["mixed"]["cells"], 1374, 0, "| 1,374 |", ["draft"])
    add("C.5", "mixed: companies", _sc["mixed"]["companies"], 107, 0, "| 107 |", ["draft"])
    # No entry for the mixed band's median here: it is the same float as §3.3's
    # `same_security["mixed_median"]`, which is pinned above, and one quantity gets one entry.
    add("C.5", "mixed: above 24% (%)", _sc["mixed"]["above_24"], 40.8, 0.05, "40.8%",
        ["draft"])
    # And five more the same guard found once it read the table instead of a list: the
    # company counts of two bands, their shares above 24%, and the panel median at the two
    # decimals Table C.1 prints it to. The referee found two stale cells; the reason two
    # could go stale is that seven were unpinned.
    add("C.5", "unnamed: companies", _sc["unnamed"]["companies"], 488, 0, "| 488 |", ["draft"])
    add("C.5", "unnamed: above 24% (%)", _sc["unnamed"]["above_24"], 43.8, 0.05, "43.8%",
        ["draft"])
    add("C.5", "fully named: companies", _sc["fully_named"]["companies"], 58, 0, "| 58 |",
        ["draft"])
    add("C.5", "fully named: above 24% (%)", _sc["fully_named"]["above_24"], 14.8, 0.05,
        "14.8%", ["draft"])
    # The panel median is pinned in §5.5 as "12.1%", which is the token the body uses. Table
    # C.1 prints the same quantity to two decimals, and a token is matched literally, so
    # "12.1%" pins nothing about the table's cell. Same expression, second token.
    add("C.5", "panel median, at Table C.1's two decimals (%)", k["median"], 12.13, 0.005,
        "12.13%", ["draft"])
    add("C.5", "median spread, cells naming one letter throughout (%)",
        _sc["fully_named"]["median"], 0.0, 0.005, "a median of 0.00%", ["draft"])
    _sfix = pop.same_series_spread(d, c)
    add("2.3", "security fixed: groups", _sfix["groups"], 2717, 0, "2,717", ["draft"])
    add("2.3", "security fixed: cells", _sfix["cells"], 1758, 0, "1,758 cells", ["draft"])
    add("2.3", "security fixed: companies", _sfix["companies"], 137, 0, "137 companies", ["draft"])
    add("2.3", "security fixed: median spread (%)", _sfix["median"], 0.74, 0.005,
        "0.74%", ["draft"])
    add("2.3", "security fixed: above 24% (%)", _sfix["above_24"], 22.0, 0.1, "22.0%", ["draft"])
    add("2.3", "same cells, series ignored: median (%)", _sfix["pooled_median"], 8.45, 0.01,
        "8.45%", ["draft"])
    add("2.3", "same cells, series ignored: above 24% (%)", _sfix["pooled_above_24"], 35.4, 0.1,
        "35.4%", ["draft"])
    add("2.3", "series-fixed tail: groups above 24%", _sfix["tail_groups"], 597, 0,
        "597 groups", ["draft"])
    add("2.3", "series-fixed tail: companies", _sfix["tail_companies"], 68, 0,
        "68 companies", ["draft"])
    add("C.5", "series-fixed tail: share carried by the top five names (%)",
        _sfix["tail_top5_share"], 29.5, 0.5, "only 29% of them", ["draft"])
    # §3.2's survivor count. It said "twelve, on six issuers" for two rounds: twelve rows is
    # right, six is the number of distinct titles, and the issuers are five because Magic Leap
    # contributes two of the six. Nothing was registered, so nothing disagreed. All three
    # counts are pinned now, and the four/two split is pinned off the two sets rather than off
    # the sentence beside them, which is what was wrong in `population.py`'s own comment.
    # `panel()` hands back the raw marks; the detector runs on the comparable ones, as in
    # `tests/test_population.py`. Passing `d` here returned 91 rows on 19 issuers — the claim
    # instruments §3.2 excludes, counted as survivors of the filter that excludes them.
    _po = pop.price_outliers(pop.comparable(d), c)
    add("5.3", "price-detector survivors: rows", len(_po), 12, 0, "twelve of them", ["draft"])
    add("5.3", "price-detector survivors: distinct titles",
        _po.groupby(["company", "title"]).ngroups, 6, 0, "under six titles", ["draft"])
    add("5.3", "price-detector survivors: distinct issuers", _po.company.nunique(), 5, 0,
        "on five issuers", ["draft"])
    add("5.3", "survivors that are another security of the same issuer",
        len(pop.OTHER_SECURITY), 4, 0, "Four are a genuinely different security", ["draft"])
    add("5.3", "survivors that are marks a house really filed",
        len(pop.MARKS_THAT_STAND), 2, 0, "two are marks that houses really filed", ["draft"])
    add("5.6", "clusters labelled listed", float((_cls.label == "listed").sum()), 348, 0,
        "348 listed clusters", ["draft"])
    add("C.2", "share of booked value left unlabelled (%)",
        float(_cls[_cls.basis == "unclassified"].nav.sum() / _cls.nav.sum() * 100), 2.5, 0.1,
        "2.5%", ["draft"], {"draft": "The remaining 147, holding 2.5%"})
    # Filed where the sentence is. Its context string has always pointed at Appendix A.3's
    # limits paragraph; the section label said §5.2 because §5.2 also happened to print the
    # figure, and when that paragraph turned out to be a duplicate lift and was cut, the
    # mislabelling surfaced. A claim and its context belong to one section.
    add("A.3", "share of booked value labelled by rule (%)",
        float(_cls[_cls.basis == "rule"].nav.sum() / _cls.nav.sum() * 100), 3.7, 0.1,
        "3.7%", ["draft"], {"draft": "applied by rule over 3.7% more"})
    _v = _tot.loc["venture"]
    add("5.6", "venture cells", _v.cells, 2113, 0, "**2,113**", ["draft", "readme"])
    add("5.6", "venture companies", _v.companies, 142, 0, "142 clusters", ["draft"])
    add("5.6", "venture issuers after folding split keys", _ic["venture_issuers"], 137, 0,
        "**137** distinct issuers", ["draft", "readme"])
    add("A.2", "issuers reaching a cell under more than one key", _ic["split_issuers"], 7, 0,
        "seven companies", ["draft"])
    add("5.6", "venture median spread (%)", _v.median_spread_pct, 10.1, 0.1,
        "**10.1%**", ["draft", "readme"])
    add("5.6", "venture cells above 24% (%)", _v.above_24_pct, 37.0, 0.2,
        "**37.0%**", ["draft", "readme"])
    add("5.6", "venture booked NAV ($B)", _v.nav_busd, 402.2, 0.1, "$402.2B", ["draft", "readme"])
    add("5.6", "venture NAV above 24% ($B)", _v.nav_above_24_busd, 152.8, 0.1,
        "**$152.8B**", ["draft", "readme"])
    # The bold wraps the pair "$153.0B — 38.0%", so the bare token is what to look for, with
    # a context phrase pinning it to its role rather than to any percentage that reads 38.0.
    add("5.6", "venture NAV share above 24% (%)",
        float(_v.nav_above_24_busd / _v.nav_busd * 100), 38.0, 0.2, "38.0%", ["draft"],
        {"draft": "$152.8B (38.0%)"})
    add("5.6", "non-venture median spread (%)", _tot.loc["private_nonventure"].median_spread_pct,
        16.1, 0.1, "16.1%", ["draft"])
    add("5.6", "listed median spread (%)", _tot.loc["listed"].median_spread_pct, 19.0, 0.1,
        "19.0%", ["draft"])
    # The like-for-like percentile: all ten §7.1 names carry the venture label, so the
    # population they should be scored against is the venture one, not the mixed panel.
    _gv = g.merge(_cls[["label"]], left_on="company", right_index=True)
    _gv = _gv[_gv.label == "venture"]
    add("5.6", "ten §4.3 names carrying the venture label",
        int(_cls.reindex(["NM:PROJECT DEBUSSY", "NM:STRIPE", "NM:ANTHROPIC", "NM:EPIC GAMES",
                          "ROW:276028", "ROW:275786", "NM:OPENAI", "NM:ANDURIL", "NM:DISCORD",
                          "NM:REVOLUT"]).label.eq("venture").sum()), 10, 0, None)
    add("C.2", "house-level ten-name median, percentile in the venture panel",
        float((_gv.spread_pct < _mh).mean() * 100), 63, 1, "**63rd percentile**", ["draft"])
    add("C.2", "fund-level 24%, percentile in the venture panel",
        float((_gv.spread_pct < 24).mean() * 100), 63, 1, "**63rd**", ["draft"])
    # Why the listed bucket's median exceeds the venture one, settled rather than left open.
    _ls = ccl.listed_split()
    add("C.2", "listed clusters whose marks never move", _ls["frozen_companies"], 135, 0,
        "**135**", ["draft"])
    add("C.2", "median spread, listed clusters that never move (%)",
        _ls["frozen_median"], 0.7, 0.1, "**0.7%**", ["draft"])
    add("C.2", "of those, share above 24% (%)", _ls["frozen_above_24_pct"], 7.4, 0.3, "7.4%", ["draft"])
    add("C.2", "listed clusters still being repriced", _ls["moving_companies"], 213, 0, "213", ["draft"])
    add("C.2", "median spread, listed clusters still repriced (%)",
        _ls["moving_median"], 32.8, 0.2, "**32.8%**", ["draft"])
    add("C.2", "booked value per listed cell ($M)", _ls["listed_nav_per_cell_musd"], 3.7, 0.1,
        "$3.7M", ["draft"])
    add("C.2", "booked value per venture cell ($M)", _ls["venture_nav_per_cell_musd"], 66.6, 0.2,
        "$66.6M", ["draft"])

    add("A.2", "rows whose two name fields disagree (%)", _mm["row_pct"], 2.52, 0.05,
        "**2.52%**", ["draft"])
    add("A.2", "clusters carrying such a row", _mm["clusters"], 57, 0, "57 clusters", ["draft"])

    # -- listing dates read off EDGAR, and the P4 pre-test that runs on them ----------------
    _ld = ld.summary()
    add("E.1", "listing dates: companies asked for", _ld["candidates"], 23, 0, "23 companies", ["draft"])
    add("E.1", "listing dates: dated from filings", _ld["dated"], 21, 0, "**21**", ["draft"])
    add("E.1", "listing dates: validated against the panel exit", _ld["validated"], 18, 0,
        "**eighteen**", ["draft"])
    add("E.1", "listing dates: worst validated gap (days)", float(_ld["worst_validated_gap"]),
        82, 0, "**82 days**", ["draft"])
    add("E.1", "listing dates: closest rejected gap (days)", float(_ld["closest_rejected_gap"]),
        258, 0, "258", ["draft"])

    _p4 = p4.summary()
    add("F.4", "P4 pre-test cohort size", _p4["names"], 15, 0, "**fifteen**", ["draft"])
    add("F.4", "P4 pre-test: names that narrow", _p4["declined"], 6, 0, "Six narrow", ["draft"])
    add("F.4", "P4 pre-test: names that widen", _p4["widened"], 7, 0, "seven widen", ["draft"])
    add("F.4", "P4 pre-test: one-sided signed-rank p", _p4["p_endpoint"], 0.431, 0.01,
        "**p=0.43**", ["draft"])
    add("F.4", "P4 pre-test: same test on the full within-window trend, p", _p4["p_trend"],
        0.838, 0.01, "p=0.84", ["draft"])
    add("F.4", "P4 pre-test: cells that sat after their own listing", _p4["post_listing_cells"],
        1, 0, None)
    add("F.4", "P4 power against a ten-point narrowing", _p4["power_at_10"], 0.43, 0.04,
        "**0.43**", ["draft"])
    add("F.4", "P4 power against a ten-point narrowing, normal approximation",
        _p4["power_normal_at_10"], 0.17, 0.04, "0.17", ["draft"])
    add("F.4", "P4 power against every spread collapsing to zero", _p4["power_total_collapse"],
        0.73, 0.04, "**0.73**", ["draft"])
    add("F.4", "P4 pre-test, the note-text rule it replaced: cohort size",
        _p4["legacy_strict_n"], 12, 0, "twelve", ["draft"])
    add("F.4", "P4 pre-test, the note-text rule it replaced: p", _p4["legacy_strict_p"],
        0.577, 0.01, "p=0.58", ["draft"])
    add("F.4", "P4 pre-test, looser membership: cohort size", _p4["legacy_loose_n"], 18, 0, None)
    add("F.4", "P4 pre-test, looser membership: p", _p4["legacy_loose_p"], 0.378, 0.01,
        "p=0.38", ["draft"])

    # The far side of the window's new boundary. Registered without a literal because none of
    # it is in the manuscript yet — the point of registering it now is that these are the
    # numbers a later draft would quote, and an unregistered number is one that can drift
    # between the run that produced it and the sentence that repeats it.
    _lag = p4.lag_summary()
    add("10.1", "post-listing marks still at Level 3", _lag["post_listing_marks"], 57, 0, None)
    add("10.1", "post-listing marks: names", _lag["post_listing_names"], 10, 0, None)
    add("10.1", "post-listing marks inside a 180-day lock-up", _lag["marks_inside_lockup"],
        43, 0, None)
    add("10.1", "post-listing marks past the lock-up", _lag["marks_past_lockup"], 14, 0, None)
    add("10.1", "post-listing marks past the lock-up: names", _lag["names_past_lockup"], 3, 0, None)
    add("10.1", "longest Level-3 persistence after a listing (days)", float(_lag["longest_days"]),
        1603, 0, None)
    add("10.1", "largest post-lock-up Level-3 mark ($)", _lag["largest_late_mark_usd"],
        260773.12, 0.01, None)

    # -- 5.7 the dollars -------------------------------------------------------------------
    add("5.7", "booked NAV across population cells ($B)", k["nav_busd"], 517.3, 0.3,
        "$517.3B", ["draft", "readme"])
    add("5.7", "NAV in cells disagreeing over 24% ($B)", k["nav_disagreeing_busd"], 180.0, 0.3,
        "$180.0B", ["draft", "readme"])
    add("5.7", "NAV share in cells disagreeing over 24% (%)", k["nav_disagreeing_share"],
        34.8, 0.2, "34.8%", ["draft", "readme"])

    # -- 5.8 persistence --------------------------------------------------------------------
    add("5.8", "companies on 4+ report dates", per["companies"], 290, 0, "290 companies", ["draft"])
    add("5.8", "between-company share of spread variance (%)", per["between_share"], 58.8, 0.4,
        "58.8%", ["draft", "readme"])
    add("5.8", "relabelling null median (%)", per["null_median"], 9.7, 0.6, "9.7%", ["draft", "readme"])
    add("5.8", "relabelling null 95th percentile (%)", per["null_p95"], 10.8, 0.8, "10.8%", ["draft"])
    add("5.8", "lag-1 Spearman rho, all pairs", per["rho_all"], 0.734, 0.005, "0.734", ["draft", "readme"])
    add("5.8", "lag-1 pairs, all", per["n_all"], 3439, 0, "3,439", ["draft"])
    add("5.8", "lag-1 Spearman rho, mark moved", per["rho_moved"], 0.665, 0.005, "0.665", ["draft", "readme"])
    add("5.8", "lag-1 pairs, mark moved", per["n_moved"], 2228, 0, "2,228", ["draft"])

    # -- 5.9 the question Appendix D left open ------------------------------------------------------
    _st = pop.staleness(d, c)
    add("5.9", "cells where every house's freshness is knowable", _st["judgeable"], 3238, 0,
        "3,238", ["draft"])
    add("5.9", "cells in which no house moved", _st["quiet"], 760, 0, "**760**", ["draft"])
    add("5.9", "companies contributing a stood-pat cell", _st["quiet_companies"], 197, 0,
        "197 companies", ["draft"])
    add("5.9", "stood-pat cells that are not unanimous (%)", _st["quiet_nonzero_pct"], 66.4, 0.3,
        "**66.4%**", ["draft"])
    add("5.9", "stood-pat cells above 24% (%)", _st["quiet_above_24_pct"], 23.6, 0.3, "23.6%",
        ["draft"])
    add("5.9", "stood-pat cells above 24%, count", _st["quiet_above_24_n"], 179, 0, "179", ["draft"])
    add("5.9", "NAV in stood-pat cells above 24% ($B)", _st["quiet_above_24_nav_busd"], 5.3, 0.1,
        "$5.3B", ["draft"])
    add("5.9", "parked houses holding one number for 4+ reports (%)",
        _st["parked_four_or_more_pct"], 26.0, 0.3, "**26.0%**", ["draft"])
    add("5.9", "cells in which every house moved", _st["fresh"], 1147, 0, "1,147", ["draft"])
    add("5.9", "median spread where every house moved (%)", _st["fresh_median"], 9.9, 0.15,
        "9.9%", ["draft"])
    add("5.9", "companies with both kinds of cell", _st["paired_companies"], 129, 0,
        "129 companies", ["draft"])
    # Both of these count companies whose two medians differ, so both inherit whatever the
    # tie rule decides. `population.same_number` makes that rule a tolerance rather than
    # float equality; the tolerances here are what a legitimate dependency release may move
    # them by, and `narrowest untied gap` is the number that says the count means anything.
    add("5.9", "untied companies in the paired comparison", _st["paired_untied"], 95, 2,
        "95 companies", ["draft"])
    add("5.9", "untied companies where the remarked cells are wider",
        _st["paired_fresh_wider"], 54, 2, "are wider in 54", ["draft"])
    add("5.9", "sign test on the paired comparison", _st["sign_p"], 0.22, 0.06, "p=0.22", ["draft"])
    add("5.9", "signed-rank test on the paired magnitudes", _st["wilcoxon_p"], 0.002, 0.0006,
        "p=0.001", ["draft"])
    add("5.9", "narrowest untied gap between two company medians (pts)",
        _st["narrowest_untied_gap"], 1.9e-8, 1e-9, None)

    # -- 5.10 house policy at scale ------------------------------------------------------------
    add("5.10", "multi-fund house cells", hp["family_cells"], 9210, 0, "9,210", ["draft", "readme"])
    add("5.10", "house cells filing one identical mark (%)", hp["identical_pct"], 89.0, 0.05,
        "89.0%", ["draft", "readme"])
    add("5.10", "between-house variance share, population median", hp["eta2_median"], 1.000, 0.001,
        "**1.000**", ["draft"])
    add("5.10", "multi-house cells scored", hp["eta2_cells"], 3278, 0, "3,278", ["draft"])

    # -- 5.11 the relationship that reverses -----------------------------------------------------
    add("5.11", "size effect at 8 report dates (NAV ratio)", hz.loc[8, "nav_ratio"], 0.59, 0.01,
        "0.59×", ["draft"])
    add("5.11", "size effect at 16 report dates (NAV ratio)", hz.loc[16, "nav_ratio"], 0.36, 0.01,
        "0.36×", ["draft"])
    add("5.11", "size effect at 24 report dates (NAV ratio)", hz.loc[24, "nav_ratio"], 0.28, 0.01,
        "**0.28×**", ["draft"])
    add("5.11", "size effect p at 24 report dates", hz.loc[24, "p"], 1.6e-11, 2e-12,
        "p=2×10⁻¹¹", ["draft"])
    add("5.11", "size effect p on the full panel", per["nav_mwu_p"], 5.9e-5, 1e-5,
        "p=6×10⁻⁵", ["draft"])
    add("5.11", "size effect on the full panel (NAV ratio)", per["nav_ratio"], 0.66, 0.02,
        "**0.66×**", ["draft"])

    # -- 5.12 reconciliation ---------------------------------------------------------------------
    _bd = _rvmod.bound_from_the_complete_filing_set()
    _ex = _rvmod.same_series_exemplar()
    add("5.12", "published ten-cell median spread (%)", _bd["published_median"], 23.5, 0.1,
        "**23.5%**", ["draft"])
    add("5.12", "same cells on the complete filing set, median (%)", _bd["bulk_median_guarded"],
        34.7, 0.1, "**34.7%**", ["draft"])
    _fb = fmb.summary()
    add("5.12", "complete-filing median, cross-checked in fund_marks_bulk (%)",
        _fb["bulk_median"], 34.7, 0.1, None)
    add("5.12", "median restricted to one named series (%)", _fb["letter_median"], 28.7, 0.1,
        "**28.7%**", ["draft"])
    add("5.12", "cells where two houses name the same series", _fb["letters_shared"], 7, 0,
        "seven of the nine", ["draft"])
    # The two cells the corrected series pattern moves furthest, registered because the
    # sentence that names them is the one that went stale silently: it kept the pattern's old
    # answer for a round while the code carried the new one. Stripe is the whole decomposition
    # arriving in a single cross-fund cell — 73.1% between houses is 1.4% once both are held
    # to Series B — and it is quoted in the prose, so it is pinned like any other figure.
    _lr = fmb.letter_restricted().set_index("company").spread_pct
    add("5.12", "Stripe's spread restricted to its shared series (%)", float(_lr["Stripe"]),
        1.4, 0.05, "Stripe 73.1% to 1.4%", ["draft"])
    add("5.12", "Canva's spread restricted to its shared series (%)", float(_lr["Canva"]),
        33.3, 0.05, "Canva 39.3% to 33.3%", ["draft"])
    add("5.12", "of those, cells the restriction leaves unchanged", _fb["letters_unchanged"],
        3, 0, "**three**", ["draft"])
    add("5.12", "funds per cell, published", _fb["published_funds_median"], 8, 0, None)
    add("5.12", "funds per cell, complete filings", _fb["bulk_funds_median"], 16, 0,
        "**8 to 16**", ["draft"])
    add("5.12", "cells surviving the guard on the bulk recomputation", _bd["cells_guarded"],
        9, 0, "nine of the ten", ["draft"])
    add("5.12", "Stripe Series I: houses naming the same series", _ex["houses"], 4, 0,
        "**four fund houses**", ["draft"])
    add("5.12", "Stripe Series I: funds", _ex["funds"], 9, 0, None)
    add("5.12", "Stripe Series I: lowest mark ($)", _ex["low_pps"], 36.90, 0.01,
        "**$36.90**", ["draft"])
    add("5.12", "Stripe Series I: highest mark ($)", _ex["high_pps"], 63.87, 0.01,
        "**$63.87**", ["draft"])
    add("5.12", "Stripe Series I: spread (%)", _ex["spread_pct"], 73.1, 0.1, "**73.1%**", ["draft"])
    add("5.12", "Stripe Series I: rows whose value/balance returns the filed price",
        _ex["arithmetic_checks"], 9, 0, "all nine", ["draft"])
    # The staleness reading of the outlier, tested rather than dismissed.
    _eh = _rvmod.exemplar_history()
    add("5.12", "outlying house: reporting dates", _eh["observations"], 12, 0, "**twelve**", ["draft"])
    add("5.12", "outlying house: consecutive quarters below the others", _eh["discount_run"],
        5, 0, "**last five quarters**", ["draft"])
    add("5.12", "outlying house: own move at the last step (%)", _eh["own_move_pct"], 5.9, 0.1,
        "**5.9%**", ["draft"])
    add("5.12", "the other houses' move at the same step (%)", _eh["others_move_pct"], 52.1, 0.1,
        "**52.1%**", ["draft"])
    add("5.12", "outlying house's mark was ever the consensus (0 = never)",
        float(_eh["ever_the_consensus"]), 0, 0, None)
    add("5.12", "outlying house's own marks rose across the run (1 = yes)",
        float(_eh["own_marks_rising"]), 1, 0, None)
    # The two figures E.3 prints for one cell. 71% is the other houses' median over Morgan
    # Stanley's mark; 73.1% is the cell's max over its min. They differ because the comparator
    # differs, and the paragraph now says so — unregistered, the pair read as an unexplained
    # two-point discrepancy in the paper's own showcase cell.
    add("5.12", "outlying house: gap to the others' median at the last date (%)",
        _eh["gap_last_pct"], 70.7, 0.1, "and now 71%", ["draft"])

    add("5.12", "published cells returning more funds", int((_rec.verdict == "wider coverage").sum()),
        9, 0, "nine cells with *more* funds", ["draft"])
    add("5.12", "median funds per published cell, first version", _rec.paper_funds.median(), 8, 0,
        "**8 funds to 15.5**", ["draft"])
    add("5.12", "median funds per published cell, bulk data",
        _rec[_rec.bulk_funds > 0].bulk_funds.median(), 15.5, 0, None)


def _print_table(nums: list[Number]) -> None:
    hdr = f"{'§':<5}{'claim':<14}{'computed':>12}{'paper':>10}  {'code':<5}{'prose':<7} label"
    print(hdr)
    print("-" * len(hdr))
    for n in nums:
        if not n.claim and not n.context:
            prose = "n/a"
        else:
            miss = prose_missing(n)
            prose = "OK" if not miss else "MISS"
        claim = n.claim or "(numeric)"
        print(f"{n.section:<5}{claim:<14}{n.computed:>12.3f}{n.value:>10.3f}  "
              f"{'OK' if n.code_ok else 'DRIFT':<5}{prose:<7} {n.label}")


if __name__ == "__main__":
    nums = canonical_numbers()
    _print_table(nums)
    bad_code = [n for n in nums if not n.code_ok]
    bad_prose = [n for n in nums if prose_missing(n)]
    print(f"\n{len(nums)} canonical numbers · {len(bad_code)} code-drift · {len(bad_prose)} prose-drift")
    sys.exit(1 if (bad_code or bad_prose) else 0)
