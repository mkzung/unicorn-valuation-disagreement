"""Every pointer in the paper resolves, and the numbering it points into has no holes.

`tests/test_readme_pointers.py` does this for the README and nothing did it for the paper,
which is the wrong way round: a reader forgives a stale README and does not forgive a paper
that refers him to Appendix C when there is no Appendix C.

Resolvability is the easy half and it was already clean. The half that was not clean, and
that no guard here could see, is numbering with a hole in it. Two structural cuts had left:

  * appendices lettered A, D, E, F, G — B and C went with the secondary and cycle legs, so
    a reader met a sequence that says "two appendices are missing from this file";
  * body tables 1–6 and 8–18, with Table 7 sitting inside an appendix after Table E.1,
    because the exits table kept its body number when it moved.

Both resolve perfectly. `Appendix E.5` existed, `Table 7` existed. That is exactly why this
file checks the shape of the sequence and not only the destination of each arrow.

The numbering itself is derived by the assembler's `renumber` pass, so these tests assert a
property of its output. They are cheap and they are the only thing standing between the next
structural edit and another silent hole.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")

_SEC = re.compile(r"^## (\d+)\. ", re.M)
_SUB = re.compile(r"^### (\d+)\.(\d+) ", re.M)
_APX = re.compile(r"^## Appendix ([A-Z])\. ", re.M)
_APX_SUB = re.compile(r"^### ([A-Z])\.(\d+) ", re.M)
_CAPTION = re.compile(r"^\*\*Table ([A-Z]\.\d+|\d+)\.\*\*", re.M)
_FIGURE = re.compile(r"`(figures/[a-z_]+\.png)`")


def headings() -> set[str]:
    out = {m.group(1) for m in _SEC.finditer(DRAFT)}
    out |= {m.group(1) for m in _APX.finditer(DRAFT)}
    out |= {f"{m.group(1)}.{m.group(2)}" for m in _SUB.finditer(DRAFT)}
    out |= {f"{m.group(1)}.{m.group(2)}" for m in _APX_SUB.finditer(DRAFT)}
    return out


def captions() -> list[str]:
    return [m.group(1) for m in _CAPTION.finditer(DRAFT)]


def test_the_scrape_sees_the_paper():
    """Empty scrapes make every assertion below vacuous."""
    assert len(headings()) > 50, f"only {len(headings())} headings found"
    assert len(captions()) > 15, f"only {len(captions())} table captions found"
    assert "11" in headings() and "A" in headings()


def test_the_body_sections_run_without_a_gap():
    nums = sorted(int(m.group(1)) for m in _SEC.finditer(DRAFT))
    assert nums == list(range(1, len(nums) + 1)), f"body sections are {nums}"


def test_every_subsection_sequence_runs_without_a_gap():
    """§8 jumping from 8.9 to 8.11 means a subsection was cut and nothing renumbered."""
    groups: dict[str, list[int]] = {}
    for m in list(_SUB.finditer(DRAFT)) + list(_APX_SUB.finditer(DRAFT)):
        groups.setdefault(m.group(1), []).append(int(m.group(2)))
    bad = [f"§{k}: {v}" for k, v in groups.items() if v != list(range(1, len(v) + 1))]
    assert not bad, "subsection numbering has a hole or is out of order:\n  " + "\n  ".join(bad)


def test_the_appendices_are_lettered_without_a_gap():
    """A, D, E, F, G is what this test exists for."""
    letters = [m.group(1) for m in _APX.finditer(DRAFT)]
    want = [chr(ord("A") + i) for i in range(len(letters))]
    assert letters == want, f"appendices are lettered {letters}, expected {want}"


def test_the_tables_are_numbered_in_the_order_they_appear():
    """Body tables count 1..N; an appendix table is <its letter>.k.

    The failure this replaces: Table 7 inside Appendix F, printed after Table E.1.
    """
    first_apx = DRAFT.find("\n## Appendix ")
    body, per_apx, expected = 0, {}, []
    for m in _CAPTION.finditer(DRAFT):
        if m.start() < first_apx:
            body += 1
            expected.append(str(body))
        else:
            letter = [h.group(1) for h in _APX.finditer(DRAFT) if h.start() < m.start()][-1]
            per_apx[letter] = per_apx.get(letter, 0) + 1
            expected.append(f"{letter}.{per_apx[letter]}")
    assert captions() == expected, (
        f"tables are captioned {captions()}\n            expected {expected}")


def test_every_pointer_resolves():
    # `§` followed by a LETTER as well as by a number. The section sign in front of an
    # appendix subsection is not a form this paper uses, so the pattern was numeric-only —
    # and that is exactly why it could not see `§I.2` and `§I.3` when the NAV wedge moved out
    # of the body and its two internal pointers were rewritten in pre-renumber letters. Both
    # shipped into the PDF. `renumber` resolves `Appendix I.2`; it has no reason to resolve a
    # form the manuscript never uses, so the guard has to reject that form rather than skip it.
    have, tables, bad = headings(), set(captions()), []
    for m in re.finditer(r"§([A-Z]\.\d+|[A-Z](?![a-z])|\d+(?:\.\d+)?)", DRAFT):
        if m.group(1) not in have:
            bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: §{m.group(1)}")
    for m in re.finditer(r"Appendi(?:x|ces) ([A-Z])(?:\.(\d+))?", DRAFT):
        key = m.group(1) if m.group(2) is None else f"{m.group(1)}.{m.group(2)}"
        if key not in have:
            bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: Appendix {key}")
    for m in re.finditer(r"Table ([A-Z]\.\d+|\d+)", DRAFT):
        if m.group(1) not in tables:
            bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: Table {m.group(1)}")
    assert not bad, "pointer(s) with no destination:\n  " + "\n  ".join(bad)


def test_every_figure_caption_figure_is_one_the_paper_states():
    """Figure captions are the one place a number reaches the page unguarded.

    The registry pins prose in `paper/draft.md`. A caption lives in `build_pdf.FIG_DEFS`,
    which the registry never reads and the manuscript never contains, so a figure could carry
    any number at all. One did: the IPO-exit caption said "the last fund mark sits within
    ~8%" beside a chart showing that mark at -25% on Circle and -28% on Figma. The claim was
    true of the four down-round names it was written about and false of the seven on the page.

    A caption is a summary, so it may round and it may use words the body does not. What it
    may not do is state a figure the paper states nowhere: that is a number no run recomputes.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import build_pdf as bp

    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = " ".join(draft.split())
    fig = re.compile(r"(?<![\d.])[\d][\d.,]*%|\$[\d.,]+[BMT]|\b\d{1,3}(?:,\d{3})+\b")
    loose = []
    for path, (caption, _width) in bp.FIG_DEFS.items():
        for m in fig.finditer(caption):
            tok = m.group(0)
            if tok in body or tok.lstrip("+") in body:
                continue
            loose.append(f"{path}: {tok}")
    assert not loose, (
        "figure caption(s) state a figure the manuscript does not, so nothing recomputes "
        "it:\n  " + "\n  ".join(loose))
    # Vacuous if the scan reads no captions or finds no figures in them.
    assert len(bp.FIG_DEFS) == 6, f"{len(bp.FIG_DEFS)} figures; re-point this guard"
    # Ten is the count on the run that added this guard, not a round number: the three
    # captions between them state ten percentages, dollar totals and grouped counts.
    assert sum(len(fig.findall(c)) for c, _ in bp.FIG_DEFS.values()) >= 10, (
        "the caption scan found almost no figures; it is reading the wrong field")


