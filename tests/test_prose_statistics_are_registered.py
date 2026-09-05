"""The registry runs one way. This is the other way, for the class where it bit.

`reproduce.py` takes every registered figure, recomputes it from production code and requires
its token in the prose. Nothing runs the reverse: a number typed into the manuscript and never
registered is invisible to every guard in this repository. Five were found by reading, and the
fifth was not merely unpinned but wrong — §4.2 said the single-lot within-house median was
"four ten-thousandths" where the value is 0.000109, and nothing could object because nothing
recomputed it.

WHY THIS IS A CEILING AND NOT A LIST
A scan over every digit in the paper returns 220 residuals and cannot be closed at a readable
size: table cells carry their own guards, arithmetic shown in the text is checked by
the arithmetic audit, and dates, CUSIPs, accession numbers and other authors' figures are
legitimately unregistered. Narrowed to the class the defect lived in — a percentage, a p-value
or a point-valued statistic asserted in a prose sentence — the residual is small enough to
count. Naming each of the twenty would be a list nobody re-reads; a count fails the moment a
twenty-first appears, which is the only event worth stopping.

The number is what the manuscript measured at the round it was written, not a target. Lowering
it is the work; raising it needs a reason written beside it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import paper_numbers as pn

DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")

# A percentage, a p-value, or a statistic in points. The three shapes the manuscript states a
# measured quantity in when it is making a claim in a sentence.
STAT = re.compile(
    r"(?<![\w.])(\d{1,3}(?:\.\d+)?)%"
    r"|p=(\d?\.\d+|0)"
    r"|(?<![\w.])(\d{1,3}\.\d+)\s+(?:points?|percentage points?|basis points?)"
    r"|(?<![\w.])(\d?\.\d+)\s+of\s+a\s+point")
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")

# There was a FOREIGN list here — Gornall-Strebulaev's 48%, the 24% threshold, 50 and 100 used
# as fractions — on the reasoning that no code here computes another author's figure. Every one
# of its six entries turned out to be covered by a registry token already, because a bare
# two-digit integer collides with something among 435 pinned values whatever it means. The list
# excluded nothing and was written as though it did. `test_every_exemption_is_still_earning_its
# _place` is what found that, on the round it was added, which is the only reason it is not
# still sitting here looking useful.

# Markups and ratios printed to six decimals to demonstrate that two filings agree exactly.
# They are arithmetic on the page, not statistics about the panel, and the arithmetic audit
# checks the relations they sit in.
SHOWN_ARITHMETIC = re.compile(r"\d+\.\d{4,}")

# Figures the paper names in order to withdraw them. These cannot be registered even in
# principle: the code that produced them does not exist any more, which is what withdrawing a
# result means. They are a class, not a gap, and the title page says so — `reproduce.py`
# recomputes every figure the paper ASSERTS. §6.3's 169x is the third and the scan does not
# reach it, because a multiple is not one of the three shapes read here.
DISOWNED = {
    "12.6": "§5.1's superseded house-level median, kept because it bounds the correction's "
            "direction: splitting one house into thirty trusts can only make funds look more "
            "agreeing, so the corrected figure cannot be an artifact of the correction",
    "0.12": "C.5's superseded decomposition, kept because the factor it implied — seventy-four "
            "rather than eleven — is what the series-pattern error cost",
}

UNREGISTERED_PROSE_STATISTICS = 12


def _tokens() -> set[str]:
    out: set[str] = set()
    for n in pn.canonical_numbers():
        for f in ("%g", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f", "%d"):
            try:
                s = (f % n.value).lstrip("-")
            except (TypeError, ValueError):
                continue
            out.add(s)
            out.add(s.rstrip("0").rstrip(".") or "0")
        for src in (n.claim or "", *(n.context or {}).values()):
            for tok in NUM.findall(src):
                bare = tok.replace(",", "")
                out.add(bare)
                out.add(bare.rstrip("0").rstrip(".") or "0")
    return out


def _residual(draft: str, known: set[str]) -> dict[str, set[str]]:
    miss: dict[str, set[str]] = {}
    sec = ""
    for ln in draft.split("\n"):
        if ln.startswith("#"):
            sec = ln.strip("# ").strip()[:40]
            continue
        if ln.lstrip().startswith("|") or ln.startswith("```") or not ln.strip():
            continue
        for m in STAT.finditer(ln):
            raw = next(g for g in m.groups() if g)
            bare = raw.replace(",", "")
            if bare in known or (bare.rstrip("0").rstrip(".") or "0") in known:
                continue
            if bare in DISOWNED or SHOWN_ARITHMETIC.fullmatch(bare):
                continue
            miss.setdefault(raw, set()).add(sec)
    return miss


@pytest.fixture(scope="module")
def known():
    return _tokens()


def test_the_scan_reads_the_manuscript(known):
    """Vacuous against an empty extraction, which is how this kind of guard dies quietly."""
    body = re.split(r"^## References", DRAFT, flags=re.M)[0]
    found = [next(g for g in m.groups() if g) for m in STAT.finditer(body)]
    assert len(found) > 200, f"the scan found only {len(found)} stated statistics"
    assert len(known) > 1000, f"the registry offered only {len(known)} tokens to match against"


def test_no_new_statistic_enters_the_prose_unregistered(known):
    body = re.split(r"^## References", DRAFT, flags=re.M)[0]
    miss = _residual(body, known)
    assert len(miss) <= UNREGISTERED_PROSE_STATISTICS, (
        f"{len(miss)} prose statistics have no registry token, against a ceiling of "
        f"{UNREGISTERED_PROSE_STATISTICS}. A figure nothing recomputes cannot be checked "
        f"against anything, and one of these was simply wrong for several rounds. Register the "
        f"new one rather than raising the number:\n  "
        + "\n  ".join(f"{k}  {sorted(v)}" for k, v in sorted(miss.items())))


def test_the_ceiling_is_not_slack(known):
    """A ceiling far above the count stops nothing. This keeps it tight enough to bite."""
    body = re.split(r"^## References", DRAFT, flags=re.M)[0]
    n = len(_residual(body, known))
    assert n >= UNREGISTERED_PROSE_STATISTICS - 3, (
        f"the residual is {n} against a ceiling of {UNREGISTERED_PROSE_STATISTICS}: figures "
        f"were registered and the ceiling was not lowered with them. Lower it to {n}.")


def test_every_exemption_is_still_earning_its_place(known):
    """A dead exemption is a hole nobody is watching, and both lists are small enough to check.

    Each entry has to be a statistic the manuscript still states AND one the registry still
    does not pin: an exemption for a figure that has since been registered is dead, and one for
    a figure that has been cut is dead in the other direction.
    """
    body = re.split(r"^## References", DRAFT, flags=re.M)[0]
    stated = {next(g for g in m.groups() if g) for m in STAT.finditer(body)}
    gone = sorted(k for k in DISOWNED if k not in stated)
    assert not gone, f"DISOWNED exempts figures the paper no longer states: {gone}"
    pinned = sorted(k for k in DISOWNED
                    if k in known or (k.rstrip("0").rstrip(".") or "0") in known)
    assert not pinned, (
        f"DISOWNED exempts figures the registry now pins, so the exemption excludes nothing "
        f"and the ceiling should fall with it: {pinned}")


def test_the_scan_fires_on_a_defect_it_would_have_caught(known):
    """Shown failing on a real one, and honest about which.

    Of the five unregistered figures found by reading, this scan would have caught three:
    §8.1's 10.71% and its 18% phase null, and §8.5's p=0.076. It would NOT have caught §4.2's
    median, because that one was spelled out — "four ten-thousandths" — and a scan for digits
    cannot see a number written as words. That is the residual hole in this guard and it is
    stated here rather than left for someone to discover.

    §8.1's sentence is the fixture, in the shape it had before it was cut.
    """
    fixture = ("Its pooled profile ran from 0.01% at the round month to 10.71% nine months "
               "later, and a phase-randomised null reproduced the shape 18% of the time.\n")
    miss = _residual(fixture, known)
    assert "10.71" in miss, f"the scan no longer sees an unregistered percentage: {miss}"

    assert not _residual("| a table row | 10.71% | 13.8 points |\n", known), (
        "a table cell is counted, and tables have their own guards")
    assert not _residual("The median gap is 12.1% between houses.\n", known), (
        "a registered figure is reported as unregistered")
