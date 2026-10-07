"""One quantity stated twice has to be stated the same way.

Table 19 read "425 company-series pairs on 288 companies". Appendix C read "433 company-series
pairs on 287 companies". One quantity, two places, two answers, and every guard in this
repository was green: the registry pinned one of the two and had no opinion about the other,
`test_registry_sections` found the pinned token inside its own section, and `reproduce.py`
reported zero prose drift on a paper contradicting itself.

The registry cannot close this by construction. It compares a value against the code and a
token against the text; it has no way to notice that a *second* place states the same quantity
differently, because that second place is not registered — and if it were registered, the
collision guard would already catch it.

HOW A REPEAT IS RECOGNISED, AND THE TWO DESIGNS THAT DID NOT WORK
A sentence-level skeleton — the sentence with its numbers blanked — finds nothing here. The
two statements live in a table row and a sentence and share only a fragment, so they are never
the same sentence.

Grouping each number by the words that follow it does find them, but only after two
corrections that were made by running it rather than by thinking about it. Numbers inside the
window have to be blanked, or "425 … on 288" and "433 … on 287" hash differently and the pair
this exists for is invisible. And the window has to contain two words that are not numbers, or
every row of every table collides with every other and the report is fifty-seven groups of
digits. With both, the scan reports eleven groups on the manuscript as it stood, ten of them
benign and named below, and the eleventh is the defect.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
NUM = re.compile(r"(?<![\w.$])(\d[\d,]*(?:\.\d+)?)(%?)")
STOP = re.compile(r"^(of|to|and|or|in|on|at|the|a|an|is|are|was|were|from|per|by)$")
WINDOW = 4

# Phrases that legitimately follow more than one number. Every one was read against the
# manuscript before it was written down, and `test_the_allowances_are_all_still_live` deletes
# an entry the moment the manuscript stops producing it.
ALLOWED = {
    "against <n> for": "§7's error pair and Appendix G's spread pair, different quantities",
    "jenkinson sousa and": "two bibliography years",
    "sec edgar form": "Form 10-K against a section pointer",
    "agree to within a": "the N-CSR lot count and the family-agreement share",
    "carry two or more": "N-CSR lots and dated rounds, different objects",
    "cells on <n> companies": "three different cell counts, each its own selection",
    "funds across <n> houses": "the wedge panel's funds and a line join",
    "of the booked value": "the verified-label share and the classified share",
    "of <n> untied anchors": "three counts of untied anchors, each its own selection: §8.5's "
                             "widest ladder rung, §8.4's top house at the round, and §8.4's "
                             "three placebo anchors pooled",
}
# §8.3's placebo table and §8.4's decomposition run the same four anchors. When Table 21 was
# first written it reused Table 9's row labels, every label came to carry one number from each
# table, and closing that took SEVEN new entries above — a 70% widening of a list whose whole
# value is that it is short enough to read. The collision was in the manuscript, not in the
# scan, so the fix belongs there too: Table 21 names where its anchor was PLACED ("the round
# itself", "six months earlier") where Table 9 names an offset ("the round", "six months
# before"). Six allowances went away and the wording is more accurate than what it replaced.
# The lesson is recorded here because the cheap move was the wrong one and it was available.


def _groups(text: str) -> dict[str, set[str]]:
    flat = " ".join(ln for ln in text.split("\n") if not ln.startswith(("#", "```")))
    flat = " ".join(flat.replace("|", " ").replace("*", "").split())
    by: dict[str, set[str]] = defaultdict(set)
    for m in NUM.finditer(flat):
        tail = flat[m.end():].split()[:WINDOW]
        words = [w for w in tail
                 if re.search(r"[A-Za-z]", w) and not STOP.match(w.strip(".,;:()").lower())]
        if len(tail) < WINDOW or len(words) < 2:
            continue
        # Re-split after stripping: a token that is punctuation only strips to nothing
        # and leaves a leading space, so the same phrase hashes two ways.
        key = " ".join(" ".join(NUM.sub("<n>", w.strip(".,;:()"))
                                for w in tail).split()).lower()
        by[key].add(m.group(1) + m.group(2))
    return by


def test_the_scan_reads_the_manuscript():
    """Vacuous against an empty extraction, which is how this kind of guard dies quietly."""
    by = _groups(DRAFT)
    assert len(by) > 1000, f"the scan found only {len(by)} phrases; it should find over a thousand"
    assert any("company-series pairs" in k for k in by), "the scan lost the phrase it was built on"


def test_no_quantity_is_stated_with_two_different_numbers():
    repeats = {k: v for k, v in _groups(DRAFT).items() if len(v) > 1}
    bad = [f"{sorted(v)}  …{k}" for k, v in sorted(repeats.items()) if k not in ALLOWED]
    assert not bad, (
        "one phrase carrying more than one number — two places state one quantity and "
        "disagree, which no other guard in this repository can see:\n  " + "\n  ".join(bad) +
        "\n  If both are correct and merely share a phrase, name it in ALLOWED with the reason.")


def test_the_scan_fires_on_the_pair_it_exists_for():
    """Shown failing on the real defect, in the shape it really had: a table row and a sentence.

    A guard only ever seen passing has not been reviewed, and this one needed three designs
    before it could see this pair at all.
    """
    fixture = (
        "| Round dates | the first report month a new series letter appears across two "
        "houses | 425 company-series pairs on 288 companies | the earliest N-CSR date |\n"
        "\n"
        "*Reach.* 433 company-series pairs on 287 companies clear both rules, against ten "
        "companies with any N-CSR coverage at all.\n")
    hits = {k: v for k, v in _groups(fixture).items() if len(v) > 1}
    assert any(v == {"425", "433"} for v in hits.values()), (
        f"the scan no longer separates the pair it was measured on: {hits}")


def test_the_allowances_are_all_still_live():
    """A dead allowance is a hole nobody is watching."""
    repeats = {k for k, v in _groups(DRAFT).items() if len(v) > 1}
    stale = sorted(set(ALLOWED) - repeats)
    assert not stale, (
        f"allowance(s) for phrases the manuscript no longer repeats — delete them: {stale}")
