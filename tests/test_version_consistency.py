"""
Final-paper marker guard.

During development the manuscript carried a 'Working draft vN' marker, pinned to
match across paper/draft.md, src/build_pdf.py (the rendered date line) and
CITATION.cff. The paper is now final: that marker is removed from the manuscript
and from the rendered date. These tests make sure it does not creep back in and
that CITATION.cff still declares a release version.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_working_draft_marker():
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    build = (ROOT / "src" / "build_pdf.py").read_text(encoding="utf-8")
    assert "Working draft" not in draft, "paper/draft.md still carries a 'Working draft' marker"
    assert "Working draft" not in build, "src/build_pdf.py DATE_LINE still carries a 'Working draft' marker"


def test_citation_declares_a_release_version():
    cite = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert re.search(r'version:\s*"[\d.]+"', cite), "CITATION.cff missing a numeric version"


def test_the_three_version_dates_agree():
    """The date a reader sees lives in three files: the manuscript byline, the rendered
    PDF footnote, and CITATION.cff. Nothing forced them to agree, and they drifted a month
    behind the manuscript — a reader downloading the PDF saw a date older than its own
    contents. Same date, written once per file, checked here."""
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    build = (ROOT / "src" / "build_pdf.py").read_text(encoding="utf-8")
    cite = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

    m = re.search(r"This version: (\w+ \d+, \d{4})", draft)
    assert m, "the manuscript byline no longer states a version date"
    stated = m.group(1)
    # The rendered footnote, not the source text. `build_pdf.AUTHOR_THANKS` interpolates
    # `VERSION_DATE` now, so the date is no longer a literal anywhere in that file and
    # grepping for one found nothing — a check that had stopped being able to pass.
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import build_pdf as bp
    assert f"This version: {stated}" in bp.AUTHOR_THANKS, (
        f"build_pdf.py renders a different date from the manuscript's {stated!r}")
    assert "VERSION_DATE" in build, (
        "the date is a literal in build_pdf.py again; it is meant to have one definition")

    import datetime as _dt
    iso = _dt.datetime.strptime(stated, "%B %d, %Y").date().isoformat()
    assert f"date-released: {iso}" in cite, (
        f"CITATION.cff does not carry {iso}, the date the manuscript states")


def test_the_version_date_is_not_in_the_future():
    """A paper dated ahead of today reads as a copy-paste, and it is one."""
    import datetime as _dt
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    stated = _dt.datetime.strptime(
        re.search(r"This version: (\w+ \d+, \d{4})", draft).group(1), "%B %d, %Y").date()
    assert stated <= _dt.date.today(), f"the paper is dated {stated}, which has not happened yet"


def test_the_manuscript_has_not_moved_past_its_own_version_date():
    """The three files agreeing on a date says nothing about whether the date is current.

    It said 12 August while the manuscript carried four days of corrections past it — the
    series-pattern fix, three defensive passages, a bibliography entry. All three copies
    agreed, and all three were stale, which is the hole a consistency check leaves open.

    Nothing in the repository knows what day it is in a way a test can trust: reading the
    clock makes the result depend on when the suite runs. The last commit touching
    `paper/draft.md` is a fact the repository stores, so this is decidable here and is not
    decidable in a tarball, where the test says so instead of guessing.
    """
    import datetime as _dt
    import subprocess
    import pytest
    if not (ROOT / ".git").exists():
        pytest.skip("no repository: staleness is not decidable from the files alone")
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "paper/draft.md"],
                       cwd=ROOT, capture_output=True, text=True, check=False)
    if r.returncode != 0 or not r.stdout.strip():
        pytest.skip("git present but the manuscript has no commit history here")
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    stated = _dt.datetime.strptime(
        re.search(r"This version: (\w+ \d+, \d{4})", draft).group(1), "%B %d, %Y").date()
    committed = _dt.date.fromisoformat(r.stdout.strip())
    assert stated >= committed, (
        f"the manuscript was last changed on {committed} and the title page still says "
        f"{stated}. Move `build_pdf.VERSION_DATE`, the front matter and CITATION.cff together.")


def test_the_citation_title_is_the_paper_s_title():
    """CITATION.cff is how the work gets cited, and it kept the pre-reframe title.

    The manuscript was retitled to "How Far Apart Mutual Funds Mark the Same Private
    Company"; CITATION.cff went on saying "What Sophisticated Investors Say the Same
    Private Share Is Worth" in both of the places it names the work. Anyone citing the
    repository would have cited a title the paper does not have. The date check above
    existed and this one did not, so the file was half-guarded.

    Both occurrences are checked, because they are separate keys and fixing one is the
    obvious way to leave the other wrong.
    """
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    cite = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    m = re.search(r"^# (.+)$", draft, re.M)
    assert m, "the manuscript has no H1 title"
    title = m.group(1).strip()
    assert cite.count(f'title: "{title}"') == 2, (
        f"CITATION.cff should name {title!r} as both `title` and `preferred-citation.title`; "
        f"found {cite.count(chr(34) + title + chr(34))} occurrence(s)")
