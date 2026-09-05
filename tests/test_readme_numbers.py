"""The README's figures, in the direction nothing checked.

The registry runs one way. An entry naming `readme` requires its token to APPEAR in the
README, so a figure the registry knows about cannot go stale there. A figure the registry has
never heard of is unguarded in both directions, and the README is the first thing a reader
sees — usually the only thing, for anyone deciding whether to open the paper.

That is not hypothetical. The coordination-rule sentence went on saying "10 of 14 inside 35
days" for two versions after the paper recomputed it to 11 of 15, and the retracted
third-of-a-point bound survived there through a round in which the body had already withdrawn
it. Both were registered nowhere, so both were true of a README nobody was checking.

The manuscript's own guard for this class is a budget: prose restates plenty of figures
legitimately, so the rule is not "every number is registered" but "the number of unregistered
ones does not grow". This is the same guard pointed at `README.md`, with the same two-sided
assertion — a ceiling well above the true count is a test that cannot fail, which is the
defect `test_headline_repetition.py::test_the_ceilings_are_not_slack` exists to stop and which
the manuscript's own budget carried for three rounds before it was noticed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import paper_numbers as pn

README = (ROOT / "README.md").read_text(encoding="utf-8")

# Percentages and dollar magnitudes: the same selector the manuscript's budget uses, so the
# two guards cannot drift apart in what they consider a figure.
FIGURE = re.compile(r"(?<![\d.])[\d][\d.,]*%|\$[\d.,]+[BMT]")

# Bare counts, three characters or more. The first version of this file checked percentages
# and dollars only, and the README's round-date instrument sat at "425 company-series pairs on
# 288 companies" for a round after the paper had recomputed it to 433 on 287 — a bare count,
# invisible to a selector looking for a % or a $.
#
# Three characters, not one, and the reason is the false-positive rate rather than principle:
# at two the scan picks up "10 of 15", "5 funds", "two-digit" ordinals and every list marker
# in the file, and a budget that has to absorb thirty of those cannot detect one real figure
# arriving. So two-digit counts in the README are NOT guarded, and that is a stated hole, not
# an oversight. `309,654`, `1,941`, `4,271` and `425` are all caught.
# Thousands-grouped or three digits and up. The looser `\d[\d,]{2,}` tokenised the set
# notation `K∈[2,5]` as the number "2,5", which is the kind of false positive that makes a
# budget unreadable and then unmaintained.
COUNT = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{3,}\b")
YEAR = re.compile(r"^(?:19|20)\d\d$")

# Structural rather than measured. The list is short on purpose: an exemption is a figure
# nothing checks, so each one has to earn its line.
EXEMPT = {
    "100%",          # a share that sums to one is a denominator, not a finding
}


def prose() -> str:
    """The README without its tables and code blocks.

    A figure belongs in every table row that reports it, and the fenced blocks are commands.
    Including either buries the thing this checks: a result restated in a sentence that no
    registry entry owns.
    """
    out, fenced = [], False
    for line in README.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced or line.startswith("|"):
            continue
        out.append(line)
    return "\n".join(out).replace("**", "").replace("*", "")


@pytest.fixture(scope="module")
def reachable() -> set[str]:
    """Every figure some registry entry states, whichever file it states it in.

    Not restricted to entries naming `readme`: the README paraphrases the paper, so a figure
    registered against the draft is a figure this repository does check. What matters is
    whether anything recomputes it, not which file it was pinned in.
    """
    out: set[str] = set()
    for n in pn.canonical_numbers():
        for phrase in (n.claim, *n.context.values()):
            if not phrase:
                continue
            flat = pn._demark(phrase)
            out.add(flat.strip())
            out.update(m.group(0) for m in FIGURE.finditer(flat))
            out.update(m.group(0) for m in COUNT.finditer(flat))
    return out


def _tokens(text: str) -> set[str]:
    """Every result-shaped number the README states, years excluded."""
    out = {m.group(0) for m in FIGURE.finditer(text)}
    out |= {m.group(0) for m in COUNT.finditer(text) if not YEAR.match(m.group(0))}
    return out


def _loose(reachable: set[str]) -> list[str]:
    return sorted(t for t in _tokens(prose()) if t not in EXEMPT and t not in reachable)


def test_the_figure_scan_reads_the_readme():
    """Vacuous against an empty extraction, which is how a budget guard dies quietly."""
    text = prose()
    assert len(text) > 10_000, f"the README filter returned {len(text)} characters"
    found = _tokens(text)
    assert len(found) > 60, f"the scan found only {len(found)} tokens; it should find dozens"
    assert {"12.1%", "$180.0B", "309,654"} <= found, "the scan misses the README's headlines"
    # The repository-layout table must not be counted: a figure belongs in every row that
    # reports it. Asserted against a string that IS in the raw file, so the check fails if
    # the stripping is ever removed rather than passing on a substring nothing produces.
    assert "| Path | Holds |" in README, "the layout table has gone; re-point this check"
    assert "| Path | Holds |" not in text, "table rows were not removed"


def test_the_registry_reaches_the_readme_headline(reachable):
    """The guard is worthless if `reachable` is empty or misses what it plainly contains."""
    assert len(reachable) > 200, f"only {len(reachable)} registered phrases"
    for fig in ("12.1%", "0.004%", "0.74%", "8.45%"):
        assert fig in reachable, f"{fig} is registered in the paper but not seen as reachable"


# Read off the run that introduced this guard, not chosen. The budget only ever goes down:
# register a figure and lower it. Raising it is the thing to argue about in review.
BUDGET = 26


def test_the_readme_states_no_unregistered_figure_past_its_budget(reachable):
    loose = _loose(reachable)
    assert len(loose) <= BUDGET, (
        f"{len(loose)} figures in README.md that no registry entry recomputes "
        f"(budget {BUDGET}): {loose[:25]}\n"
        f"Register the figure, or state it as the paper states it so an entry reaches it.")


def test_the_readme_budget_is_not_slack(reachable):
    """A ceiling well above the true count cannot fail, which is no guard at all."""
    loose = _loose(reachable)
    assert len(loose) >= BUDGET - 3, (
        f"only {len(loose)} unregistered figures against a budget of {BUDGET} — "
        f"lower the budget to {len(loose)}")
