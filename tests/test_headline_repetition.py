"""A headline figure may be restated a few times. It may not be restated everywhere.

The manuscript pins its numbers by requiring each one to appear verbatim
(`src/paper_numbers.py`), and that requirement has exactly one failure mode: it is
satisfied by repeating a figure and never by removing one. Over nineteen rounds the
paper drifted into quoting `12.1%` eleven times and `$180.0B` six, so a reader met the
same three statistics in the abstract, the introduction, four body sections, an
appendix and the conclusion, and the paper read as if it were arguing by insistence.
The registry cannot see this: eleven occurrences pass its check as comfortably as one.

Ceilings below are the counts after the compression round, not aspirations, so this
locks in what was done rather than describing what someone intended. Raising one is a
legitimate edit — put the new number here and the reason beside it.

Tables are excluded from the count. A figure belongs in every table row that reports
it, and no reader experiences a table cell as a repetition of the prose.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")


def prose() -> str:
    """The manuscript without its tables, and without the bibliography.

    Bold markers are stripped because the style pass sets some occurrences bold and
    some not, and `**12.1%**` and `12.1%` are the same repetition to a reader.
    """
    body = "\n".join(l for l in DRAFT.split("\n") if not l.startswith("|"))
    cut = body.find("\n## References")
    return (body if cut < 0 else body[:cut]).replace("**", "")


# figure -> (ceiling, where the occurrences legitimately are)
CEILINGS = {
    "12.1%":  (10, "abstract, §1 ×2, §3.3, §5.1, §5.2, §5.4, Appendix G.2, §11, Appendix B "
                   "— the last is a different statistic that rounds the same way and "
                   "says so in the sentence"),
    # The reviewer's point, taken: a large number that Appendix G then reduces to 0.33 basis points
    # spends a reader's trust twice. Both totals are out of the abstract and the introduction
    # and live where they are measured — §5.1's reconciliation, §5.3, and the conclusion, where
    # the NAV result stands next to them.
    "$180.0B": (3, "§5.1 (the reconciliation), §5.3, §11"),
    "$517.3B": (3, "§5.1, §5.3, §11"),
    "0.004%":  (5, "abstract, §1, §5.1, §5.4, §11 — the registrant-level figure is the "
                   "paper's foil and appears wherever the unit is being argued"),
    "10.1%":   (5, "§5.2, §5.4, Appendix G.2, §11 ×2"),
    "0.33 basis points": (5, "abstract, §1, Appendix G.2 ×2, §11"),
    # The three results added in review are headline figures now, and nothing was
    # watching them: the showcase pass put each into §1 and §11 beside the section that
    # measures it, which is three mentions apiece and the same budget the older figures
    # keep. Ceilings are the current counts, so the next restatement has to argue for
    # itself here.
    "5.88%":  (5, "abstract, §1, §5.2 where it is measured, §5.7's list of the four "
                  "medians, §11"),
    "65.1%":  (3, "§1, §5.4, §11"),
    "25.4%":  (3, "§1, §5.4, §11 — the null the repeat rate is read against, so it "
                  "travels with it"),
    "25.54%": (3, "§1, §5.4, §11"),
    "1.57%":  (3, "§1, §5.4, §11"),
    "2,326":  (3, "§1, §5.4, §11 — the cells that have a dissenter at all"),
    "2,586":  (1, "§5.4 only, as the denominator the 260 unanimous cells come out of"),
    "0.94%":  (2, "§1 and §5.2's sentence; the table cell is not prose"),
    "29.63%": (2, "§1 and §5.2's sentence"),
    "4.82%":  (2, "§1 and §5.3's sentence"),
    "309,654": (5, "abstract, §1, §3.1, §11, README-facing summary"),
}


def test_the_counter_reads_the_manuscript_and_can_see_a_figure():
    """Every assertion below is vacuous against an empty or table-stripped-to-nothing text."""
    p = prose()
    assert len(p) > 100_000, f"prose extraction returned {len(p)} characters"
    assert "12.1%" in p, "the counter cannot see the paper's headline figure"
    assert p.count("|") < DRAFT.count("|") / 10, "table rows were not removed"
    # Cutting at the bibliography hides everything after it. That is correct only while
    # the bibliography is last — found by writing a probe that appended text to the end
    # of the manuscript and watching the counter ignore it.
    heads = re.findall(r"^## (.+)$", DRAFT, re.M)
    assert heads[-1].startswith("References"), (
        f"the bibliography is no longer the last section ({heads[-1]!r}); everything "
        f"after it is invisible to this check")


def test_the_ceilings_are_not_slack():
    """A ceiling well above the true count is a test that cannot fail.

    Each ceiling must be the current count or one above it; if a figure is cut further,
    this fails and the ceiling comes down with it. That is the intended maintenance.
    """
    p, loose = prose(), []
    for fig, (cap, _) in CEILINGS.items():
        n = p.count(fig)
        if n < cap - 1:
            loose.append(f"{fig}: {n} occurrences against a ceiling of {cap} — lower the ceiling")
    assert not loose, "ceiling(s) no longer binding:\n  " + "\n  ".join(loose)


def test_no_headline_figure_is_repeated_past_its_ceiling():
    over = []
    for fig, (cap, where) in CEILINGS.items():
        n = prose().count(fig)
        if n > cap:
            over.append(f"{fig}: {n} occurrences, ceiling {cap} ({where})")
    assert not over, ("headline figure(s) repeated past the ceiling:\n  " + "\n  ".join(over) +
                      "\n  Cut one, or raise the ceiling here with the reason.")


def test_no_sentence_states_the_same_figure_twice():
    """`expecting the 12.1% to be a 12.1% error` — the version this test was written for.

    Restating a figure inside one sentence is never emphasis; it is a sentence that was
    edited around the number instead of through it.
    """
    bad = []
    for sentence in re.split(r"(?<=[.!?])\s+", prose()):
        for fig in CEILINGS:
            if sentence.count(fig) > 1:
                bad.append(f"{fig} twice in: {' '.join(sentence.split())[:110]}…")
    assert not bad, "figure repeated within one sentence:\n  " + "\n  ".join(bad)
