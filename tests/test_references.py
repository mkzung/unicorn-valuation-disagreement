"""
Bibliography drift guard (v0.21).

`paper/references.bib` is the structured source of truth for the paper's
bibliography; `src/references.py` renders it (author-date, alphabetical) and
`paper/draft.md`'s "## References" section must contain exactly that rendered
list. This is the same failure mode `tests/test_paper_consistency.py` closes for
the quoted *numbers* — prose left stale after the source moved — applied to the
references: edit a `.bib` entry without regenerating the manuscript and CI fails.

(This repo's pandoc is 2.9, which predates the built-in `--citeproc`, so the list
is rendered deterministically in Python rather than by an external citeproc
filter; the test is what keeps the two representations honest.)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import references as refs

DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
ENTRIES = refs.parse_bib((ROOT / "paper" / "references.bib").read_text(encoding="utf-8"))


def _references_section() -> str:
    """The body of draft.md's '## References' section (References is the last section)."""
    i = DRAFT.index("## References")
    return DRAFT[i:]


def test_bib_parses_all_entries_well_formed():
    """Every .bib entry parses with the fields the renderer needs."""
    # Five entries went with the secondary/prediction-market legs cut to a second
    # paper: the Forge index note, Polymarket, Kalshi, Prediction News and the
    # specification-curve method paper. A bibliography that outlives its citations
    # is a reader following a pointer to nothing.
    assert len(ENTRIES) == 16, f"expected 16 bib entries, parsed {len(ENTRIES)}"
    keys = {e.key for e in ENTRIES}
    assert {"gornall2020squaring", "chernenko2021mutual", "kwon2020mutual",
            "agarwal2023private", "wef2026futurevc", "diether2002differences",
            "getmansky2004econometric", "brown2019private", "barber2017interim",
            "jenkinson2013fair", "ewens2020deregulation", "cochrane2005risk",
            "korteweg2010risk", "bias2026secondary", "zitzewitz2003who",
            # The working paper §1.3 names separately from the same team's journal article.
            # The References list carried its line and the bibliography did not generate it,
            # which a rendered-from-source list is supposed to make impossible.
            "agarwal2023investors"} == keys
    for e in ENTRIES:
        assert e.fields.get("author"), f"{e.key} has no author"
        assert e.fields.get("title"), f"{e.key} has no title"
        assert e.fields.get("year"), f"{e.key} has no year"


def test_render_is_alphabetical_and_complete():
    """The rendered list is 9 paragraphs, alphabetical by first-author / corporate name."""
    blocks = [b for b in refs.render_reference_list().split("\n\n") if b.strip()]
    assert len(blocks) == 16
    leads = [b.split(" (")[0] for b in blocks]
    assert leads == sorted(leads, key=str.lower), f"not alphabetical: {leads}"
    # spot-check the author-date signatures the in-text citations rely on
    joined = "\n".join(blocks)
    assert "Gornall, W., and I. A. Strebulaev (2020)." in joined
    assert "Chernenko, S., J. Lerner, and Y. Zeng (2021)." in joined
    assert "Agarwal, V., B. M. Barber, S. Cheng, A. Hameed, and A. Yasuda (2023)." in joined
    assert "World Economic Forum and Stanford GSB Venture Capital Initiative (2026)." in joined


def test_draft_references_section_is_in_sync_with_bib():
    """Every rendered entry appears verbatim in draft.md's References section — the
    core anti-drift guard. references.py --check enforces the same thing on the CLI."""
    section = _references_section()
    missing = [b for b in refs.render_reference_list().split("\n\n")
               if b.strip() and b not in section]
    assert not missing, ("draft.md References out of sync with references.bib:\n"
                         + "\n".join(f"  - {m[:90]}" for m in missing))


def test_every_reference_carries_year_and_title_token():
    """Defensive: each entry's year and a distinctive title word are present in the
    section, so a malformed render (e.g. an empty field) cannot pass silently."""
    section = _references_section()
    for e in ENTRIES:
        year = refs._clean(e.fields["year"])
        assert year in section, f"{e.key}: year {year} missing from References"
        # a content word from the title (>4 chars, not a stop-ish token)
        title_words = [w for w in re.findall(r"[A-Za-z]+", e.fields["title"]) if len(w) > 4]
        assert any(w in section for w in title_words), f"{e.key}: no title word in References"


def test_academic_anchors_cited_in_body():
    """The four scholarly works are cited in the running text, not only listed — so the
    reference list documents actual citations (the data sources are cited in §2/§4)."""
    body = DRAFT[:DRAFT.index("## References")]
    assert "Gornall and Strebulaev (2020)" in body
    assert "Chernenko, Lerner and Zeng (2021" in body
    assert "Kwon, Lowry and Qian (2020" in body
    # The first mention names all five authors, because the companion working paper adds a
    # sixth and "et al." on both would read as one work cited twice.
    assert "Agarwal, Barber, Cheng, Hameed and Yasuda (2023)" in body
    assert "Agarwal, Barber, Cheng, Hameed, Shanker and Yasuda (2023, working paper)" in body
    # WEF report now cited too (so every bib entry is used, not just listed)
    assert "World Economic Forum and Stanford GSB Venture Capital Initiative (2026)" in body
