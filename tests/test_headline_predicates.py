"""The sentences the load-bearing figures are allowed to appear in.

The registry pins values. It does not pin predicates, and the difference is the worst defect
this project has shipped: §1 and §11 quoted $180.0B correctly and then said it was "a wedge
of that size in the net asset value two sets of ordinary fund investors are credited with",
which is the one thing Appendix G exists to disprove. Every number was right, the claim was wrong,
the guard was green, and the paper contradicted itself in the introduction and the conclusion
for two rounds.

*What this guard learned about itself.* The first version banned the phrase as a substring.
It failed on the CORRECTED text, because §1 now reads "It is **not** a wedge of that size in
the net asset value", and it failed on Appendix G's "it is **not**, on this evidence, a systemic
mispricing" and on §1.1's *Not claimed* list. A checker that cannot tell an assertion from a
denial does not police meaning; it pressures the author to delete the denial to get a green
build, which is worse than no checker.

So the scope is cut to what it can actually decide:

* an APPOSITIVE asserting the identity — "which is ... a wedge of that size in the net asset
  value" — which the shipped sentence had and no denial can produce;
* proximity requirements that hold for every legitimate use, checked by running them;
* the presence of the two denials themselves, so removing them fails.

Rules the checker cannot decide are not in it.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
PROSE = " ".join("\n".join(
    l for l in DRAFT.split("\n") if not l.startswith(("|", "#"))).split())

WINDOW = 320

# An appositive that ASSERTS the identity. "It is not a wedge ..." cannot match: the pattern
# requires a relative pronoun and no intervening sentence end or negation.
ASSERTS_NAV_WEDGE = re.compile(
    r"(which|that) is(?![^.]{0,40}\bnot\b)[^.]{0,90}wedge of that size in the net asset value",
    re.I)

# Figures that must sit near a word naming what they are OF. Each list was checked against
# every occurrence in the manuscript before being written down.
NEARBY = {
    "$180.0B": {"position", "booked", "security", "24%"},
    "0.33 basis point": {"net asset", "nav", "median"},
}

# Denials the paper must keep. These are the corrections; losing one silently restores the
# defect, and unlike the assertion they are plain strings.
# The first of these used to be §1's own denial, in the paragraph that quoted $180.0B. That
# paragraph is gone: the introduction no longer states a dollar total it would then have to
# take back, which is the same defect handled by removal rather than by correction. What the
# paper still has to carry is the boundary itself, stated where the size is claimed and again
# where it is measured.
REQUIRED = [
    "A spread that is large as a fraction of an asset can be small as a fraction of a "
    "diversified fund",
    "not, on this evidence, a systemic mispricing of mutual-fund NAV",
]


def _windows(fig: str) -> list[str]:
    return [PROSE[max(0, m.start() - WINDOW):m.end() + WINDOW]
            for m in re.finditer(re.escape(fig), PROSE)]


def test_the_scan_finds_the_figures():
    """A window function that matches nothing passes every rule vacuously."""
    assert len(PROSE) > 150_000, "the prose filter has eaten the manuscript"
    for fig in NEARBY:
        assert _windows(fig), f"{fig!r} no longer appears in the manuscript prose"


def test_no_sentence_asserts_the_disagreement_is_a_nav_wedge():
    hits = [PROSE[max(0, m.start() - 160):m.end() + 40] for m in ASSERTS_NAV_WEDGE.finditer(PROSE)]
    assert not hits, ("a sentence asserts the >24% disagreement IS a wedge of that size in "
                      "NAV; Appendix G measures 0.33 basis points:\n  " + "\n  ".join(hits))


def test_the_assertion_pattern_rejects_what_shipped_and_accepts_the_fix():
    """Both directions, because a pattern that fires on nothing is not a guard.

    The first string is what §1 carried for two rounds. The second is what it carries now.
    """
    shipped = ("$180.0B of it sits where houses differ by more than 24% about the same "
               "security, which is, because shares outstanding are common to every holder, "
               "a wedge of that size in the net asset value two sets of ordinary fund "
               "investors are credited with.")
    fixed = ("Shares outstanding are common to every holder, so that is a disagreement of "
             "that size about what one holding is worth to two different sets of fund "
             "investors. It is not a wedge of that size in the net asset value they "
             "transact at.")
    assert ASSERTS_NAV_WEDGE.search(shipped), "the pattern no longer catches the shipped error"
    assert not ASSERTS_NAV_WEDGE.search(fixed), "the pattern fires on the corrected sentence"


def test_headline_figures_sit_near_a_word_naming_what_they_are_of():
    bad = []
    for fig, need in NEARBY.items():
        for i, w in enumerate(_windows(fig)):
            if not any(t in w.lower() for t in need):
                bad.append(f"{fig} occurrence {i + 1}: none of {sorted(need)} nearby\n"
                           f"      ...{w[WINDOW - 90:WINDOW + 110]}...")
    assert not bad, "figure(s) with no unit named nearby:\n  " + "\n  ".join(bad)


def test_the_denials_are_still_in_the_paper():
    missing = [s for s in REQUIRED if s not in PROSE]
    assert not missing, ("the correction has been dropped from the manuscript:\n  "
                         + "\n  ".join(missing))
