"""A registry entry's claim string must state the entry's own number.

The registry has three parts and checked two of them. `computed` is recomputed from production
code and compared to `value`; `claim` is required to appear verbatim in the manuscript. Nothing
compared `claim` to `value`, so an entry could carry a corrected value and a superseded
sentence at the same time and pass both checks — the value check because the code agrees with
`value`, the prose check because the old token is still somewhere in a 28,000-word manuscript.

Two entries were in exactly that state when this file was written, both from the series-regex
correction:

    add("5.12", "median restricted to one named series (%)", ..., 28.7, 0.1, "**32.3%**")
    add("5.12", "of those, cells the restriction leaves unchanged", ..., 3, 0, "**five**")

Both passed `reproduce.py` with zero code drift and zero prose drift. The manuscript said the
class objection was worth about two points where the code said six, and said the restriction
left five cells unchanged where the code said three. `test_registry_sections` did not see it
either: it requires the token to sit in the entry's own section, and both tokens did — §5.12
names Gusto's spread, which is 32.3% for an unrelated reason, and "five" is a common word.

So the rule is the one the other two checks imply and neither states: the sentence the paper
prints and the number the code produces have to be the same number.

WHAT THIS CANNOT DECIDE, AND WHY IT IS EXEMPT RATHER THAN GUESSED
A claim may state its number in several shapes, and each shape below was met in the live
registry rather than imagined: spelled out ("twenty-two sub-advised funds"), in scientific
notation ("p=2×10⁻¹¹"), with a Unicode minus ("a step of −2.52 points"), or as a derived
quantity the sentence never prints ("undershot in all three" for a 1/0 flag). The parser
handles the first three. The fourth cannot be parsed by anything, so those entries are named
in `NO_NUMBER_IN_CLAIM` one at a time, and `test_the_exemptions_are_all_still_live` deletes
the list the moment an exemption stops being needed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import paper_numbers as pn

# Claims whose number is not in the sentence at all. Each is a flag or a count the prose
# expresses as a word that is not a numeral, and each was read before being listed.
NO_NUMBER_IN_CLAIM = {
    # "undershot in all three" — a 1/0 flag, and the three is the sample, not the value.
    "Fidelity pre-IPO marks all undershot (1=yes)",
    # "η²" — the claim is the symbol. The number beside it is registered separately.
    "between-family variance share (material names)",
    # "a third of a point" — a fraction in words, and spelling it 0.33 in the sentence
    # would be worse prose for a figure whose whole point is that it is small.
    "points they move the population median",
}

WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
}
SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
SCI = re.compile(r"(\d+(?:\.\d+)?)\s*×\s*10([⁻\-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)")


def _numbers(claim: str) -> set[float]:
    """Every quantity the sentence states, in any shape the registry actually uses."""
    flat = pn._demark(claim).replace("−", "-")
    out: set[float] = set()
    for m in SCI.finditer(flat):
        out.add(float(m.group(1)) * 10 ** int(m.group(2).translate(SUPER)))
    for m in NUM.finditer(flat):
        out.add(float(m.group(0).replace(",", "")))
    # "twenty-two" is one number written as two words; the tens word alone is also a number.
    low = flat.lower()
    for tens in ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"):
        for unit, u in WORDS.items():
            if u < 10 and f"{tens}-{unit}" in low:
                out.add(WORDS[tens] + u)
    for w, v in WORDS.items():
        if re.search(rf"\b{w}\b", low):
            out.add(float(v))
    return out


def _tolerance(n) -> float:
    """The entry's own band, widened only to cover the rounding the prose is allowed.

    A claim prints a rounded figure — `−2.52 points` for −2.5178, `421,062` for −421062.62 —
    so the comparison has to survive one place of rounding. Half a unit of the claim's own
    last printed place would need the claim parsed twice; one percent of the value plus half
    a unit covers every rounding in the live registry and is still far tighter than the gap
    between 28.7 and 32.3, which is what this exists to catch.
    """
    return max(float(n.tol), 0.01 * abs(float(n.value)) + 0.5)


@pytest.fixture(scope="module")
def registry():
    return pn.canonical_numbers()


def test_the_parser_reads_the_shapes_the_registry_uses():
    """Vacuous unless the parser can actually read each shape. All four are live entries."""
    assert 22 in _numbers("twenty-two sub-advised funds")
    assert 3 in _numbers("**three** of them")
    assert -2.52 in _numbers("a step of −2.52 points")
    assert any(abs(v - 2e-11) < 1e-13 for v in _numbers("p=2×10⁻¹¹"))
    assert 421062 in _numbers("a wedge of 421,062 basis points")
    assert 28.7 in _numbers("**28.7%**")


def test_every_claim_states_the_value_it_is_registered_at(registry):
    bad = []
    for n in registry:
        if not n.claim or n.label in NO_NUMBER_IN_CLAIM:
            continue
        vals = _numbers(n.claim)
        if not vals:
            bad.append(f"§{n.section} {n.label}: claim states no number at all — {n.claim!r}")
            continue
        v, tol = abs(float(n.value)), _tolerance(n)
        if not any(abs(abs(x) - v) <= tol for x in vals):
            bad.append(f"§{n.section} {n.label}: value {n.value:g} is not stated by its own "
                       f"claim {n.claim!r}")
    assert not bad, (
        "registry entr(ies) whose sentence and whose number disagree — the paper prints one "
        "and the code produces the other, and both other checks pass:\n  " + "\n  ".join(bad))


def test_the_guard_fires_on_the_pair_it_exists_for():
    """Shown failing on the real defect. A guard only ever seen passing has not been reviewed.

    The two entries as they stood after the series-regex retune moved their values and left
    their sentences behind.
    """
    class Entry:
        def __init__(self, value, tol, claim):
            self.value, self.tol, self.claim = value, tol, claim

    for value, tol, claim in ((28.7, 0.1, "**32.3%**"), (3, 0, "**five**")):
        e = Entry(value, tol, claim)
        vals = _numbers(e.claim)
        assert vals, "the parser stopped reading the claim; the guard would pass vacuously"
        assert not any(abs(abs(x) - abs(value)) <= _tolerance(e) for x in vals), (
            f"{claim!r} no longer reads as disagreeing with {value}; the tolerance has "
            f"widened past the defect this guard was measured against")


def test_the_exemptions_are_all_still_live(registry):
    """A dead exemption is a hole nobody is watching."""
    labels = {n.label for n in registry}
    stale = sorted(NO_NUMBER_IN_CLAIM - labels)
    assert not stale, f"exemption(s) for entries the registry no longer has: {stale}"
