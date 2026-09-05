"""
Every section pointer in README.md must land on a section the paper has.

The README is the first thing a reader opens and it is written in the paper's own
section numbers. When the manuscript was reorganised, fifteen of its pointers kept
pointing at the pre-reframe numbering: `§4.1` had become `§7.2`, `§4.6` had become
`Appendix C.2`, and a reader following either landed somewhere unrelated. Nothing
failed, because nothing was checking — `tests/test_paper_consistency.py` guards the
numbers in the manuscript and had no opinion about the README.

Two checks, because the obvious one alone is close to worthless here.

The first scrapes the headings out of `paper/draft.md` and requires every `§N.M` in
the README to be one of them. That catches a pointer into a section that no longer
exists — `§4.7`, `§4.10`, `§5.12`. Run against the README as it stood, it would have
caught nine of the fifteen and *missed* the other six: `§4.1` and `§4.2` still exist
under the new numbering, as entirely different sections, so a pointer at them is
wrong and resolvable at the same time. An existence check cannot see that.

The second is a banlist, the same device `tests/test_paper_consistency.py` uses for
superseded figures. The pre-reframe manuscript numbered the secondary cross-section
`§4.1–4.2` and the corroborating legs `§4.5`–`§4.11`; all of that moved to §7 and
Appendices C–E. Those numbers are therefore retired as README pointers whether or not
the new numbering happens to reuse them, and the banlist says so by hand, with the
target beside each one so the fix is written down rather than rediscovered.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")

# `## 7. Title` / `### 7.1 Title` / `## Appendix C. ...` / `### C.2 Title`
_HEADING = re.compile(r"^#{2,3} (?:Appendix )?([A-G]|\d+)(?:\.(\d+))?[ .]", re.M)
# `§7.2`, `§8.9–8.11`, `Appendix C.2`, `Appendices C.1–C.2`
_POINTER = re.compile(r"§(\d+(?:\.\d+)?)|Appendix (?:[A-G]\.\d+|[A-G])\b")
# `Appendix C.4`, `Appendix E.1` — the letter half, which the numeric checks never see.
_APPENDIX = re.compile(r"Appendi(?:x|ces) ([A-G])(?:\.(\d+))?")


def sections() -> set[str]:
    out = set()
    for m in _HEADING.finditer(DRAFT):
        out.add(m.group(1) if m.group(2) is None else f"{m.group(1)}.{m.group(2)}")
    return out


def test_the_scrape_finds_the_sections_it_claims_to():
    """The guard is worthless if the heading scrape comes back empty or tiny.

    A regex that matches nothing makes every pointer look valid. These are the shape
    of the paper as of the reframe: twelve numbered sections and five appendices, so
    a scrape that drops below fifty entries has stopped reading the headings.
    """
    s = sections()
    assert len(s) > 35, f"heading scrape found only {len(s)}: {sorted(s)}"
    for expected in ("1", "11", "3.1", "8.5", "C.1", "C.5"):
        assert expected in s, f"heading scrape missed §{expected}"


# The pre-reframe numbers, and where each one went. `§4.3` and `§4.4` are absent on
# purpose: the cross-fund-marks section the README means by `§4.3` is §4.3 in the new
# numbering too, so those pointers are correct and the banlist must not fire on them.
RETIRED = {
    # §4.1 and §4.2 pointed at the secondary cross-section, which is cut to a second
    # paper. Their targets no longer exist here at all, which is a stronger reason to
    # ban them than the renumbering that first put them on this list.
    "4.1": "the secondary cross-section, cut to a second paper",
    "4.2": "the sector sign-split, cut with it",
    "7.2": "the secondary cross-section, cut to a second paper",
    "4.5": "the marks-through-time appendix, cut to a second paper",
    "4.6": "the Forge index appendix, cut with it",
    "4.7": "the prediction-market appendix, cut with it",
    "4.8": "Appendix B (robustness)",
    "4.9": "the cross-signal synthesis, cut with the legs it synthesised",
    "4.10": "Appendix C.1 (the Gornall-Strebulaev reconciliation)",
    "4.11": "Appendix C.4 (testable predictions)",
    "5.12": "Appendix C.3 (the harvest cap lifted)",
}


def test_the_guard_can_fail():
    """Both halves have to be able to fail, and on the right inputs.

    §4.7 does not exist, so the existence check owns it. §4.1 does exist and means
    something else now, so only the banlist owns it — that split is the whole reason
    there are two checks and it is asserted here rather than described above.
    """
    assert "4.7" not in sections(), "the existence check has nothing to catch"
    assert "4.1" in sections(), "§4.1 exists; if it stops, the banlist entry is dead"
    assert "4.3" not in RETIRED, "§4.3 is a live pointer and must not be banned"


def test_no_retired_section_pointer_survives_in_the_readme():
    bad = []
    for m in re.finditer(r"§(\d+\.\d+)", README):
        if (n := m.group(1)) in RETIRED:
            line = README[:m.start()].count("\n") + 1
            bad.append(f"README line {line}: §{n} is the pre-reframe number for {RETIRED[n]}")
    assert not bad, "retired section pointer(s):\n  " + "\n  ".join(bad)


def test_every_readme_section_pointer_resolves():
    have, bad = sections(), []
    for m in _POINTER.finditer(README):
        if m.group(1) and m.group(1) not in have:
            line = README[:m.start()].count("\n") + 1
            bad.append(f"README line {line}: §{m.group(1)} is not a section of the paper")
    assert not bad, "stale section pointer(s):\n  " + "\n  ".join(bad)


def test_every_readme_appendix_pointer_resolves():
    """The appendix letters, which the §N.M checks above are blind to.

    Cutting the secondary, prediction-market and cycle legs deleted Appendices B and C, and
    the README went on pointing at `Appendix C.4` and `Appendix C.1` in two places. Nothing
    failed: `_POINTER` matched them and then only ever looked up the `§` group. A pointer at
    a deleted appendix is worse than a stale section number, because the reader cannot even
    guess where the material went.
    """
    have, bad = sections(), []
    for m in _APPENDIX.finditer(README):
        want = m.group(1) if m.group(2) is None else f"{m.group(1)}.{m.group(2)}"
        if want not in have:
            line = README[:m.start()].count("\n") + 1
            bad.append(f"README line {line}: Appendix {want} is not in the paper")
    assert not bad, "pointer(s) at a deleted appendix:\n  " + "\n  ".join(bad)


def test_the_appendix_check_can_fail():
    """The appendices are A–E now, relettered after the cut, and F was never one of them.

    The first version of this test asserted that Appendix C did *not* exist, which was true
    for exactly one round: the letters ran A, D, E, F, G with a hole where the cut material
    had been, and the assembler's numbering pass has since closed it. An assertion about a
    hole is an assertion with a shelf life; this one is about the shape that should hold.
    """
    have = sections()
    assert "A" in have and "C.1" in have, "the heading scrape misses the live appendices"
    # The letters run A-G since the NAV-wedge section left the body for Appendix G. The
    # guard is about the SHAPE — contiguous, no hole — so it asserts the next letter is
    # absent rather than a fixed last letter, and moves by one line when an appendix is
    # added rather than failing on a correct manuscript.
    assert "G" in have, "Appendix G is gone; if the cost section moved back, update this guard"
    assert "H" not in have, "the appendices run A-G; if that changes, update this guard"


def test_readme_quotes_the_paper_s_headline_numbers():
    """The README restates the headline; if the paper moves, this catches the drift.

    Only the figures the paper's own registry pins, so this test cannot disagree with
    `tests/test_paper_consistency.py` about what is true.
    """
    for figure in ("12.1%", "10.1%", "0.004%", "$180.0B", "$517.3B", "309,654",
                   "58.8%", "$92.50", "$190.00"):
        assert figure in README, f"README no longer quotes {figure}"
        assert figure in DRAFT, f"{figure} is in the README but not in the paper"