def test_no_appendix_pointer_hides_from_the_renumbering_pass():
    """`renumber()` derives the appendix letters from order of appearance and rewrites every
    pointer it can see. What it looks for is the word: `Appendix G.3`. A pointer written
    `§G.3` is invisible to it, so it keeps whatever letter the author typed while every other
    reference to the same subsection moves.

    One existed, in §8.4, and it pointed at the right subsection by luck: the letter it named
    happened to survive the pass unchanged. That is the failure this cannot detect from the
    output, because a stale pointer and a correct one look identical until the appendices move.
    """
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    hidden = re.findall(r"§[A-Z]\.\d+", draft)
    assert not hidden, (
        "appendix pointer(s) written with § instead of the word 'Appendix', which the "
        f"renumbering pass cannot rewrite: {sorted(set(hidden))}")
    # The check is worthless if the manuscript has no appendix pointers at all.
    assert len(re.findall(r"Appendix [A-Z]\.\d+", draft)) > 15, (
        "almost no appendix subsection pointers found; this guard is scanning the wrong text")

    # The third spelling, and the one that shipped: no prefix at all. §5.2 read "Appendix H.1
    # supplies the reason … H.1 uses that to defend §8". The first pointer moved with the
    # appendices and the bare one kept the letter the source typed, so the sentence named an
    # appendix H in a paper lettered A to G. Headings and `Table X.Y` labels have the same
    # shape and are rewritten by their own passes, so they are excluded here — as is Form
    # N-CEN's Item C.9, which is an item number on a filing and collides by coincidence.
    body = "\n".join(ln for ln in draft.split("\n") if not ln.lstrip().startswith("#"))
    for pat in (r"(?:Table|Figure|Appendix|Item)\s+[A-Z]\.\d+", r"\*\*[A-Z]\.\d+"):
        body = re.sub(pat, " ", body)
    bare = sorted(set(re.findall(r"(?<![\w.])([A-Z]\.\d+)(?![\d.])", body)))
    assert not bare, (
        "appendix pointer(s) written with no prefix, which the renumbering pass cannot see, "
        f"so they keep whatever letter the source typed: {bare}")


