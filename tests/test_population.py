"""Guards for the population panel (§5) and for the two mistakes it took to build it.

Neither test below restates a number — `tests/test_paper_consistency.py` already pins every
§5 figure against the registry. These cover the things a number cannot: that the identity
join is safe, that one bucketing serves the table, the figure and the registry, and that the
manuscript does not call a monthly report date a quarter.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import coverage_regimes as cov
import population as pop


@pytest.fixture(scope="module")
def cells():
    _, c = pop.panel()
    return c[c.guarded]


def test_shared_identifier_joins_do_not_fuse_unrelated_securities():
    """Entity resolution joins rows on a shared CUSIP-shaped code, and 2.6% of those codes
    are filer- or vendor-assigned TC identifiers rather than real CUSIPs. If such a code were
    private to one filer, two registrants carrying the same string would be two different
    securities and the join would invent a price spread — this paper's dependent variable,
    manufactured. The check is empirical: where two registrants do share a code on one date,
    their prices must agree. They do, to the cent, so the join is sound.
    """
    d, _ = pop.panel()
    cu = d.ISSUER_CUSIP.fillna("").str.strip().str.upper()
    tc = d[cu.str.startswith("TC") & (cu != "")].assign(cu=cu[cu.str.startswith("TC") & (cu != "")])
    shared = tc.groupby("cu").CIK.nunique()
    cross = tc[tc.cu.isin(shared[shared > 1].index)]
    assert len(cross) > 500, "too few cross-registrant rows for this check to mean anything"

    r = cross.groupby(["cu", "dt"]).pps.agg(["min", "max", "size"])
    r = r[r["size"] > 1]
    assert len(r) > 100, f"only {len(r)} code-date groups; the check would prove nothing"
    ratio = r["max"] / r["min"]
    assert ratio.median() == pytest.approx(1.0, abs=1e-6), (
        f"shared vendor codes disagree on price (median ratio {ratio.median():.3f}) — the "
        "identifier join is fusing different securities")
    assert (ratio > pop.CLASS_GUARD).mean() == 0, (
        "some shared-code groups differ by more than the share-class guard")


def test_one_bucketing_serves_the_table_the_figure_and_the_registry(cells):
    """The manuscript table, the figure and the number registry each bucketed the spread
    independently at first, using different edge conventions. Seven cells sitting exactly at
    50% then landed in different rows depending on the caller, and the registry caught it as
    six simultaneous drifts. There is now one function; this pins that it stays complete."""
    bk = pop.spread_buckets(cells)
    assert list(bk.bucket) == pop.BUCKET_LABELS
    assert bk.cells.sum() == len(cells), "bucketing drops or double-counts cells"
    assert bk.cells_pct.sum() == pytest.approx(100.0, abs=1e-9)
    assert bk.nav_pct.sum() == pytest.approx(100.0, abs=1e-9)
    assert bk.nav_busd.sum() == pytest.approx(cells.nav.sum() / 1e9, rel=1e-9)


def test_a_monthly_report_date_is_never_called_a_quarter():
    """N-PORT carries position detail for every month-end, so the panel's unit is a company
    on a report date and there are 104 of them across 27 quarterly data sets. An earlier
    draft called these company-quarters throughout — a specific factual claim, and wrong."""
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    # The population material now runs from the data section through the staleness tests;
    # the appendices are excluded because the robustness appendix genuinely buckets calendar quarters.
    body = draft.split("## 3. The data")[1].split("## 7. Which mark was right")[0]
    assert len(body) > 20000, "the population span has moved; this check has lost its anchor"
    assert not re.search("company.quarter", body, re.I), (
        "the population sections call a monthly report date a quarter")
    for rel in ["src/population.py", "src/population_figure.py"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert not re.search("company.quarter", text, re.I), (
            f"{rel} calls a monthly report date a quarter")
    # The staleness test in section 4.8 does bucket into calendar quarters, so the word is
    # correct there; a blanket rename of the manuscript once removed it.
    assert "company-quarters over seven companies" in draft, (
        "section 4.8 genuinely works on calendar quarters and should say so")


def test_the_family_unit_is_the_house_not_the_trust():
    """A registrant is a legal trust. Fidelity files under 36 of them, so counting
    registrants as families lets one house clear a bar meant to need two independent
    opinions, and then records that house agreeing with itself. Section 5 was built that way
    once; this pins that the panel now groups by complex."""
    import fund_complex as fx
    d, _c = pop.panel()
    assert "house" in d.columns, "the panel no longer carries a fund-complex column"
    assert fx.complex_of("FIDELITY CONTRAFUND") == "Fidelity"
    assert fx.complex_of("Variable Insurance Products Fund II") == "Fidelity"
    assert fx.complex_of("Growth Fund of America") == "Capital Group"
    assert fx.complex_of("iShares Trust") == "BlackRock"
    # Verified against the series each files: Ivy is Macquarie's, not Invesco's, and a
    # multi-adviser series trust must stay unmapped or it fabricates one house from several.
    assert fx.complex_of("IVY FUNDS") == "Macquarie"
    assert fx.complex_of("Professionally Managed Portfolios") == "PROFESSIONALLY MANAGED PORTFOLIOS"
    assert d[d.house == "Fidelity"].CIK.nunique() >= 30, (
        "the map stopped collapsing Fidelity's trusts")


def test_collapsing_trusts_into_houses_does_not_fabricate_disagreement():
    """The merge is the step that could manufacture this paper's dependent variable. If it
    fused two genuinely different houses, marks inside one 'complex' would disagree. The
    check is empirical and has to run both ways: inside a complex must be at least as tight
    as inside a single registrant, and far tighter than across complexes."""
    d, c = pop.panel()
    x = pop.comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    x = x[[k in keys for k in zip(x.company, x.dt)]]
    assert len(x) > 10_000, f"only {len(x)} rows; the comparison would prove nothing"

    def identical_share(by):
        r = x.groupby(["company", "dt", by]).pps.agg(["min", "max", "size"])
        r = r[r["size"] > 1]
        return float(((r["max"] / r["min"]) <= 1.0001).mean() * 100), len(r)

    within_house, n_h = identical_share("house")
    within_reg, n_r = identical_share("CIK")
    fam = x.groupby(["company", "dt", "house"]).pps.median().reset_index()
    acr = fam.groupby(["company", "dt"]).pps.agg(["min", "max", "size"])
    acr = acr[acr["size"] > 1]
    across = float(((acr["max"] / acr["min"]) <= 1.0001).mean() * 100)

    assert n_h > 1000 and n_r > 1000, "too few multi-fund groups to compare"
    assert within_house >= within_reg - 1.0, (
        f"merging trusts into houses loosened agreement ({within_house:.1f}% vs "
        f"{within_reg:.1f}% within a single registrant) — a merge is probably wrong")
    assert within_house > across + 30, (
        f"within-house {within_house:.1f}% is not distinguishable from across-house "
        f"{across:.1f}%; the complex is not behaving like one valuation committee")


def test_the_population_figure_is_wired_into_the_pdf_build():
    """A figure with no caption entry silently vanishes from the PDF while the in-text
    pointer survives as a literal file path, which is how a reader finds `figures/x.png`
    printed mid-sentence in a finished paper."""
    build = (ROOT / "src" / "build_pdf.py").read_text(encoding="utf-8")
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    fig = "figures/population_spread.png"
    assert f'"{fig}": (' in build, "no caption registered"
    assert f'("{fig}", ["{fig}"])' in build, "not placed in any figure group"
    # The pointer map is derived from the injection order rather than written down, so the
    # check is that the map the build actually produces names this figure — a hard-coded
    # "(Figure 9)" would pass while pointing at whatever the reorder moved into ninth place.
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "src"))
    import build_pdf as _bp
    _, _rw = _bp.inject_figures(_bp.parse_draft(draft)["body"])
    assert f"(`{fig}`)" in _rw, "the build does not rewrite this figure's in-text pointer"
    assert re.fullmatch(r"\(Figure \d+\)", _rw[f"(`{fig}`)"]), _rw[f"(`{fig}`)"]
    assert f"(`{fig}`)" in draft, "the manuscript never points at the figure"
    assert (ROOT / fig).exists(), "the figure file itself is missing"


def test_no_reported_cell_prices_a_claim_against_a_share():
    """The identifiers that keep two companies apart cannot keep two securities apart.

    A CUSIP and an LEI name the issuer. A contingent value right, an escrow line, a
    subscription right, a warrant and a lock-up placeholder therefore land on the same
    company key as the stock, and their price per unit is not a price per share — so a cell
    holding one against the other reports a spread that no house ever expressed. The panel
    is built to have none of them left; this fails if the exclusion is ever loosened or the
    field it reads is renamed.
    """
    d, c = pop.panel()
    x = pop.comparable(d)
    keys = set(zip(c[c.guarded].company, c[c.guarded].dt))
    inside = x[[k in keys for k in zip(x.company, x.dt)]]
    bad = inside[pop.is_claim(inside)]
    assert bad.empty, (
        f"{len(bad)} claim-instrument rows reach a reported cell, e.g. "
        f"{bad.ISSUER_TITLE.head(3).tolist()}")


def test_the_claim_filter_would_actually_fire():
    """A filter that matches nothing passes the test above for the wrong reason.

    The strings below are the shapes the filings actually use, and the last two are the
    near-misses that word boundaries exist to protect: a company whose name merely contains
    the letters, and one whose name ends in them.
    """
    import pandas as pd
    sample = pd.DataFrame({
        "ISSUER_TITLE": ["ABIOMED INC CVR RIGHTS (DEC 2022)", "GCI LIBERTY INC ESCROW DUMMY",
                         "SPIRIT MTA REIT RTS", "GRASSHOPPER BANCORP WTS 10/28 PP",
                         "SCILEX HOLDING LOCK UP", "STRIPE INC SER H PC PP",
                         "ESCO TECHNOLOGIES INC", "PARTS AUTHORITY LLC"],
        "ISSUER_NAME": ["ABIOMED INC", "GCI LIBERTY INC", "SPIRIT MTA REIT",
                        "GRASSHOPPER BANCORP", "SCILEX HOLDING", "STRIPE INC",
                        "ESCO TECHNOLOGIES", "PARTS AUTHORITY"],
    })
    got = pop.is_claim(sample).tolist()
    assert got == [True, True, True, True, True, False, False, False], got


def test_the_singular_spellings_need_an_expiry_to_fire():
    """RT and WT are two letters, so they are matched only beside a date.

    Both halves of that rule can fail, and each half has a row here. The first four are the
    spellings that got past `WTS` and `RTS` for two rounds. The last two are what the expiry
    condition protects: a preferred whose title carries the expiry of a paper certificate,
    and a Chinese expressway whose abbreviated name is the letters EXP.
    """
    import pandas as pd
    sample = pd.DataFrame({
        "ISSUER_TITLE": ["ACER INC RT 06/16/2023", "SWEETGREEN INC SER J WT P/P 01/21/26",
                         "DRAFTKINGS INC-CW25", "EARNOUT SHS 12.50 COMMON STOCK",
                         "PROTERRA INC PFD USD SERIES 5 *PHYS CERTS 144A EXP 09/16/17*",
                         "SICHUAN EXP-H"],
        "ISSUER_NAME": ["ACER INC", "SWEETGREEN INC", "DRAFTKINGS INC - CL A", "",
                        "PROTERRA INC", "SICHUAN EXPRESSWAY CO LTD"],
    })
    assert pop.is_claim(sample).tolist() == [True, True, True, True, False, False]


def test_the_book_entry_words_fire_and_the_price_detector_agrees():
    """The fifth leak and the test that would have caught it without knowing its spelling.

    DUMMY and PLACEHOLDER describe the entry rather than the paper, a liquidating trust is a
    claim on a wound-up company, and a SAFE has no share count to divide by. All four passed
    a filter that already knew about escrow dummies, because the earlier pattern wanted the
    word ESCROW beside it.
    """
    import pandas as pd
    sample = pd.DataFrame({
        "ISSUER_TITLE": ["FORESIGHT ENERGY LLC DUMMY EQUITY", "HOMER CITY HOLDINGS (PLACEHOLDER)",
                         "CMS LIQUIDATING TRUST", "SAMBANOVA SAFE",
                         "SYNIVERSE PFD PIK PFDJJZ917", "STRIPE INC SER H PC PP"],
        "ISSUER_NAME": ["FORESIGHT ENERGY LLC", "HOMER CITY GENERATION LP",
                        "CENTER FOR MEDICAL SCIENCE INC", "SAMBANOVA SYSTEMS INC",
                        "SYNIVERSE", "STRIPE INC"],
    })
    # The last two are the near-misses: PIK preferred is real accruing equity and a named
    # private-placement series is the paper's own subject.
    assert pop.is_claim(sample).tolist() == [True, True, True, True, False, False]


def test_the_price_detector_leaves_only_examined_rows():
    """The version of the filter that a sixth spelling cannot get past.

    Every leak so far looked the same in the data whatever it was called: a price two orders
    of magnitude from the rest of its own cell, under a title nobody else in that cell uses.
    This asserts the survivors are the ones read one at a time — and it asserts the detector
    is not silently empty, which is how a check of this shape usually fails.
    """
    d = pop.load_marks()
    x = pop.comparable(d)
    po = pop.price_outliers(x, pop.cells(x))
    assert len(po) >= 5, "the price detector matched almost nothing; check it still runs"
    assert set(zip(po.company, po.title)) == pop.PRICE_OUTLIERS


def test_the_survivor_counts_are_what_section_2_2_says():
    """Rows, titles and issuers are three different numbers and §3.2 quoted the wrong one.

    It read "twelve, on six issuers". Twelve rows is right; six is the count of distinct
    titles; the issuers are five, because Magic Leap contributes two of the six. The
    four/two split beside it was right, so the paragraph's arithmetic closed and the wrong
    noun survived two rounds of review.

    The counts are also registered in `src/paper_numbers.py`, which checks them against the
    prose. This checks them against each other, which the registry cannot: that titles and
    issuers really do differ here is the whole reason the sentence was wrong, and a panel
    where they happened to coincide would make the registry entries pass while saying
    nothing.
    """
    d = pop.load_marks()
    x = pop.comparable(d)
    po = pop.price_outliers(x, pop.cells(x))
    titles = po.groupby(["company", "title"]).ngroups
    issuers = po.company.nunique()
    assert (len(po), titles, issuers) == (12, 6, 5)
    assert titles != issuers, "titles and issuers coincide; §3.2's distinction is untestable here"
    assert pop.OTHER_SECURITY.isdisjoint(pop.MARKS_THAT_STAND)
    assert (len(pop.OTHER_SECURITY), len(pop.MARKS_THAT_STAND)) == (4, 2)
    assert len(pop.PRICE_OUTLIERS) == titles


def test_the_price_detector_is_not_a_filter():
    """It reports; it must never be wired into `comparable`.

    This paper measures disagreement, so a rule that dropped marks for being far from their
    neighbours would delete its own subject. Epic Games at $1.00 against a $600 consensus is
    a mark First Trust really filed, and it is still in the panel.
    """
    d = pop.load_marks()
    x = pop.comparable(d)
    epic = x[(x.company == "NM:EPIC GAMES") & (x.pps <= 1.0)]
    assert not epic.empty, "the $1.00 Epic Games mark has been filtered out"


def test_the_unnamed_issuer_cluster_is_not_a_company():
    """Rows a filer left without an issuer name arrive fused into one pseudo-company.

    Allstar Coinvest, Chennai Super Kings Cricket and Lithium Technologies are not one
    issuer, and a spread computed across them measures the absence of a name.
    """
    d = pop.load_marks()
    assert (d.company == pop.UNRESOLVED).any(), "the unnamed rows are gone; drop the exclusion"
    assert not (pop.comparable(d).company == pop.UNRESOLVED).any()


def test_no_unexamined_expiring_instrument_survives():
    """The detector that replaced extending the spelling list by hand.

    An instrument that runs out carries a date; a share in a company does not. Anything
    left in the panel with an expiry word on it is therefore either a claim the patterns
    still miss or a false positive, and both deserve a name rather than a silent pass. The
    pinned set is what a reading of every survivor left behind, so a re-harvest that brings
    a new spelling fails here instead of quietly widening the panel.
    """
    surviving = pop.expiring_survivors(pop.load_marks())
    assert surviving == pop.EXPIRING_SURVIVORS, (
        f"new: {sorted(surviving - pop.EXPIRING_SURVIVORS)} · "
        f"gone: {sorted(pop.EXPIRING_SURVIVORS - surviving)}")


def test_the_stood_pat_cells_are_scored_strictly():
    """§6.2 rests on cells where no house moved, so the classification has to be the strict
    one: a cell counts as quiet only when every house in it has a recent enough previous
    observation to have stood pat deliberately. If judgeability were assumed rather than
    checked, a house appearing for the first time would be scored as having held its mark.
    """
    d, c = pop.panel()
    st = pop.staleness(d, c)
    g = c[c.guarded]
    assert st["judgeable"] < len(g), "every cell judgeable means the freshness bar is not applied"
    assert st["quiet"] + st["fresh"] < st["judgeable"], "no cell has houses moving both ways"
    assert st["quiet_companies"] > 100, "too few companies for §6.2 to describe a population"


def test_no_paired_comparison_sits_where_a_dependency_release_would_decide_it():
    """The integer count in §6.2 is only meaningful if no company sits on the boundary.

    Six pairs used to differ by about 1e-14 — the residue of `hi/lo - 1` followed by a
    median — and changed side between pandas 2.2.3 and 2.3.3, moving a printed count.
    `population.same_number` puts those on the tie side; this asserts the nearest real
    difference stays clear of the tie rule by a wide enough margin that accumulation cannot
    carry it across. It currently clears by a factor of nineteen, against residue five
    orders smaller again. If a future panel puts a company inside that band, the count stops
    being reportable and this fails rather than the referee's build.
    """
    d, c = pop.panel()
    st = pop.staleness(d, c)
    assert st["narrowest_untied_gap"] > 10 * pop.IDENTICAL, (
        f"a company's two medians differ by {st['narrowest_untied_gap']:.3g} points, close "
        "enough to the tie tolerance that a dependency release could decide the count")


def test_same_number_calls_float_noise_a_tie_and_real_differences_real():
    """The tolerance has to be loose enough to swallow the accumulation residue and tight
    enough to keep every difference that means anything. Both edges are checked, because a
    rule that ties everything would pass the test above for the wrong reason."""
    import numpy as np
    assert pop.same_number(14.32, 14.32 + 1.11e-14)
    assert pop.same_number(0.0, 0.0)
    assert pop.same_number(1234.5, 1234.5 + 2.2e-13)   # large spreads carry larger residue
    assert not pop.same_number(14.32, 14.32 + 1.9e-8)  # the narrowest real gap in the panel
    # A relative tolerance would have made that last case a near-miss rather than a clear
    # one, which is why the rule is absolute: at this level rtol=1e-9 is 1.4e-8.
    assert not pop.same_number(1234.5, 1234.5 + 1.9e-8)
    assert not pop.same_number(0.0, 0.01)
    assert list(pop.same_number(np.array([1.0, 1.0]), np.array([1.0, 2.0]))) == [True, False]


def test_one_book_filed_twice_is_found_and_is_small():
    """Two house labels, one share count, one value to the cent — that is not two opinions.

    This is the detector that found five affiliate groups `fund_complex` had not merged
    (Apollo, Gabelli, AllianzGI, Tekla and Putnam's eighteen trusts). What it asserts now is
    the residual: after those merges the duplicated books touch a low single-digit share of
    the guarded panel, and dropping every cell they touch moves the headline median by less
    than half a point. If either stops being true the section rests on copies and the note
    has to say so.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import population as pop
    s = pop.duplicate_book_summary()
    assert s["guarded_cells_touched_pct"] < 5, "duplicated books now touch a real share of §5"
    assert abs(s["median_spread_clean"] - s["median_spread_all"]) < 0.5
    assert s["duplicated_holdings"] > 0, "the detector matches nothing; check the key"


def test_the_affiliate_merges_are_the_ones_the_detector_found():
    """Each rule added from the detector, checked against the registrants it has to catch."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import fund_complex as fx
    for name, want in [("Apollo Senior Floating Rate Fund Inc.", "Apollo"),
                       ("Apollo Tactical Income Fund Inc.", "Apollo"),
                       ("AllianzGI Convertible & Income Fund II", "AllianzGI"),
                       ("TEKLA LIFE SCIENCES INVESTORS", "Tekla"),
                       ("Gabelli 787 Fund, Inc.", "Gabelli"),
                       ("George Putnam Balanced Fund", "Putnam"),
                       ("Putnam Variable Trust", "Putnam")]:
        assert fx.complex_of(name) == want, f"{name} no longer maps to {want}"
    # GDL Fund carries the same book as Gabelli's trusts and is deliberately left alone,
    # because nothing it files says Gabelli. The map fails closed; this keeps it that way.
    assert fx.complex_of("GDL Fund") != "Gabelli"
    # And the Putnam rule must not backdate the Franklin acquisition.
    assert fx.complex_of("Franklin Templeton Trust") != "Putnam"


def test_an_empty_pattern_list_matches_nothing_rather_than_everything():
    """`"|".join({}.values())` is "", and `str.contains("")` is True for every row.

    `correction_cost` empties one of these dictionaries to measure what it is worth, and the
    first version of that measurement reported the sign backwards for exactly this reason: an
    empty expiry list reclassified the whole panel as claim instruments instead of none of it.
    The assertion inside `correction_cost` caught it; this keeps the hole shut.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import pandas as pd
    import population as pop
    txt = pd.Series(["SPACEX SER A", "ACME CVR", "WIDGET RTS EXP 09/16/17"])
    assert not pop._any(txt, {}).any()
    assert pop._any(txt, {"cvr": r"\bCVR\b"}).tolist() == [False, True, False]


def test_section_5_3_reports_what_its_corrections_actually_cost():
    """The sentence was prose for three rounds and drifted twice without complaint."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import population as pop
    c = pop.correction_cost()
    assert c["rows_removed"] > 1000, "the corrections stopped removing anything"
    assert c["cells"] < 0, "they are supposed to cost cells on net"
    assert 0.2 < c["median_pts"] < 0.5


def test_the_panel_cache_is_keyed_so_it_cannot_go_stale():
    """A stale panel cache would be a wrong number in every figure at once.

    Added after a reader reported the registry and the event study exhausting memory in one
    process: both hold the panel, and rebuilding it from the gzip in each stage is what makes
    two copies expensive. The key is the source file's mtime and size, so a rebuilt marks file
    misses rather than being silently reused, and the cache lives outside anything that ships.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import population as pop
    key = pop._cache_key()
    assert key and "-" in key
    st = pop.MARKS.stat()
    assert key == f"{int(st.st_mtime)}-{st.st_size}"
    assert "_work" in str(pop.PANEL_CACHE), "the cache must not sit anywhere that ships"
    d, c = pop.panel()
    assert len(d) > 100_000 and len(c) > 1_000


def test_no_reported_cell_counts_one_registrant_as_two_houses():
    """The paper's whole §4.1 argument is that one filer is one opinion. This checks it holds.

    `fund_complex.complex_of` is keyed on REGISTRANT_NAME, and a registrant that renames itself
    files under two names — CIK 794458 appears as both "EMERGING MARKETS GROWTH FUND INC" and
    "Emerging Markets Equities Fund Inc". Neither is a spelling variant the map folds; they are
    different names, so they become two houses, and a cell holding both would count one legal
    filer as two independent views. That is precisely the error the correction from 0.004% to
    12.1% exists to remove, reintroduced through the back door.

    Thirty-seven company-dates in the raw frame do contain a CIK under two house labels. None
    of them clears the panel bar, so nothing reported is affected — but "none of them clears
    the bar" is a fact about today's data, not a property of the code, and the next quarter of
    filings can change it without anyone editing a line. Hence a test rather than a comment.
    """
    d, _ = pop.panel()
    cells = pop.cells(d)
    reported = set(zip(cells.company, cells.dt))
    per = d.groupby(["company", "dt", "CIK"]).house.nunique()
    doubled = {(c, t) for (c, t, _), n in per.items() if n > 1}
    assert reported, "no reported cells at all; this check would be vacuous"
    assert len(per) > 10_000, f"only {len(per)} company-date-CIK groups scanned"
    # The scan must be able to see the phenomenon at all, or a green result means only
    # that it looked in the wrong column. Thirty-seven such cells exist in the frame.
    assert doubled, "the scan finds no CIK under two houses anywhere; it is not reading "\
                    "what it claims to read"
    overlap = sorted(doubled & reported)
    assert not overlap, (
        f"{len(overlap)} reported cell(s) count one registrant as two houses, which is the "
        f"double-counting §4.1 removes: {overlap[:5]}")


def _cell(marks):
    """One company-date whose houses carry the given prices, as `comparable` would deliver."""
    return pd.DataFrame({
        "company": ["C"] * len(marks), "dt": ["2024-03-31"] * len(marks),
        "house": [f"H{i}" for i in range(len(marks))], "pps": marks,
        "fund": [f"F{i}" for i in range(len(marks))], "val_usd": [1e6] * len(marks),
        "is_wrapper": False, "INVESTMENT_COUNTRY": "US",
        "ISSUER_TITLE": "COMMON STOCK", "ISSUER_NAME": "C",
    })


def test_the_pairwise_statistic_does_not_grow_with_the_house_count(monkeypatch):
    """The whole point of the second column, asserted on a case with a known answer.

    `spread_pct` is a maximum over a minimum, so adding houses that sit between the extremes
    cannot lower it and usually raises it. That is why the headline is part coverage: two-house
    cells are 39% of the panel at a median of 0.94%, six-house cells sit at 29.63%. The pair
    statistic has to be immune to that, and immunity is a property of the estimator rather than
    of this panel, so it is checked on constructed prices instead of measured ones.

    Two houses at 100 and 200, then eight more piled at 100. The end-to-end spread is 100% in
    both cases. The median pair collapses, because almost every pair is now 100 against 100.
    """
    two = cov.pairwise_spread(_cell([100.0, 200.0]),
                              pd.DataFrame({"company": ["C"], "dt": ["2024-03-31"],
                                            "guarded": [True], "nav": [1e6]}))
    ten = cov.pairwise_spread(_cell([100.0, 200.0] + [100.0] * 8),
                              pd.DataFrame({"company": ["C"], "dt": ["2024-03-31"],
                                            "guarded": [True], "nav": [1e6]}))
    assert len(two) == 1 and len(ten) == 1
    assert two.spread_pct.iloc[0] == pytest.approx(100.0)
    assert ten.spread_pct.iloc[0] == pytest.approx(100.0), "the end-to-end spread must not move"
    assert two.pairwise_pct.iloc[0] == pytest.approx(100.0), (
        "with one pair the two statistics are the same measurement")
    assert ten.pairwise_pct.iloc[0] == pytest.approx(0.0, abs=1e-9), (
        "eight houses agreeing to the cent must pull the typical pair to zero; it did not, so "
        "the statistic is not the pairwise median it claims to be")


def test_the_coverage_gradient_and_the_panel_median_are_the_same_cells():
    """A gradient over a different denominator than the headline would explain nothing.

    The bands must partition the guarded panel exactly: same cells, same total, and the
    cell-weighted medians must bracket the panel median rather than sit off to one side.
    """
    d, c = pop.panel()
    g = cov.coverage_gradient(d, c)
    guarded = c[c.guarded]
    assert int(g.cells.sum()) == len(guarded), (
        f"the gradient covers {int(g.cells.sum())} cells against the panel's {len(guarded)}")
    assert set(g.band) == {2, 3, 4, 5, 6}, f"bands are {sorted(g.band)}"
    lo, hi = g.median_spread.min(), g.median_spread.max()
    assert lo <= guarded.spread_pct.median() <= hi, (
        "the panel median falls outside every band median, which is arithmetically impossible "
        "unless the two are computed on different cells")
    # The finding the table exists to show, asserted so it cannot quietly stop being true.
    assert g.set_index("band").loc[2, "median_spread"] < 2.0
    assert g.set_index("band").loc[6, "median_spread"] > 25.0


def test_the_calendar_path_is_not_explained_by_coverage():
    """The paper says composition runs the other way. That is a claim, so it is checked."""
    _d, c = pop.panel()
    p = cov.calendar_path(c).set_index("year")
    assert int(p.cells.sum()) == len(c[c.guarded])
    full = p.loc[2019:2025]
    assert full.mean_houses.is_monotonic_decreasing, (
        "mean houses per cell no longer falls monotonically 2019-2025; the paper's argument "
        "that the rising spread cannot be composition rests on exactly that")
    assert p.loc[2021, "median_spread"] < p.loc[2019, "median_spread"], "2021 is the trough"
    assert p.loc[2024, "median_spread"] > 2 * p.loc[2021, "median_spread"]


def test_the_quiet_rebuild_matches_the_pinned_one():
    """`coverage_regimes` rebuilds the no-house-moved selection, and a rebuild can drift.

    The registration pins `population.py`, so the post-hoc work cannot import a private helper
    out of it or add one to it, and `staleness` returns counts rather than keys. The selection
    is therefore written twice. Two copies of a rule are two rules the moment one is edited,
    and the only thing standing between them is this assertion: the rebuilt frame must hold
    exactly as many cells as the pinned function counts, on the same panel.
    """
    d, c = pop.panel()
    assert len(cov.quiet_cells(d, c)) == pop.staleness(d, c)["quiet"], (
        "the rebuilt quiet selection and the pinned one disagree; §6.2's intersection is "
        "computed on a different subsample from the 760 it is described as narrowing")
    assert len(cov.fully_named_cells(d, c)) == pop.series_composition(d, c)["fully_named"]["cells"]


def test_the_intersection_is_a_subset_of_both_parents():
    """A count that is not a subset of both would be measuring something else entirely."""
    d, c = pop.panel()
    q = cov.quiet_cells(d, c)
    f = cov.fully_named_cells(d, c)
    r = cov.no_move_one_letter(d, c)
    assert r["both"] <= min(len(q), len(f))
    assert r["both_above_24"] <= r["both_nonzero"] <= r["both"]
    # And it must not be vacuous: an empty intersection would be a finding, but it is not this
    # one, and the paper states a count that a silent emptying would contradict.
    assert r["both"] > 0, "the intersection is empty; §6.2 states 132 cells"


def test_the_outlier_is_identified_leave_one_out_not_against_a_consensus_it_is_in():
    """With three houses the middle one is zero against the cell median, by construction.

    A house compared to a consensus computed including itself cannot be far from it, and the
    middle house of three is exactly at it. Leave-one-out is what makes "furthest from the
    others" mean anything. Built by hand: 100, 101 and 200. The outlier is unambiguous and its
    deviation is measured against the median of the two it leaves, not against all three.
    """
    marks = [100.0, 101.0, 200.0]
    cell = _cell(marks)
    guarded = pd.DataFrame({"company": ["C"], "dt": ["2024-03-31"], "guarded": [True],
                            "nav": [1e6]})
    r = cov.outlier_structure(cell, guarded, min_cells=1)
    assert r["cells"] == 1
    # 200 against the median of {100, 101} = 100.5. ln(200/100.5) = 0.6883, which is 68.83
    # log points and 99.0% arithmetic; the reported figure is the arithmetic one.
    assert r["outlier_dev_log_points"] == pytest.approx(68.83, abs=0.05), (
        "the deviation is being measured against a consensus the outlier is inside")
    assert r["outlier_dev"] == pytest.approx(99.0, abs=0.05)
    assert r["rest_spread"] == pytest.approx(1.0, abs=0.01), "101/100 - 1 is one per cent"
    assert r["above_pct"] == pytest.approx(100.0)


def test_the_outlier_repeat_rate_beats_its_own_resampled_null():
    """The claim §5.1 makes, and the null it makes it against, on the real panel.

    A repeat rate means nothing without the null, because a cell of three hands out a one in
    three chance and a cell of six a one in six. The null is drawn from the houses actually in
    each cell rather than assumed, and the test asserts the gap rather than the level so it
    survives the panel growing.
    """
    d, c = pop.panel()
    r = cov.outlier_structure(d, c)
    assert r["pairs"] > 1000, f"only {r['pairs']} pairs; the comparison is thin"
    assert r["repeat_pct"] > 2 * r["null_mean"], (
        f"repeat {r['repeat_pct']:.1f}% against null {r['null_mean']:.1f}%: the claim that the "
        "outlier is a house rather than an accident of the quarter no longer holds")
    assert r["null_max"] < r["repeat_pct"], "some resampled draw reached the observed rate"
    # And the house table must be a ratio against each house's own coverage, not a raw rate:
    # a house living in three-house cells is the outlier a third of the time by chance.
    tab = r["table"]
    assert (tab.baseline > 0).all()
    assert tab.ratio.max() > 2 and tab.ratio.min() < 0.2, "the house spread has collapsed"


def test_the_outlier_choice_does_not_depend_on_row_order():
    """Fifty-seven cells have two houses the same distance from the others, and a rule decides.

    Of the 2,586 cells carrying three or more houses, 57 have two or more of them within
    `TIE_EPS` of the furthest, and in six of those the tied deviations are not equal bit for
    bit. So the choice is a rule, not a reading: an independent replication of this function
    got 1,489 pairs and 66.7% against 1,490 and 66.3%. Sorting by house name and taking the
    first inside the tolerance is arbitrary and it is the same everywhere, which is all a
    tie-break has to be.

    Shuffling the input rows is NOT the test, though the first version of this thought it was.
    `_house_marks` groups by company, date and house, and a group median does not care what
    order it was given, so the shuffle cannot reach the tie-break: restoring the `argmax` this
    test is named for leaves the shuffled and unshuffled answers identical, and the test passed
    on the bug. The shuffle stays as the cheap half, and the half that can fail is below it: a
    cell built with two houses tied inside the tolerance, handed over in both orders, has to
    name the same house both times. Remove the sort and it names whichever came first, which
    is what this proves. It does NOT prove the tolerance: restoring `argmax` leaves it green,
    because this fixture's two candidates happen to fall the same way bit-for-bit.
    `test_the_outlier_survives_a_perturbation_the_size_of_a_libm_difference` is the half that
    catches that, and the two are not interchangeable.
    """
    d, c = pop.panel()
    straight = cov.outlier_structure(d, c)
    shuffled = cov.outlier_structure(d.sample(frac=1.0, random_state=7), c)
    for k in ("cells", "pairs", "repeat_pct", "outlier_dev", "rest_spread", "above_pct"):
        assert straight[k] == pytest.approx(shuffled[k]), (
            f"{k} moves when the input rows are shuffled: {straight[k]} against {shuffled[k]}")

    # 80, 100, 125, 156.25 is a geometric ladder, so the two outside houses are the same
    # distance from the median of the others: |dev| is 44.628710263 for both, 22.314355131 for
    # both middles. They are NOT bit-equal — the two logarithms land 7.1e-15 apart — which is
    # the real case, and why the tolerance and not `argmax` decides it. ALPHA sorts before
    # ZEBRA, so ALPHA is named whichever order the rows arrive in.
    fam = pd.DataFrame([{"company": "X", "dt": dt, "house": h, "pps": v}
                        for dt in ("2024-03-31", "2024-06-30")
                        for h, v in (("ALPHA", 156.25), ("BRAVO", 100.0),
                                     ("CHARLIE", 125.0), ("ZEBRA", 80.0))])
    fam["dt"] = pd.to_datetime(fam.dt)
    top = sorted(abs(x) for x in
                 [np.log(v / np.median([u for u in (156.25, 100.0, 125.0, 80.0) if u != v]))
                  for v in (156.25, 100.0, 125.0, 80.0)])
    assert 0 < top[-1] - top[-2] < cov.TIE_EPS, (
        f"the fixture's two furthest houses are {top[-1] - top[-2]:.2e} apart; it has to be "
        f"inside TIE_EPS={cov.TIE_EPS:g} and outside zero, or it is not testing a tolerance")
    picked = set()
    for order in (fam, fam.iloc[::-1]):
        rows, *_ = cov._outlier_rows(order)
        assert len(rows) == 2, f"the fixture stopped producing two cells: {len(rows)}"
        picked.update(r["out"] for r in rows)
    assert picked == {"ALPHA"}, (
        f"a cell whose two furthest houses are tied within TIE_EPS named {sorted(picked)}; "
        "the tie-break is following row order, not the house name")


def test_the_outlier_deviation_is_arithmetic_like_every_other_spread():
    """18.23 log points and 0.35 per cent sat in one sentence behind one per-cent sign.

    Every spread this paper prints is `exp(x) - 1`, and this one was the raw log ratio. The
    two are 18.23 and 20.0 for the same cells, which is a fifth of the quantity in dispute.
    """
    d, c = pop.panel()
    r = cov.outlier_structure(d, c)
    assert r["outlier_dev"] == pytest.approx(
        (np.exp(r["outlier_dev_log_points"] / 100) - 1) * 100, abs=1e-9)
    assert r["outlier_dev"] > r["outlier_dev_log_points"], (
        "the reported deviation is still in log points")


def test_the_outlier_survives_a_perturbation_the_size_of_a_libm_difference():
    """Sorting the rows fixed the ORDER of the tie-break and not its CONTENTS.

    Exact equality asks whether two `np.log` results agree to the last bit, and libm builds
    disagree there. The same code on the same data found 286 tie cells on one platform and 292
    on another; medians and ratios did not notice, but `repeat_pct` is a chain — one cell's
    outlier is compared against the next cell's — so a handful of flipped ties compounded into
    66.31 against 66.64, seven times the registered tolerance.

    A row shuffle cannot see this: it varies the order within one machine's arithmetic. What
    varies between machines is the last bit of a logarithm, so that is what is varied here.
    Every price is nudged by a relative 1e-15, which is the scale of the disagreement, and
    every reported statistic has to come back the same.
    """
    d, c = pop.panel()
    rng = np.random.default_rng(11)
    jittered = d.copy()
    jittered["pps"] = d.pps.to_numpy() * (1 + rng.choice([-1.0, 1.0], len(d)) * 1e-15)
    base, moved = cov.outlier_structure(d, c), cov.outlier_structure(jittered, c)
    for k in ("cells", "pairs", "repeat_pct", "above_pct", "outlier_dev", "rest_spread",
              "houses", "ratio_min", "ratio_max"):
        assert base[k] == pytest.approx(moved[k], rel=1e-12), (
            f"{k} moves when prices are nudged by one part in 1e15: {base[k]} against "
            f"{moved[k]}. The tie-break is deciding on bits, so this number is a property of "
            "the machine that computed it")


def test_the_tie_epsilon_sits_in_an_empty_band():
    """`TIE_EPS` is a threshold, and a threshold with data either side of it is a judgement.

    This one is not. Between the largest deviation in a cell and each of the others there is a
    gap; over the whole panel those gaps are bimodal. Floating-point noise on identical marks
    lands below 1e-11 log points and a real difference lands at 1e-9 or above, with nothing in
    between, so any epsilon inside the gap gives the same tie set and the choice cannot matter.
    The test is that the gap stays empty — if the data ever puts a deviation there, the
    epsilon starts deciding something and has to be argued for instead of measured.
    """
    d, c = pop.panel()
    fam = cov._house_marks(d, c)
    noise, real, inside = 0, 0, []
    cells = 0
    for _key, s in fam.groupby(["company", "dt"]):
        v = s.sort_values("house", kind="stable").pps.values
        if len(v) < 3:
            continue
        cells += 1
        mag = np.abs([np.log(v[i] / np.median(np.delete(v, i))) * 100 for i in range(len(v))])
        for gap in mag.max() - mag:
            if gap <= 0:
                continue
            if gap < 1e-11:
                noise += 1
            elif gap >= 1e-9:
                real += 1
            else:
                inside.append(gap)
    assert cells > 2000, f"only {cells} cells scanned; the band check is not reading the panel"
    assert noise > 50, f"only {noise} gaps at noise scale — the bimodality has gone"
    assert real > 50, f"only {real} gaps at real scale — the bimodality has gone"
    assert not inside, (
        f"{len(inside)} deviation gap(s) sit between 1e-11 and 1e-9 log points, where "
        f"cov.TIE_EPS={cov.TIE_EPS:g} decides the outlier: {sorted(inside)[:5]}. The epsilon "
        "is no longer measured from an empty band and has to be argued for.")
    assert 1e-11 < cov.TIE_EPS < 1e-9, "TIE_EPS has moved out of the empty band"
