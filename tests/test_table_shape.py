"""Every markdown table in the manuscript is rectangular, and every one has a caption.

A ragged table is not a rendering bug you notice — pandoc pads the short row with an empty
cell and the PDF looks plausible, so a dropped value becomes a blank the eye reads as "not
applicable". The paper carries twenty-one tables and a reader checks the arithmetic of the
ones that interest him; nobody counts cells.

Splitting on a bare `|` is wrong here and was wrong when this was first written by hand:
three tables carry an escaped pipe inside a cell (`Median \\|wedge\\| (bps)`,
`median \\|Forge − independent\\|`, `paired Wilcoxon on \\|errors\\|`) because the quantity
really is an absolute value. A naive split reported all three as ragged. They render
correctly; the checker was wrong, not the paper.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")

_ESCAPED_PIPE = re.compile(r"\\\|")
_RULE = re.compile(r"^[\s|:-]+$")


def cells(row: str) -> int:
    """Cells in a pipe-table row, with escaped pipes held out of the split."""
    return len(_ESCAPED_PIPE.sub("\x00", row).strip().strip("|").split("|"))


def tables():
    """(first line number, header, body rows) for every pipe table in the draft."""
    lines = DRAFT.split("\n")
    i = 0
    while i < len(lines):
        if not lines[i].startswith("|"):
            i += 1
            continue
        start, run = i, []
        while i < len(lines) and lines[i].startswith("|"):
            run.append(lines[i])
            i += 1
        yield start + 1, run[0], [r for r in run[1:] if not _RULE.fullmatch(r)]


def test_the_scan_finds_every_table():
    found = list(tables())
    assert len(found) == 25, f"expected the paper's 25 tables, scanned {len(found)}"


def test_the_cell_counter_handles_an_escaped_pipe():
    """The check has to be right about the thing that made the first version wrong."""
    assert cells(r"| a | b | c |") == 3
    assert cells(r"| Median \|wedge\| (bps) | b | c |") == 3
    assert cells(r"| a | b |") != 3


def test_every_table_is_rectangular():
    bad = []
    for line, header, body in tables():
        n = cells(header)
        for k, row in enumerate(body):
            if cells(row) != n:
                bad.append(f"draft line {line + k + 2}: {cells(row)} cells against a "
                           f"{n}-column header — {row[:70]}")
    assert not bad, "ragged table row(s):\n  " + "\n  ".join(bad)


def test_every_table_has_a_caption_above_it():
    """A table with no caption is a table a reader cannot cite or check."""
    lines = DRAFT.split("\n")
    bad = []
    for line, header, _ in tables():
        window = " ".join(lines[max(0, line - 4):line - 1])
        if not re.search(r"\*\*Table [A-Z]?\.?\d+(?:\.\d+)?\.\*\*", window):
            bad.append(f"draft line {line}: {header[:70]}")
    assert not bad, "table(s) with no caption in the three lines above:\n  " + "\n  ".join(bad)


def test_every_number_in_the_decomposition_table_is_registered():
    """Table C.1 is a claim per cell, and three of its five bands were pinned.

    The two that were not — `partial` and `mixed` — are exactly the two that went stale: the
    table shipped 591 and 1,373 where the code returns 590 and 1,374, two cells swapping
    bands after the series-regex correction. Nothing caught it. The registry only sees a
    figure it has been given, the arithmetic audit passed because both readings sum to 4,271,
    and the decomposition figure — drawn from the same production call — printed the right
    numbers beside a table printing the wrong ones for one release.

    So this reads the table itself rather than a list of what someone remembered to pin: every
    number in it has to be a token some registry entry claims. A cell nobody registered is a
    number nothing recomputes, which is the whole failure in one sentence.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import paper_numbers as pn

    caption = "**Table C.1.**"
    assert caption in DRAFT, "Table C.1's caption has moved; re-point this guard"
    start = DRAFT.index(caption)
    rows = [ln for ln in DRAFT[start:].split("\n\n")[1].split("\n") if ln.startswith("|")]
    assert len(rows) >= 6, f"only {len(rows)} rows found under {caption}"

    pinned = set()
    for n in pn.canonical_numbers():
        for phrase in (n.claim, *n.context.values()):
            if phrase:
                pinned.update(re.findall(r"[\d][\d.,]*%?", pn._demark(phrase)))

    loose = []
    for row in rows[2:]:                       # skip the header and its rule
        for tok in re.findall(r"(?<![\w.])[\d][\d.,]*%?(?![\w])", row):
            if tok not in pinned:
                loose.append(f"{tok} in: {row[:64]}")
    assert not loose, (
        "number(s) in Table C.1 that no registry entry claims, so nothing recomputes "
        "them:\n  " + "\n  ".join(loose))