def test_a_pointer_spelled_in_words_resolves_too():
    """`Section 7.2` is a pointer and `§7.2` is a pointer; only one of them was checked.

    The paper says "Section 5 measures…" in prose and "§5.1" in parentheses, and the scan above
    only reads the second. §10.1 spent a round pointing at "Section 7.2" — a subsection that
    left with the sector contrast — and every pointer test passed, because the regex was
    looking for a section sign. A guard that checks one spelling of a thing checks one spelling
    of a thing.
    """
    have, bad = headings(), []
    for m in re.finditer(r"\b[Ss]ections? (\d+(?:\.\d+)?)", DRAFT):
        if m.group(1) not in have:
            bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: {m.group(0)}")
    assert not bad, "section(s) named in words with no destination:\n  " + "\n  ".join(bad)
    # The scan must find something: "Section" appears throughout the road map and §8's opening.
    assert len(re.findall(r"\b[Ss]ections? \d", DRAFT)) > 10, "the word-form scan found nothing"


def test_the_paper_does_not_use_round_for_its_own_revisions():
    """"Round" is this paper's central technical term. It may not also mean a draft.

    A funding round is the event the whole of §8 is about. Two body sentences used the same
    word for a revision of the paper — "each of four rounds of this paper found a class the
    last one missed", "two rounds of this work before the statistic existed" — and a reader
    who has just been told that a round is a priced financing event has to stop and re-parse.
    Private vocabulary is worse than untidy when it collides with a defined term.
    """
    bad = []
    for m in re.finditer(r"\b(?:\w+) rounds? of (?:this|that) (?:paper|work|study|version)", DRAFT):
        bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: {m.group(0)}")
    for m in re.finditer(r"\b(?:two|three|four|five|several) rounds (?:ago|earlier|before)", DRAFT):
        bad.append(f"line {DRAFT[:m.start()].count(chr(10)) + 1}: {m.group(0)}")
    assert not bad, ("\"round\" used for a revision of the paper, in a paper where it means a "
                     "financing event:\n  " + "\n  ".join(bad))
    # The scan has to be able to see the word at all.
    assert DRAFT.count("round") > 100, "the manuscript scrape lost the word this test is about"


def test_the_paper_keeps_one_voice():
    """No "we" in a single-author paper, and no third person for its own author.

    "In a paper whose chief risk is that the author found what he was looking for" shipped for
    several versions. It is a single-author paper; "the author" reads as though someone else
    wrote it, and the pronoun then has to guess a gender. First person for the choices the
    author made, "this paper" for what the document does, and nothing else.
    """
    body = DRAFT[DRAFT.index("\n## 1. "):DRAFT.index("\n## Appendix A")]
    bad = []
    for pat, why in [(r"\b(?:we|our)\b(?! own)", "first person plural in a single-author paper"),
                     (r"\bthe author\b", "third person for the author"),
                     (r"\bthis (?:study|work)\b", "a third name for the paper")]:
        for m in re.finditer(pat, body, re.I):
            line = body[:m.start()].count(chr(10)) + 1
            bad.append(f"{m.group(0)!r} ({why}), near line {line} of the body")
    assert not bad, "voice:\n  " + "\n  ".join(bad)


