"""The external validation of the house map, and the two ways it could report nothing.

A referee's central objection: the correction from 0.004% to 12.1% rests on a registrant-to-
house map that is mine, checked only against the data it was built on. Form N-CEN names the
adviser of each series, so the SEC can be asked the same question independently.

The harvest needs a route to sec.gov; the comparison does not, and runs off the committed
extract. Most of what is checked here is built by hand, because the failure mode of a
validation like this one is not a wrong answer — it is an empty one, and an empty one is
indistinguishable from a clean bill of health. The first run returned 1,167 rows with no
adviser on any of them and cheerfully reported nought disagreements; the four guards at the
foot of this file are the four separate ways it managed that.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import ncen_advisers as nc


def test_the_normaliser_folds_the_spellings_one_adviser_files_under():
    """One adviser writes its own name several ways across its own registrants, and the
    difference is a suffix or a connective. What the normaliser must NOT do is fold two
    genuinely different advisers, which is the second half of this test.

    It also does not expand an acronym: `FMR Co., Inc.` stays `fmr` and does not join
    `fidelity management research`. That is deliberate — expanding acronyms is name matching
    by similarity, which section 3.2 refuses — and it is why `houses_with_two_advisers` is an
    upper bound on wrong merges rather than a count of them.
    """
    same = {"Fidelity Management & Research Company LLC",
            "Fidelity Management and Research Co., Inc.",
            "FIDELITY MANAGEMENT & RESEARCH COMPANY"}
    keys = {nc.normalise(s) for s in same}
    assert len(keys) == 1, f"one adviser under three spellings gave {keys}"

    different = ["T. Rowe Price Associates, Inc.", "BlackRock Advisors, LLC",
                 "Capital Research and Management Company", "Alger Management, Inc."]
    assert len({nc.normalise(s) for s in different}) == len(different)
    # And it must not reduce a name to nothing: "Capital Group" is all suffix words.
    assert all(nc.normalise(s) for s in different), "a name normalised away to the empty string"


def test_an_empty_extract_stops_rather_than_reporting_no_problems(tmp_path, monkeypatch):
    """The failure this module is most likely to have. A harvest behind a blocked route
    writes a row per registrant with no adviser on any of them, and a comparison over no
    comparisons finds no disagreements — a validation that passes by looking at nothing.
    """
    empty = tmp_path / "ncen_advisers.csv"
    pd.DataFrame({"CIK": range(50), "ncen_accession": [""] * 50,
                  "advisers": [""] * 50}).to_csv(empty, index=False)
    monkeypatch.setattr(nc, "OUT", empty)
    with pytest.raises(SystemExit, match="rows name an adviser"):
        nc.load()

    # And the other direction: an extract that IS populated must load.
    full = tmp_path / "full.csv"
    pd.DataFrame({"CIK": range(50), "ncen_accession": ["0001-25-1"] * 50,
                  "advisers": ["Some Adviser LLC"] * 50}).to_csv(full, index=False)
    monkeypatch.setattr(nc, "OUT", full)
    assert len(nc.load()) == 50


def test_the_comparison_finds_a_merge_that_is_wrong(monkeypatch):
    """The direction that would damage the paper: two registrants this map calls one house,
    filing two different advisers. Built by hand so the answer is known."""
    ncen = pd.DataFrame({
        "CIK": [1, 2, 3, 4],
        "ncen_accession": ["a", "b", "c", "d"],
        "advisers": ["Fidelity Management & Research Company LLC",
                     "Fidelity Management and Research Co., Inc.",
                     "T. Rowe Price Associates, Inc.",
                     "BlackRock Advisors, LLC"]})
    panel = pd.DataFrame({"CIK": [1, 2, 3, 4],
                          "REGISTRANT_NAME": ["R1", "R2", "R3", "R4"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel, None))

    # A map that calls R1 and R2 one house is right: one adviser under two spellings.
    monkeypatch.setattr(nc, "complex_of", {"R1": "Fidelity", "R2": "Fidelity",
                                           "R3": "T. Rowe", "R4": "BlackRock"}.get)
    good = nc.compare(ncen)
    assert good["houses_with_two_advisers"] == 0
    assert good["multi_registrant_houses"] == 1, "the check has no merged house to look at"

    # A map that calls R3 and R4 one house is wrong, and this has to say so.
    monkeypatch.setattr(nc, "complex_of", {"R1": "Fidelity", "R2": "Fidelity",
                                           "R3": "Wrong", "R4": "Wrong"}.get)
    bad = nc.compare(ncen)
    assert bad["houses_with_two_advisers"] == 1
    assert bad["split_detail"]["Wrong"] == 2


def test_the_comparison_finds_a_merge_that_is_missing(monkeypatch):
    """The other direction, which the map's fail-closed rule permits: two registrants left
    apart that file one adviser. It costs coverage and can only make the reported
    disagreement smaller, so it is reported separately rather than as an error."""
    ncen = pd.DataFrame({"CIK": [1, 2], "ncen_accession": ["a", "b"],
                         "advisers": ["Alger Management, Inc.", "ALGER MANAGEMENT INC"]})
    panel = pd.DataFrame({"CIK": [1, 2], "REGISTRANT_NAME": ["R1", "R2"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel, None))
    monkeypatch.setattr(nc, "complex_of", {"R1": "Alger", "R2": "Alger Institutional"}.get)
    r = nc.compare(ncen)
    assert r["advisers_split_across_houses"] == 1
    assert r["houses_with_two_advisers"] == 0


# ---------------------------------------------------------------------------------------
# Four defects the harvest had while it looked designed, found only by running it. Each one
# returned a comforting answer: no adviser, no N-CEN, no problem. These are the guards.
# ---------------------------------------------------------------------------------------

# A fragment of the real filing — Fidelity Salem Street Trust's N-CEN, accession
# 0000035402-26-004290 — kept verbatim, ampersand entity and all.
_REAL = """      <investmentAdvisers>
        <investmentAdviser>
          <investmentAdviserName>Fidelity Management &amp; Research Company LLC</investmentAdviserName>
          <investmentAdviserFileNo>801-7884</investmentAdviserFileNo>
        </investmentAdviser>
      </investmentAdvisers>"""


def test_the_adviser_pattern_matches_the_tag_the_sec_actually_writes():
    """The pattern looked for `adviserName`. The SEC writes `investmentAdviserName`.

    It matched nothing, on every filing, and a filing that parses to zero advisers was
    indistinguishable from a registrant that files none — so the harvest reported a clean map
    from an empty parse. Nothing here had ever been run against a real document.
    """
    assert nc._ADVISER.findall(_REAL) == ["Fidelity Management &amp; Research Company LLC"]


def test_the_entity_reference_is_resolved_before_the_name_is_normalised(monkeypatch):
    """`&amp;` normalises to the word "amp", which splits a house from itself.

    The flat files give the name with a literal ampersand and the filing gives it escaped, so
    a house read from one source would not fold with the same house read from the other — and
    that shows up as the one failure this module exists to detect.

    The first version of this test called `html.unescape` itself and compared the result to
    `normalise`. That proves Python unescapes entities, which was not in doubt; it says
    nothing about whether `_advisers` does it. It goes through `_advisers` now.
    """
    monkeypatch.setattr(nc, "_get", lambda _url: _REAL.encode())
    names = nc._advisers(42, "0000-24-000001")
    assert names == ["Fidelity Management & Research Company LLC"]
    assert nc.normalise(names[0]) == nc.normalise(
        "Fidelity Management and Research Co., Inc.") == "fidelity management research"


def test_a_transport_failure_raises_instead_of_reporting_nothing_there(monkeypatch):
    """An empty CA bundle used to come back as "this registrant files no N-CEN"."""
    import urllib.error
    import urllib.request

    def boom(*a, **k):
        raise urllib.error.URLError("CERTIFICATE_VERIFY_FAILED")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(nc.Unreachable):
        nc._get("https://data.sec.gov/submissions/CIK0000000001.json")


def test_a_real_404_is_still_an_answer(monkeypatch):
    """The raise above must not swallow the honest case, or every clone stops on nothing."""
    import urllib.error
    import urllib.request

    def missing(*a, **k):
        raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", missing)
    assert nc._get("https://data.sec.gov/submissions/CIK0000000001.json") is None


def test_an_n_cen_outside_the_recent_window_is_still_found(monkeypatch):
    """`filings.recent` is capped, and the cap bites the biggest houses hardest.

    Fidelity Salem Street Trust holds 1,003 filings in `recent` and not one is an N-CEN; the
    N-CEN sits in one of three overflow files. Reading only `recent` reported the largest
    complexes in the panel as filing no N-CEN at all — and reported it as a clean result, on
    exactly the registrants whose merge the map most depends on.
    """
    import json
    pages = {
        "https://data.sec.gov/submissions/CIK0000000042.json": json.dumps({"filings": {
            "recent": {"form": ["NPORT-P"] * 3, "accessionNumber": ["x-1", "x-2", "x-3"]},
            "files": [{"name": "CIK0000000042-submissions-001.json"}]}}).encode(),
        "https://data.sec.gov/submissions/CIK0000000042-submissions-001.json": json.dumps({
            "form": ["485BPOS", "N-CEN"], "accessionNumber": ["y-1", "0000-24-000001"],
        }).encode(),
    }
    monkeypatch.setattr(nc, "_get", lambda url: pages.get(url))
    monkeypatch.setattr(nc.time, "sleep", lambda *_: None)
    assert nc._latest_ncen(42) == "0000-24-000001"


def test_reading_only_the_recent_window_would_have_missed_it(monkeypatch):
    """The test above passes trivially if the overflow is never the only place it lives."""
    import json
    monkeypatch.setattr(nc, "_get", lambda _url: json.dumps({"filings": {
        "recent": {"form": ["NPORT-P"], "accessionNumber": ["x-1"]}, "files": []}}).encode())
    monkeypatch.setattr(nc.time, "sleep", lambda *_: None)
    assert nc._latest_ncen(42) is None


def test_every_house_that_splits_has_been_read_and_every_reading_is_live():
    """§4.1 says not one of the twenty-two fuses two unrelated firms. That is a claim about a
    set the code recomputes, so the set and the reading of it must not drift apart.

    Both directions: a house that starts filing two advisers must not slip in unread, and a
    reading whose house no longer splits must not sit there implying it was checked.
    """
    if not nc.OUT.exists():
        pytest.skip("no committed extract; run `python3 src/ncen_advisers.py --harvest`")
    r = nc.compare()
    assert r["unread_splits"] == [], (
        "house(s) filing more than one adviser with no entry in READ_BY_HAND — the paper's "
        f"sentence does not cover them: {r['unread_splits']}")
    assert r["stale_readings"] == [], (
        f"READ_BY_HAND entr(ies) for a house that no longer splits: {r['stale_readings']}")
    assert sum(r["split_kinds"].values()) == r["houses_with_two_advisers"]


def test_no_adviser_in_the_real_extract_normalises_away():
    """The empty key is a silent drop, and a list of hand-picked names cannot find one.

    `test_the_normaliser_folds_the_spellings_one_adviser_files_under` already asserts that no
    name normalises to nothing — over four names I chose. In the extract, "Capital
    International, Inc." is spelled entirely out of suffix words, strips to "", and was
    dropped by `compare` from BOTH directions without a line of output saying so. The rule has
    to be read against every name in the file, with the denominator printed, or it is a rule
    about my imagination.
    """
    if not nc.OUT.exists():
        pytest.skip("no committed extract; run `python3 src/ncen_advisers.py --harvest`")
    d = pd.read_csv(nc.OUT).fillna({"advisers": ""})
    names = sorted({p.strip() for a in d.advisers for p in str(a).split(" | ") if p.strip()})
    assert len(names) > 400, f"only {len(names)} distinct adviser names — the file is thin"
    empty = [n for n in names if not nc.normalise(n)]
    assert not empty, (
        f"{len(empty)} of {len(names)} adviser names normalise to the empty string and are "
        f"dropped from the comparison in silence: {empty}")


def test_the_comparison_says_how_many_rows_it_threw_away():
    """A count of nothing thrown away is the claim; it has to be made, not assumed."""
    if not nc.OUT.exists():
        pytest.skip("no committed extract; run `python3 src/ncen_advisers.py --harvest`")
    assert nc.compare()["named_but_unnormalisable"] == 0


def test_a_registrant_filing_two_advisers_is_seen_as_filing_two(monkeypatch):
    """The comparison read the FIRST adviser of each registrant and dropped the rest.

    `harvest` writes the names sorted, so "first" meant alphabetically first — Vanguard's
    external manager ARGA stood for Vanguard. Sixty-nine of the 1,161 registrants file more
    than one adviser, so six per cent of the evidence went missing, and it went missing from
    the direction that would damage the paper: two merged houses filing two advisers did not
    appear in the count at all.

    Built by hand. R1 and R2 are one house and each files the same first name, so a check
    that reads only the first sees one adviser and reports nothing.
    """
    ncen = pd.DataFrame({
        "CIK": [1, 2],
        "ncen_accession": ["a", "b"],
        "advisers": ["AAA Advisers, LLC | Unrelated Partners, LLC", "AAA Advisers, LLC"]})
    panel = pd.DataFrame({"CIK": [1, 2], "REGISTRANT_NAME": ["R1", "R2"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel, None))
    monkeypatch.setattr(nc, "complex_of", {"R1": "H", "R2": "H"}.get)
    r = nc.compare(ncen)
    assert r["houses_with_two_advisers"] == 1, (
        "a merged house filing two advisers is invisible — only the first name is being read")
    assert r["registrants_naming_several_advisers"] == 1


def test_one_registrant_under_two_names_is_not_a_merge(monkeypatch):
    """`duplicated("house")` counted a renamed trust as two registrants.

    One CIK filing under two names produces two rows, and the old rule read two rows sharing a
    house as a merge the map had made. It had made nothing: CIK 878719 files as both "THE
    ADVISORS' INNER CIRCLE FUND" and "ADVISORS' INNER CIRCLE FUND". Twenty-four of the
    seventy-nine houses the old count called merged were that, and two of them reached the
    damaging count on the strength of one trust hosting unrelated managers — which says
    nothing about a map that never merged anything there.
    """
    ncen = pd.DataFrame({"CIK": [7, 7], "ncen_accession": ["a", "a"],
                         "advisers": ["Alpha Partners, LLC | Beta Partners, LLC"] * 2})
    panel = pd.DataFrame({"CIK": [7, 7], "REGISTRANT_NAME": ["One Trust", "The One Trust"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel, None))
    monkeypatch.setattr(nc, "complex_of", {"One Trust": "H", "The One Trust": "H"}.get)
    r = nc.compare(ncen)
    assert r["multi_registrant_houses"] == 0, "one CIK under two names is not a merged house"
    assert r["houses_with_two_advisers"] == 0, (
        "a single trust hosting two managers was counted as a wrong merge")


def test_an_adviser_reaching_two_names_of_one_registrant_is_not_a_missed_merge(monkeypatch):
    """Direction two has the same trap and it cost eight of the reported hits.

    An adviser under two house labels that are one CIK is a rename, not a merge the map
    failed to make. Requiring two CIKs as well as two houses took the count from 104 to 96.
    """
    ncen = pd.DataFrame({"CIK": [7, 7], "ncen_accession": ["a", "a"],
                         "advisers": ["Solo Advisers, LLC"] * 2})
    panel = pd.DataFrame({"CIK": [7, 7], "REGISTRANT_NAME": ["Growth Fund", "Equities Fund"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel, None))
    monkeypatch.setattr(nc, "complex_of", {"Growth Fund": "A", "Equities Fund": "B"}.get)
    assert nc.compare(ncen)["advisers_split_across_houses"] == 0

    # And the real thing still registers: same adviser, two houses, two CIKs.
    ncen2 = pd.DataFrame({"CIK": [7, 8], "ncen_accession": ["a", "b"],
                          "advisers": ["Solo Advisers, LLC"] * 2})
    panel2 = pd.DataFrame({"CIK": [7, 8], "REGISTRANT_NAME": ["Growth Fund", "Equities Fund"]})
    monkeypatch.setattr(nc.pop, "panel", lambda: (panel2, None))
    assert nc.compare(ncen2)["advisers_split_across_houses"] == 1


def test_every_reading_names_an_adviser_that_is_actually_filed():
    """Four of the twenty-two reasons named entities that appear in no filing.

    "FMR" for Fidelity, "the international arm" for T. Rowe Price, a single Delaware trust for
    Macquarie, a variable-trust entity for Putnam — all written from what I expected rather
    than from the extract. A reason is a factual claim about a document, so it is checked
    against the document: every capitalised firm name in a reason must appear in the adviser
    names OR the registrant names filed under that house, or be the house's own name.

    Both columns, because a reason legitimately says which registrant an adviser is attached
    to — "Strategic Advisers on Rutland Square II" names a trust, not a firm. The first
    version searched only the adviser column and flagged five true statements, which is the
    other way a check fails: loudly, on the correct case.
    """
    if not nc.OUT.exists():
        pytest.skip("no committed extract; run `python3 src/ncen_advisers.py --harvest`")
    import re
    d, _ = nc.pop.panel()
    reg = d[["CIK", "REGISTRANT_NAME"]].drop_duplicates().assign(CIK=lambda t: t.CIK.astype(int))
    reg["house"] = reg.REGISTRANT_NAME.map(nc.complex_of)
    m = reg.merge(nc.load(), on="CIK", how="left").fillna({"advisers": ""})

    # Words a reason may use that are not firm names: the vocabulary of the explanation.
    allowed = {"Item", "The", "This", "That", "Every", "Nine", "Four", "US", "SEC", "CEN",
               "Franklin", "Income", "Credit", "Flexible", "Fund", "Which", "Both", "Title"}
    bad = []
    for house, (_kind, reason) in nc.READ_BY_HAND.items():
        rows = m[m.house == house]
        filed = (" ".join(rows.advisers) + " " + " ".join(rows.REGISTRANT_NAME)).lower()
        for word in re.findall(r"\b[A-Z][A-Za-z&.']{2,}", reason):
            if word in allowed or word.lower() in house.lower():
                continue
            if word.lower().rstrip(".,'s") not in filed:
                bad.append(f"{house}: reason names {word!r}, which no filing under it does")
    assert not bad, "reason(s) naming an entity that is not in the extract:\n  " + "\n  ".join(bad)
