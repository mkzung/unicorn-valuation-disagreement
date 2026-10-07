"""Read the finished PDF, not the things that produce it.

Three test files mention the PDF and all three read `src/build_pdf.py`. Nothing has ever
opened the artifact a reader downloads, and everything that went wrong in it went wrong
between the source and the page: six lifted blocks printed a dead section heading, `1×10⁻⁵`
set as `1×10⁻` because the font lacked one glyph, and a whole build came out with no bold
face embedded while the script reported success. Each was found by hand, late, and twice by
noticing a file size.

So this checks the output. It is skipped rather than failed when the PDF is absent or stale
relative to the manuscript, because a contributor without XeLaTeX should not be blocked by a
file he cannot rebuild — `test_the_pdf_was_built_from_this_manuscript` reports that separately,
and it asks the question of content rather than of mtimes.
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
import build_pdf as bp
PDF = ROOT / "paper" / "unicorn_valuation_disagreement.pdf"
DRAFT = ROOT / "paper" / "draft.md"


def _text() -> str:
    out = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True, check=False).stdout
    # the PDF sets a real minus and curly quotes; hyphenation breaks words across lines
    out = (out.replace("−", "-").replace("’", "'").replace("‘", "'")
              .replace("“", '"').replace("”", '"').replace("-\n", ""))
    return " ".join(out.split())


def _stale() -> bool:
    """Was this PDF built from this manuscript? Asked of content, not of clocks.

    The first version compared mtimes and it was wrong in the way this whole test file is
    about: mtime asks whether the build happened after the edit, not whether the artifact
    matches the text. Git stores no mtimes, so after `git clone` the order is arbitrary and
    a reviewer running `pytest` on an untouched tree got a red suite telling him to rebuild
    a PDF that was already correct — three microseconds of clock skew reported as a defect.

    `src/build_pdf.py` stamps the manuscript's sha256 into the PDF's Keywords, so the
    question is now decidable from the two files alone.
    """
    stamped = bp.pdf_fingerprint(PDF)
    if stamped is None:
        return False                      # unstamped or no poppler: not evidence of staleness
    return stamped != bp.draft_fingerprint(DRAFT.read_text(encoding="utf-8"))


def _usable() -> None:
    if not PDF.exists():
        pytest.skip("no PDF built")
    if not shutil.which("pdftotext"):
        pytest.skip("pdftotext (poppler) not installed")
    if _stale():
        pytest.skip("PDF was built from a different manuscript; rebuild with src/build_pdf.py")


@pytest.fixture(scope="module")
def pdf_text() -> str:
    _usable()
    return _text()


REPO_URL = "https://github.com/mkzung/unicorn-valuation-disagreement"


def url_faults(text: str) -> tuple[list[str], int]:
    """Every place the repository URL is set, and what is wrong with it. Also the denominator.

    Separate from the test so that the two pages this repository actually shipped can be fed
    to it directly, below. A guard against a typesetting fault can only be trusted if its own
    failure has been seen, and seeing it otherwise means shipping a bad PDF on purpose.

    Legitimate: a break after a slash or a hyphen that is really in the address. Faults: a
    break anywhere else, and any page whose characters do not reconstruct the address at all.
    """
    faults, checked = [], 0
    for m in re.finditer(r"https\s*:", text):
        window = text[m.start():m.start() + 200]
        if "github.com" not in window.replace(" ", "")[:60]:
            continue                          # some other address; this test is about ours
        checked += 1
        raw, plain = "", ""
        for ch in window:
            raw += ch
            if not ch.isspace():
                plain += ch
            if plain == REPO_URL:
                break
        if plain != REPO_URL:
            faults.append(f"the URL is mangled on the page, not merely broken: {raw!r}")
            continue
        for w in re.finditer(r"\s", raw):
            if raw[:w.start()].rstrip()[-1:] not in ("/", "-"):
                faults.append("the URL breaks inside a word rather than at its own "
                              f"punctuation, so a reader retyping it invents a "
                              f"character: {raw!r}")
                break
    return faults, checked


@pytest.fixture(scope="module")
def pdf_raw() -> str:
    """`pdftotext -raw`, for the one question that is about line breaks.

    Two normalisations stand between the page and a naive reading of it, and both would make
    this test lie. `_text` collapses whitespace and strips `-\\n`. Default `pdftotext` ALSO
    strips a hyphen at a line end, on the assumption that TeX put it there — so a URL breaking
    correctly after the real hyphen in "unicorn-" extracts as "unicornvaluation-disagreement",
    and a test reading that would call a correct page mangled. `-raw` keeps the hyphen and the
    newline, which is the only form in which the question can be asked.
    """
    _usable()
    return subprocess.run(["pdftotext", "-raw", str(PDF), "-"],
                          capture_output=True, text=True, check=False).stdout


def test_the_extraction_works_at_all(pdf_text):
    """Every assertion below is vacuous if extraction returns a stub."""
    assert len(pdf_text) > 150_000, f"extracted only {len(pdf_text)} characters"
    assert "Disagreement Without a Price" in pdf_text


def test_every_section_heading_reaches_the_page(pdf_text):
    """The assembler printed six dead headings into the body and nothing noticed."""
    heads = re.findall(r"^#{2,3} (.+)$", DRAFT.read_text(encoding="utf-8"), re.M)
    assert len(heads) > 50, f"scraped only {len(heads)} headings from the manuscript"
    missing = [h for h in heads if " ".join(h.replace("*", "").split()) not in pdf_text]
    assert not missing, "heading(s) in the manuscript but not in the PDF:\n  " + "\n  ".join(missing)


def test_no_dead_section_number_is_set_as_body_text(pdf_text):
    """`N.N Capital` mid-paragraph is a lifted heading the delabeller missed.

    Real headings look identical once pdftotext flattens the page, so they are excluded by
    matching them against the manuscript's own heading list rather than by a shape rule. The
    first version used a shape rule and flagged §3.1.
    """
    heads = {" ".join(h.replace("*", "").split())
             for h in re.findall(r"^#{2,3} (.+)$", DRAFT.read_text(encoding="utf-8"), re.M)}
    stale = [s for s in re.findall(r"(?<=[.:] )\d+\.\d+ [A-Z][a-z][^.]{10,70}", pdf_text)
             if not any(s.startswith(h[:len(s)]) or h.startswith(s[:40]) for h in heads)]
    assert not stale, f"section number set as running text: {stale[:3]}"


def test_the_registered_figures_are_on_the_page(pdf_text):
    """A number can be right in the manuscript and absent from the PDF.

    Only the headline set: the full registry is checked against the manuscript by
    `test_paper_consistency.py`, and re-checking 474 numbers here would duplicate it
    slowly. These are the ones a reader quotes.
    """
    for fig in ("309,654", "12.1%", "0.004%", "$180.0B", "$517.3B", "10.1%", "58.8%",
                "$92.50", "$190.00", "2.52", "0.33 basis points", "8.45%", "0.74%",
                "48.19%", "11.06%"):
        assert fig in pdf_text, f"{fig} is in the manuscript but not in the rendered PDF"


def test_the_repository_url_is_not_broken_inside_a_word(pdf_raw):
    """The address a reader retypes has to survive typesetting, and twice it did not.

    The title page shipped `unicorn-valu` / `ation-disagreement` across a line break. A URL is
    the one string on the page that a reader may copy by hand, and a break invented inside a
    word makes it wrong. It survived two rounds because every check ran on the manuscript, and
    the manuscript is correct — the defect is created by the typesetter, so only the page can
    show it.

    The break is legitimate after a slash or a hyphen that is really in the address, so the
    test does not ban breaking. It bans breaking anywhere else.

    The first version of this test joined the lines back together and asked whether the URL
    was present. It passed on the broken page: the typesetter emits no hyphen at the break, so
    deleting the newline reconstructs the correct address from the incorrect page and the test
    could not tell the two apart. What distinguishes them is where the whitespace sits, so
    that is what is read — every whitespace character inside the address must follow a
    character that is in the address.
    """
    problems, checked = url_faults(pdf_raw)
    assert checked, "the repository URL is not on any page; the probe matched nothing"
    assert not problems, "\n  ".join(problems)


def test_the_scientific_notation_survived_the_font(pdf_text):
    """The superscript that shipped truncated, checked on the page rather than in the source.

    `1×10⁻⁵` set as `1×10⁻` for two rounds because TeX Gyre Termes lacks U+2075 and xelatex
    calls a missing glyph a warning. `pdftotext` puts a space between the base and a
    superscript digit, so the probe is whitespace-tolerant — the literal string is not in the
    extraction even when the page is correct, which is how the first version of this test
    managed to fail on a good build.

    The exponents are read out of the manuscript rather than listed here. Three were listed,
    and two of them left the paper when Appendix G.3's table stopped needing them, so the
    test failed on prose that was correct and would have said nothing about the ones that
    remained. A guard over a hand-written sample of what it guards goes stale by design.
    """
    sup = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    want = sorted({m.translate(sup) for m in
                   re.findall(r"\d×10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+", draft)})
    assert len(want) >= 3, f"only {len(want)} scientific-notation figures in the draft: {want}"
    for tok in want:
        base, exp = tok.split("-", 1)
        assert re.search(re.escape(base) + r"-?\s*" + exp, pdf_text), (
            f"{tok} is truncated or missing on the page")


def test_the_font_carries_bold_and_italic():
    """A family whose bold the engine cannot resolve sets \\textbf in the regular face.

    That shipped: 79 pages with no bold anywhere and an `OK` from the build script.
    """
    if not PDF.exists() or not shutil.which("pdffonts"):
        pytest.skip("no PDF or no pdffonts")
    fonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True, check=False).stdout.lower()
    assert "bold" in fonts, "the PDF embeds no bold face"
    assert "italic" in fonts or "oblique" in fonts, "the PDF embeds no italic face"


def test_the_pdf_was_built_from_this_manuscript():
    """Content, not clocks. See `_stale` for why the mtime version had to go."""
    if not PDF.exists():
        pytest.skip("no PDF built")
    stamped = bp.pdf_fingerprint(PDF)
    if stamped is None:
        pytest.skip("PDF carries no fingerprint (built before the stamp, or no poppler)")
    want = bp.draft_fingerprint(DRAFT.read_text(encoding="utf-8"))
    assert stamped == want, (
        f"the PDF was built from manuscript {stamped}, the tree holds {want} — "
        f"rebuild with `python3 src/build_pdf.py`")


def test_the_fingerprint_would_notice_a_changed_manuscript():
    """A hash check that cannot fail is a comment.

    One character of prose must change the fingerprint; the same text must reproduce it.
    """
    md = DRAFT.read_text(encoding="utf-8")
    assert bp.draft_fingerprint(md) == bp.draft_fingerprint(md), "not deterministic"
    assert bp.draft_fingerprint(md) != bp.draft_fingerprint(md + " "), "insensitive to an edit"


def test_the_check_survives_a_clone(tmp_path):
    """The failure this replaced: identical files, arbitrary mtimes, red suite.

    Copying without preserving timestamps is what `git clone` does to a working tree. The
    old check called that stale; this one has to call it current.
    """
    if not PDF.exists() or bp.pdf_fingerprint(PDF) is None:
        pytest.skip("no fingerprinted PDF")
    import shutil as sh
    pdf2, md2 = tmp_path / PDF.name, tmp_path / DRAFT.name
    sh.copyfile(PDF, pdf2)                       # copyfile does NOT carry mtime
    sh.copyfile(DRAFT, md2)
    import os
    os.utime(pdf2, (0, 0))                       # PDF now looks decades older than the draft
    assert pdf2.stat().st_mtime < md2.stat().st_mtime, "the probe did not create skew"
    assert bp.pdf_fingerprint(pdf2) == bp.draft_fingerprint(md2.read_text(encoding="utf-8")), \
        "the content check followed the clock instead of the bytes"


# The three pages this repository actually produced while chasing one line break, kept
# verbatim from `pdftotext -raw`. The guard above is worth exactly what these prove it is.
_SHIPPED_PAGES = {
    "xurl, as pandoc loads it":
        "figures: https://github.com/mkzung/unicorn-valu\nation-disagreement. python3 src",
    "UrlBreaks emptied, muskip left behind":
        "figures: https : //github.com/mkzung/unicorn valuation- disagreement. python3 src",
    "both undone, which is what ships":
        "figures: https://github.com/mkzung/unicorn-\nvaluation-disagreement. python3 src",
}


def test_the_url_guard_fails_on_the_pages_that_were_actually_shipped():
    """Two of these three went out before anyone noticed, and one referee report each.

    The first is xurl breaking mid-word. The second is what emptying `\\UrlBreaks` alone
    produced — worse, with gaps at every mark. Both must be caught, and the third must not be:
    a break after the hyphen that is really in "unicorn-" is where a URL is allowed to break,
    and a guard that also rejected that would have no correct page left to accept.
    """
    for name, page in _SHIPPED_PAGES.items():
        faults, checked = url_faults(page)
        assert checked == 1, f"{name}: the probe did not find the URL at all"
        if name.startswith("both undone"):
            assert not faults, f"{name}: a legitimate break rejected — {faults}"
        else:
            assert faults, f"{name}: this page shipped broken and the guard passed it"
