#!/usr/bin/env python3
"""Render paper/references.bib as a formatted, alphabetical reference list.

`paper/references.bib` is the single structured source of truth for the paper's
bibliography. The PDF/markdown pipeline (`src/build_pdf.py`) carries `draft.md`
prose straight through pandoc, and *this repo's pandoc (2.9) predates the
built-in `--citeproc` processor* (added in pandoc 2.11), so rather than bolt on
a fragile external `pandoc-citeproc` filter we render the reference list
deterministically here and pin `draft.md`'s "References" section to this output
with a CI test (`tests/test_references.py`). Change a `.bib` entry -> regenerate
-> the test fails until `draft.md` is updated, so the structured bibliography and
the manuscript prose cannot silently drift -- the same anti-drift discipline
`src/paper_numbers.py` enforces for the quoted numbers.

Pure text, no network. `python3 src/references.py` prints the list; `python3
src/references.py --check` exits non-zero if draft.md is out of sync with the
rendered list.

Author-date style (alphabetical by first-author surname / corporate name):
  Article: Authors (Year). "Title." *Journal* Vol(No), pp. https://doi.org/...
  Misc:    Authors (Year). "Title." [Month Year.] URL (accessed YYYY-MM-DD).
           (report-type @misc with no URL renders the title in italics.)
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BIB = REPO / "paper" / "references.bib"
DRAFT = REPO / "paper" / "draft.md"


@dataclass
class Entry:
    key: str
    etype: str
    fields: dict


# --------------------------------------------------------------------------- #
# A small, sufficient BibTeX reader (balanced-brace field values).
# --------------------------------------------------------------------------- #
def _read_braced(text: str, j: int) -> tuple[str, int]:
    """text[j] must be '{'; return (inner_text, index_just_after_closing_brace)."""
    assert text[j] == "{"
    depth, start = 0, j
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces in references.bib")


def parse_bib(text: str) -> list[Entry]:
    entries: list[Entry] = []
    n = len(text)
    i = 0
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,]+),", text[at:])
        if not m:
            i = at + 1
            continue
        etype, key = m.group(1).lower(), m.group(2).strip()
        j = at + m.end()
        fields: dict[str, str] = {}
        while True:
            fm = re.match(r"\s*(\w+)\s*=\s*", text[j:])
            if not fm:
                break
            j += fm.end()
            fname = fm.group(1).lower()
            if j < n and text[j] == "{":
                val, j = _read_braced(text, j)
            else:                                   # bare numeric/word value
                k = j
                while k < n and text[k] not in ",}\n":
                    k += 1
                val, j = text[j:k].strip(), k
            fields[fname] = val
            while j < n and text[j] in ", \t\n":    # eat the separator(s)
                j += 1
            if j < n and text[j] == "}":            # end of this entry
                j += 1
                break
        entries.append(Entry(key, etype, fields))
        i = j
    return entries


# --------------------------------------------------------------------------- #
# Field cleaning + author formatting.
# --------------------------------------------------------------------------- #
def _clean(s: str) -> str:
    s = s.replace("\n", " ")
    s = re.sub(r"\\url\{([^}]*)\}", r"\1", s)
    s = s.replace("\\&", "&").replace("~", " ")
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def _initials(given: str) -> str:
    """'Ilya A.' -> 'I. A.'; 'Brad M.' -> 'B. M.'; 'Will' -> 'W.'"""
    toks = [t for t in re.split(r"[ .]+", given) if t]
    return " ".join(f"{t[0]}." for t in toks)


def format_authors(raw: str) -> str:
    """BibTeX author field -> author-date string. Corporate authors (wrapped in an
    extra brace pair in the .bib, so the value still starts with '{') are kept
    verbatim and never split on ' and '."""
    raw = raw.strip()
    if raw.startswith("{"):                          # corporate / institutional
        return _clean(raw)
    people = [p.strip() for p in re.split(r"\s+and\s+", raw) if p.strip()]
    names: list[str] = []
    for idx, person in enumerate(people):
        if "," in person:
            last, given = (x.strip() for x in person.split(",", 1))
            ini = _initials(given)
        else:                                        # "First Last"
            parts = person.split()
            last, ini = parts[-1], _initials(" ".join(parts[:-1]))
        names.append((f"{last}, {ini}" if idx == 0 else f"{ini} {last}").strip().rstrip(","))
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]}, and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def _sort_key(e: Entry) -> str:
    raw = e.fields.get("author", "").strip()
    if raw.startswith("{"):
        return _clean(raw).lower()
    first = re.split(r"\s+and\s+", raw)[0]
    last = first.split(",")[0] if "," in first else first.split()[-1]
    return _clean(last).lower()


def _accessed(note: str) -> str:
    m = re.search(r"Accessed (\d{4}-\d{2}-\d{2})", note)
    return f" (accessed {m.group(1)})" if m else ""


_MONTHS = {"jan": "January", "feb": "February", "mar": "March", "apr": "April",
           "may": "May", "jun": "June", "jul": "July", "aug": "August",
           "sep": "September", "oct": "October", "nov": "November", "dec": "December"}


def render_entry(e: Entry) -> str:
    f = {k: _clean(v) for k, v in e.fields.items()}
    authors = format_authors(e.fields.get("author", ""))
    year = f.get("year", "n.d.")
    title = f.get("title", "").rstrip(".")
    dot = "" if title.endswith(("?", "!")) else "."
    if e.etype == "article":
        out = f'{authors} ({year}). "{title}{dot}" *{f.get("journal", "")}*'
        if f.get("volume"):
            out += f' {f["volume"]}'
            if f.get("number"):
                out += f'({f["number"]})'
        if f.get("pages"):
            out += f', {f["pages"].replace("--", "–")}'
        out += "."
        if f.get("doi"):
            out += f' https://doi.org/{f["doi"]}'
        return out
    # @misc and friends
    url = ""
    hp = e.fields.get("howpublished", "")
    mu = re.search(r"\\url\{([^}]*)\}", hp) or re.search(r"(https?://\S+)", _clean(hp))
    if mu:
        url = mu.group(1)
    if url:                                          # web / data source -> quote title
        out = f'{authors} ({year}). "{title}{dot}"'
        if f.get("month"):
            out += f' {_MONTHS.get(f["month"][:3].lower(), f["month"])} {year}.'
        out += f" {url}{_accessed(f.get('note', ''))}."
        return out
    # Report-type entries (no URL): italic title, then what kind of document it is and where
    # to get it. `note` is printed only when it IS the document type — the WEF entry's
    # "Insight Report" — and not when it is an annotation. Every @article carries an
    # annotation and the article branch above drops it; this branch printed it, so adding a
    # working paper put a paragraph of commentary into the reference list.
    ANNOTATION = 60
    out = f'{authors} ({year}). *{title}{dot}*'
    note = f.get("note", "")
    if note and len(note) <= ANNOTATION:
        out += f" {note.rstrip('.')}."
    elif f.get("institution"):
        out += f' {f["institution"].rstrip(".")}.'
    if f.get("doi"):
        out += f' https://doi.org/{f["doi"]}'
    return out


def render_reference_list(entries: list[Entry] | None = None) -> str:
    if entries is None:
        entries = parse_bib(BIB.read_text(encoding="utf-8"))
    ordered = sorted(entries, key=_sort_key)
    return "\n\n".join(render_entry(e) for e in ordered)


def main(argv: list[str]) -> int:
    rendered = render_reference_list()
    if "--check" in argv:
        draft = DRAFT.read_text(encoding="utf-8")
        missing = [ln for ln in rendered.split("\n\n") if ln.strip() and ln not in draft]
        if missing:
            sys.stderr.write("draft.md REFERENCES out of sync; missing entries:\n"
                             + "\n".join(f"  - {m[:80]}..." for m in missing) + "\n")
            return 1
        print(f"OK: all {len(rendered.split(chr(10)+chr(10)))} references present in draft.md")
        return 0
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