def test_the_pointer_check_can_fail():
    """On a manuscript with one letter changed, each branch must report it."""
    have, tables = headings(), set(captions())
    assert "Z" not in have and "99" not in tables
    assert "C.5" in have, "the appendix subsection the checks above rely on is gone"


def test_every_figure_the_paper_cites_is_in_the_repository():
    """A path in the prose is a promise the file exists; three legs left the paper."""
    missing = sorted({p for p in _FIGURE.findall(DRAFT) if not (ROOT / p).exists()})
    assert not missing, "figure(s) cited by the paper but absent:\n  " + "\n  ".join(missing)


def test_every_figure_the_pdf_prints_still_has_its_trigger():
    """A `figures/x.png` in the prose is not decoration: it is where the float is injected.

    `src/build_pdf.py` places each figure after the paragraph that cites it and fails if a
    trigger is missing. Taking file paths out of the body — a reasonable thing to want, since
    a path inside a sentence reads like a README — removed the one in §5.3 and with it the
    only instruction to print the population figure. Caught by the build, but only after the
    manuscript had already been assembled and read.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import build_pdf as bp
    cited = set(_FIGURE.findall(DRAFT))
    missing = sorted(t for t, _ in bp.FIG_GROUPS if t in bp.FIG_DEFS and t not in cited)
    assert not missing, (
        "figure(s) the PDF builder expects to inject, with no citation left in the prose:\n  "
        + "\n  ".join(missing))


def test_the_figures_directory_holds_exactly_what_the_paper_cites():
    """The other direction of the test above, and the one that was missing.

    Three legs were cut from this paper — the Forge secondary index, the prediction markets
    and the valuation cycle — and their six figures stayed in `figures/`: `coverage_matrix`,
    `forge_vs_fundmarks`, `fund_marks_timeseries`, `gap_chart`, `headline_vs_forge` and
    `prediction_markets`. A reader who opens the repository after reading §3.4, which says
    those signals are not used, finds a megabyte and a half of charts built on them. Nothing
    was wrong with any individual file; what was wrong is that no check could see them.
    """
    cited = set(_FIGURE.findall(DRAFT))
    have = {f"figures/{p.name}" for p in (ROOT / "figures").glob("*.png")}
    assert have == cited, (
        f"figures/ holds {sorted(have - cited)} that the paper does not cite; "
        f"the paper cites {sorted(cited - have)} that are not in figures/")


def test_every_table_caption_is_referred_to_somewhere():
    """A table nobody points at is a table the reader has no reason to read.

    Counted outside the caption line itself, so a caption does not vouch for its own table.
    """
    orphan = []
    for cap in captions():
        refs = len(re.findall(rf"Table {re.escape(cap)}\b", DRAFT))
        if refs <= 1:
            orphan.append(f"Table {cap} is captioned and never referred to")
    assert not orphan, "\n  ".join(orphan)


def test_the_notes_point_at_sections_the_paper_has():
    """`notes/` ships inside the replication package and is written in the paper's numbering.

    The relettering that closed the appendix hole left `notes/registration.md` pointing at
    Appendix E.5, which is now C.5 — one stale pointer in a file a referee reads to check that
    the registration predates the data. Cheap to check, and nothing else was checking it.
    """
    have, bad = headings(), []
    for f in sorted((ROOT / "notes").glob("*.md")):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"§(\d+(?:\.\d+)?)", t):
            if m.group(1) not in have:
                bad.append(f"{f.name}: §{m.group(1)}")
        for m in re.finditer(r"Appendi(?:x|ces) ([A-Z])(?:\.(\d+))?", t):
            key = m.group(1) if m.group(2) is None else f"{m.group(1)}.{m.group(2)}"
            if key not in have:
                bad.append(f"{f.name}: Appendix {key}")
    assert not bad, "note(s) pointing at a section the paper does not have:\n  " + "\n  ".join(bad)
