#!/usr/bin/env python3
"""Build the SSRN/arXiv-ready PDF from paper/draft.md + figures.

Pipeline: draft.md -> paper/_build.md (title-block YAML + figures injected
inline with numbered captions) -> pandoc (xelatex) -> paper/unicorn_valuation_disagreement.pdf

Design choices (all reversible; draft.md is never mutated):
- The draft uses literal '$' for dollars throughout, so pandoc's $...$ math
  parsing is DISABLED (-f markdown-tex_math_dollars). Otherwise "$39B ... $9.9B"
  is read as math and mangled.
- xelatex with TeX Gyre Termes (Times-like). Every non-ASCII symbol the draft
  uses (-> x >= Sigma => in rho minus) is mapped via newunicodechar so it
  renders regardless of the text font (math glyphs come from the math font).
- Figures are auto-numbered by LaTeX; the in-text "(`figures/x.png`)" pointers
  are rewritten to "(Figure N)" in the SAME order the floats are injected, so
  the numbers always line up.

Requires: pandoc, xelatex, newunicodechar.sty (texlive). No network.
"""
from __future__ import annotations
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRAFT = REPO / "paper" / "draft.md"
BUILD_MD = REPO / "paper" / "_build.md"
HEADER_TEX = REPO / "paper" / "_header.tex"
OUT_PDF = REPO / "paper" / "unicorn_valuation_disagreement.pdf"

DATE_LINE = "Independent Researcher · MAM, London Business School"

# Title-page footnote (working-paper convention): version line, contact,
# comments-welcome, replication pointer, errors-own. Rendered via \thanks.
# The one place this date is set. It is also printed in the manuscript's own front
# matter, and the two used to be two hand-maintained copies of one fact: the title page
# claimed 12 August while the paper carried four days of corrections past it.
# `tests/test_version_consistency.py` compares all three copies and fails when the
# manuscript has moved past whichever date they agree on.
VERSION_DATE = "September 5, 2026"

AUTHOR_THANKS = (f"First draft: June 2026. This version: {VERSION_DATE}. "
                 "Contact: gorbuk.maxim@gmail.com. Comments welcome. "
                 "Replication package (Internet Appendix): "
                 "https://github.com/mkzung/unicorn-valuation-disagreement. "
                 "I declare no competing interests. All errors are my own.")

# caption + width per figure file.
FIG_DEFS = {
    "figures/ipo_validation.png": (
        "IPO-exit validation, 2023–2026 listings: two pre-IPO signals scored against "
        "the realized IPO valuation — the headline (last private round) and the last "
        "pre-IPO mutual-fund N-PORT mark (hatched; for Klarna, the 2022 down round). "
        "Bars show each signal’s error vs the IPO (0 = the IPO priced it right). "
        "On the four 2021-vintage down-round listings the headline overshoots by +56% to "
        "+294% and the fund mark on those same names sits within 8%; across all seven "
        "fund-held exits the fund mark's median absolute error is 11% against 48%. "
        "*Source:* SEC N-PORT filings (last pre-IPO marks), IPO terms from "
        "prospectuses and financial press; `data/ipo_validation.csv`.", "88%"),
    "figures/fund_marks_dispersion.png": (
        "Cross-fund dispersion of SEC N-PORT Level-3 fair-value marks for the same "
        "private security, same quarter: each fund’s implied price/share vs the "
        "cross-fund median; colour = fund family; label = number of funds and the "
        "max–min spread. *Source:* SEC N-PORT/NPORT-P filings (EDGAR), 2025–26; "
        "`data/fund_marks.csv`.", "88%"),
    "figures/population_spread.png": (
        "The population panel: every Level-3 private position registered funds reported "
        "in SEC bulk N-PORT, 2019Q4\u20132026Q2, compared between fund complexes rather "
        "than the legal trusts they file under (4,271 company-dates with \u22655 funds "
        "across \u22652 complexes, 656 companies, no name list). A: the distribution of "
        "the between-house spread. Only 17.0% of company-dates are unanimous and the median "
        "spread is 12.1%; \u00a74.3\u2019s ten-name median of 24% (dashed) sits at the 60th "
        "percentile, and scored the population\u2019s own way \u2014 between house medians "
        "rather than between funds \u2014 those same ten cells land in the same place. "
        "B: the same cells counted (solid) and weighted by the fair value "
        "funds booked (hatched); dark = above the 24% line. The widest spreads are the "
        "smallest positions. *Source:* SEC N-PORT quarterly bulk data sets (public domain); "
        "`data/nport_population_marks.csv.gz`.", "96%"),
    "figures/databricks_series_j.png": (
        "One lot, two books, three shared reporting dates. Databricks Series J, acquired "
        "17 December 2024 at an entry price both books disclose, carried by Alger and by "
        "Brighthouse. The prices are the filed markup applied to that entry price; the "
        "entry price is divided out of a filed cost and a filed share count. *Source:* SEC "
        "Form N-CSR schedules of investments; `data/ncsr_acquisitions.csv`.", "78%"),
    "figures/series_decomposition.png": (
        "What holding the security fixed does to the headline, and where it cannot be "
        "held fixed at all. A: the cells where two or more houses name the same series, "
        "scored with the series held fixed and scored the way the rest of the paper scores "
        "everything. B: the guarded panel split by what its filings name; the grey group is "
        "the one no filing describes, which the decomposition cannot reach. *Source:* SEC "
        "N-PORT quarterly bulk data sets; `data/nport_population_marks.csv.gz`.", "94%"),
    "figures/round_event_study.png": (
        "Between-house disagreement around a dated round. A: for each month relative to a "
        "company's nearest non-first dated round, the median deviation from that company's "
        "own median spread, with the two bands the step compares shaded and the cell count "
        "underneath. B: the same estimator with the anchor moved; a tick at zero marks an "
        "anchor whose median step is exactly zero. *Source:* SEC N-PORT quarterly bulk data "
        "sets, round dates recovered from the filings; `data/round_event_study.csv`.", "96%"),
}

# After the paragraph that cites <trigger>, inject these figures in order.
# Float order across the doc is the LaTeX figure order; the pointer map is derived from it.
#
# Six entries were removed here when the six orphan figures were deleted: gap_chart,
# headline_vs_forge, fund_marks_timeseries, forge_vs_fundmarks, prediction_markets and
# coverage_matrix all belong to the Forge, prediction-market and cycle legs that left this
# paper, and none of them had a citation in the prose any more. They cost nothing at build
# time — an uncited trigger is simply never found — which is why they survived three
# structural cuts.
#
# Listed in the order the manuscript cites them, because the float order IS the numbering:
# §2.1's lot, §3.3's decomposition, §5.3's population, §8.2's event study, then the two
# appendix figures. A referee counted three figures on seventy-two pages and none of them a
# picture of a result the paper leads with; the first, second and fourth are that answer.
FIG_GROUPS = [
    ("figures/databricks_series_j.png", ["figures/databricks_series_j.png"]),
    ("figures/series_decomposition.png", ["figures/series_decomposition.png"]),
    ("figures/population_spread.png", ["figures/population_spread.png"]),
    ("figures/round_event_study.png", ["figures/round_event_study.png"]),
    ("figures/fund_marks_dispersion.png", ["figures/fund_marks_dispersion.png"]),
    ("figures/ipo_validation.png", ["figures/ipo_validation.png"]),
]

# The in-text "(`figures/x.png`)" pointers are rewritten to "(Figure N)". N is DERIVED from
# the order the floats are actually injected, not written down here: this map used to be a
# hand-maintained constant, and reordering the manuscript silently renumbered every float
# while leaving all nine pointers pointing at whatever used to be there. `inject_figures`
# now returns the map it just produced, so the two cannot disagree.

UNICHAR = {
    "−": r"\ensuremath{-}",       # minus
    "→": r"\ensuremath{\rightarrow}",
    "×": r"\ensuremath{\times}",
    "≥": r"\ensuremath{\geq}",
    "≤": r"\ensuremath{\leq}",
    "Σ": r"\ensuremath{\Sigma}",
    "⇒": r"\ensuremath{\Rightarrow}",
    "∈": r"\ensuremath{\in}",
    "ρ": r"\ensuremath{\rho}",
    "σ": r"\ensuremath{\sigma}",
    "≈": r"\ensuremath{\approx}",
    # Superscripts. TeX Gyre Termes has some of these and not others, and the ones it lacks
    # are dropped silently: `1×10⁻⁵` set out of the font renders as `1×10⁻`, which is a
    # different number in a table of p-values. Every superscript the draft uses is mapped
    # here, and `_unrenderable` below fails the build on any that is not.
    "⁰": r"\textsuperscript{0}", "¹": r"\textsuperscript{1}",
    "²": r"\textsuperscript{2}", "³": r"\textsuperscript{3}",
    "⁴": r"\textsuperscript{4}", "⁵": r"\textsuperscript{5}",
    "⁶": r"\textsuperscript{6}", "⁷": r"\textsuperscript{7}",
    "⁸": r"\textsuperscript{8}", "⁹": r"\textsuperscript{9}",
    "⁻": r"\textsuperscript{\ensuremath{-}}",
    "±": r"\ensuremath{\pm}",
    "·": r"\ensuremath{\cdot}",
    "η": r"\ensuremath{\eta}",
}

# Characters the body may carry without a UNICHAR entry: ASCII, the punctuation and accented
# letters the serif font has, and the currency and dash marks used throughout.
_SAFE = set(" \t\n" + "".join(chr(c) for c in range(0x20, 0x7F))) | set(
    "—–‘’“”…§†‡°£€¥×′″áàâäãåçéèêëíìîïñóòôöõúùûüýÿæœøÁÀÂÄÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝÆŒØß")


def _unrenderable(body: str) -> list[str]:
    """Every character the PDF cannot be trusted to set, with its first line.

    xelatex reports a missing glyph as a warning and carries on, so the failure reaches the
    PDF as a silently shortened number. This turns it into a build error before pandoc runs.
    """
    bad = {}
    for i, line in enumerate(body.split("\n"), 1):
        for ch in line:
            if ch in _SAFE or ch in UNICHAR or ch in bad:
                continue
            bad[ch] = f"U+{ord(ch):04X} {ch!r} first at draft line {i}: {line.strip()[:70]}"
    return list(bad.values())


def yaml_block(key: str, text: str) -> str:
    """Render a one-paragraph value as a YAML literal block scalar (no quoting
    headaches: colons, %, $, apostrophes are all literal inside '|')."""
    body = "\n".join("  " + ln for ln in text.split("\n"))
    return f"{key}: |\n{body}\n"


def parse_draft(md: str) -> dict:
    lines = md.split("\n")
    title = next(l[2:].strip() for l in lines if l.startswith("# ") and not l.startswith("## "))

    # abstract: paragraph(s) between '## Abstract' and the next '## '
    i = next(idx for idx, l in enumerate(lines) if l.strip() == "## Abstract")
    j = next(idx for idx in range(i + 1, len(lines)) if lines[idx].startswith("## "))
    abstract = "\n".join(lines[i + 1:j]).strip()

    # repro blockquote (single line starting '> Reproducible')
    repro = next((l for l in lines if l.startswith("> ")), "").strip()

    # body from '## 1. Introduction' onward
    k = next(idx for idx, l in enumerate(lines) if re.match(r"## 1\.", l))
    body = "\n".join(lines[k:]).strip()
    return {"title": title, "abstract": abstract, "repro": repro, "body": body}


def inject_figures(body: str) -> tuple[str, dict[str, str]]:
    """Inject each figure after the paragraph that cites it, and return the pointer map.

    LaTeX numbers floats in document order, so the pointer text has to be read off the order
    the injection actually happened in — which changes whenever the manuscript is reordered.
    Returning the map instead of consulting a written-down one is what keeps "(Figure 4)"
    pointing at the figure the sentence is about.
    """
    blocks = body.split("\n\n")
    out: list[str] = []
    placed: set[str] = set()
    order: list[tuple[str, list[int]]] = []     # (trigger, latex numbers of its group)
    n = 0
    for blk in blocks:
        out.append(blk)
        for trigger, group in FIG_GROUPS:
            if trigger in blk and trigger not in placed:
                nums = []
                for path in group:
                    cap, width = FIG_DEFS[path]
                    out.append(f"![{cap}]({path}){{width={width}}}")
                    placed.add(path)
                    n += 1
                    nums.append(n)
                order.append((trigger, nums))
    missing = [p for p in FIG_DEFS if p not in placed]
    if missing:
        raise SystemExit(f"ERROR: figure(s) never injected (trigger not found?): {missing}")
    rewrites = {}
    for trigger, nums in order:
        label = (f"(Figure {nums[0]})" if len(nums) == 1
                 else f"(Figures {nums[0]}–{nums[-1]})")
        rewrites[f"(`{trigger}`)"] = label
    return "\n\n".join(out), rewrites


# A table short enough to fit on one page should never be split across two. Pandoc renders
# pipe tables as longtable, which breaks wherever the page runs out — Table 11 came out with
# a single data row stranded at the foot of one page and the repeated header at the top of
# the next. \needspace asks for the whole block up front, so a short table that does not fit
# moves down intact. Long tables (Table 1 runs 28 rows) have to break and are left alone.
SHORT_TABLE_MAX_ROWS = 12
CHARS_PER_LINE = 105        # roughly what one typeset table line holds at this width
MAX_RESERVABLE_LINES = 34   # beyond this the table cannot fit a page, so let it break
MIN_TABLE_LEAD = 9          # caption, header rule and two rows: what a break may not split


def keep_short_tables_whole(body: str) -> str:
    """Prefix each short markdown table, and its caption paragraph, with a \\needspace."""
    out, lines = [], body.split("\n")
    i = 0
    while i < len(lines):
        # a pipe table starts at a header row followed by the | --- | separator
        if (lines[i].startswith("|") and i + 1 < len(lines)
                and set(lines[i + 1].replace("|", "").replace(" ", "")) <= {"-", ":"}
                and lines[i + 1].startswith("|")):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            block = lines[i:j]
            rows = j - i - 2                      # body rows, excluding header and rule
            # Height is not the row count: Table 8's eleven rows carry sentences that wrap to
            # three lines each, so asking for eleven baselines reserved a third of what it
            # needed and it broke anyway. Estimate from the text a row actually holds.
            height = sum(max(1, -(-len(r) // CHARS_PER_LINE)) for r in block)
            # A table too tall to reserve whole still must not shed its caption or its first
            # row. Table E.1 shipped with its caption at the foot of one page and its fifteen
            # rows on the next, and Table D.1 stranded a single row of its ten. A longtable
            # may break — that is what it is for — but the first break may not fall inside the
            # caption-header-first-row group, so a long table gets a floor rather than nothing.
            need = height + 4 if (rows <= SHORT_TABLE_MAX_ROWS
                                  and height <= MAX_RESERVABLE_LINES) else MIN_TABLE_LEAD
            # Reach back over the blank line and the bold caption paragraph so the caption
            # travels with its table; a caption alone at a page foot is the same defect.
            k = len(out)
            if k >= 2 and out[k - 1] == "" and out[k - 2].startswith("**Table"):
                k -= 2
            out.insert(k, f"\\needspace{{{need}\\baselineskip}}")
            out.insert(k + 1, "")
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def build_markdown(d: dict) -> str:
    yaml = ["---",
            yaml_block("title", d["title"]).rstrip(),
            # The hash is printed on the title page as well as stamped into the PDF metadata.
            # Metadata survives copying and `pdftotext` but not a third-party re-save or a
            # printout; on the page it survives both, and a referee can check the artifact
            # against the repository by eye. Hashed from the file rather than from `d`, which
            # holds the manuscript already split into title, abstract and body.
            f'author: "Max Gorbuk\\\\thanks{{{AUTHOR_THANKS} '
            f'Manuscript fingerprint: {draft_fingerprint(DRAFT.read_text(encoding="utf-8"))}.}}"',
            f'date: "{DATE_LINE}"',
            # The replication note rides inside the abstract block. As body text it landed
            # after pandoc's \tableofcontents (which follows \maketitle immediately) and
            # took a page of its own; three lines on an otherwise blank page is what a
            # reader sees first. Here it closes the title page, where it belongs.
            yaml_block("abstract", d["abstract"] + ("\n\n" + d["repro"].lstrip("> ")
                                                    if d["repro"] else "")).rstrip(),
            "---", ""]
    body, pointer_rewrites = inject_figures(d["body"])
    for old, new in pointer_rewrites.items():
        if old not in body:
            raise SystemExit(f"ERROR: in-text pointer not found, numbering would drift: {old}")
        body = body.replace(old, new)
    # Final-paper layout: the title page (title, author, abstract, keywords, JEL and the
    # reproducibility note) stands alone; a \newpage starts the body on a fresh page, and the
    # bibliography also opens on its own page — the standard journal/working-paper convention.
    body = body.replace("## Appendix A", "\\newpage\n\n## Appendix A", 1)
    body = body.replace("## References", "\\newpage\n\n## References", 1)
    body = keep_short_tables_whole(body)
    if bad := _unrenderable(body + "\n" + d["title"] + "\n" + d["abstract"]):
        raise SystemExit("ERROR: character(s) with no PDF mapping:\n  " + "\n  ".join(bad))
    parts = ["\n".join(yaml)]
    parts.append(body)
    return "\n\n".join(parts) + "\n"


def header_tex() -> str:
    maps = "\n".join(f"\\newunicodechar{{{ch}}}{{{cmd}}}" for ch, cmd in UNICHAR.items())
    return ("% auto-generated by src/build_pdf.py -- do not edit by hand\n"
            "\\usepackage{newunicodechar}\n" + maps + "\n"
            "\\usepackage{booktabs}\n"
            "\\usepackage{needspace}\n"
            # Prevent long inline code (file paths) from overrunning the right margin:
            # \sloppy makes LaTeX prefer breaking the line (pushing an unbreakable \texttt
            # token to the next line) over an overfull box; a generous \emergencystretch and
            # \Urlmuskip help borderline lines. (seqsplit/hyphenat were rejected: the former
            # errors on pandoc's escaped underscores, the latter inserts misleading hyphens.)
            "\\setlength{\\emergencystretch}{3em}\n"
            "\\sloppy\n"  # avoid overfull table boxes
            # The repository URL on the title page broke inside a word, and the first fix made
            # it worse by believing a package description instead of testing it. `xurl` does
            # not restrict breaks to a URL's own punctuation — it ADDS every alphanumeric
            # character as a break point, which is the whole purpose of the package. Loading
            # it is what produced "unicorn-valu / ation-disagreement" in the shipped PDF.
            #
            # Deleting that `\usepackage{xurl}` did not fix it, and the rebuild said so:
            # pandoc's own template loads xurl whenever the file is present, so the paper had
            # it either way. Header-includes land after the template's packages, which is what
            # makes the override below arrive in time.
            #
            # Three candidates were set in a 3.2in column and read back with pdftotext rather
            # than reasoned about. Leaving xurl alone breaks "disagreemen / t". Restricting it
            # by hand to `\UrlBreaks{\do\/\do\-}` is worse than the disease: the address sets
            # as "https : / / github.com / mkzung / unicorn - valuation disagreement", with
            # gaps at every mark and one hyphen gone. Emptying `\UrlBreaks` removes the break
            # points xurl added and leaves the url package's own, and the address either fits
            # or moves whole to the next line. That is what ships.
            # `\AtBeginDocument` and not a bare definition, and the rebuild is what settled
            # that too. pandoc puts header-includes at line 104 of the generated preamble and
            # its own `\IfFileExists{xurl.sty}{\usepackage{xurl}}` at line 114, so a straight
            # `\def` here is overwritten ten lines later by the package it is meant to undo.
            # Deferring to \begin{document} puts it after every package in the preamble.
            # And `\Urlmuskip` with it. Emptying `\UrlBreaks` alone stopped the mid-word break
            # and replaced it with a worse page: "https : //github.com/mkzung/unicorn
            # valuation- disagreement", gaps at every mark and a hyphen adrift. xurl sets a
            # stretchable muskip at every break point as well as adding the break points, and
            # with `\sloppy` free to stretch the line, the glue that survived is what opened
            # those gaps. Both halves of the package have to be undone, not one.
            "\\AtBeginDocument{\\def\\UrlBreaks{}\\Urlmuskip=0mu plus 0mu\\relax}\n"
            # A single line of a paragraph alone at the top or foot of a page is the one
            # typesetting fault a reader notices without looking for it. LaTeX's defaults
            # (150 and 150) are advisory; a journal sets them to infinity and pays for it
            # in slightly looser pages, which is the right trade in a paper this long.
            "\\widowpenalty=10000\n\\clubpenalty=10000\n\\displaywidowpenalty=10000\n"
            "\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n"
            # pandoc 3.9 wraps pdfkeywords in \xmpquote, which lives in hyperxmp; tectonic's
            # bundle does not carry that package, so passing `-V keywords=` (the manuscript
            # fingerprint) turned every build into "Undefined control sequence" at the
            # \hypersetup block. Header-includes land before \hypersetup in pandoc's template,
            # which is why defining it here is in time. Identity is the right definition: the
            # macro only escapes XMP metadata characters, and the fingerprint is hex.
            "\\providecommand{\\xmpquote}[1]{#1}\n"
            # The contents and the first page of §1 shared a page, so the introduction began
            # halfway down under a list of section numbers. pandoc emits \tableofcontents from
            # its template with nothing after it, so the page break is attached here.
            #
            # The break in front is the same fault at the other end, and it was still there:
            # the contents began under the title page's replication note and the ten body
            # sections filled what was left, so the eleventh and the seven appendices went
            # over the fold and page two came out four fifths white. Two pages either way,
            # but one of them is a title page and a contents page rather than two of neither.
            "\\let\\oldtableofcontents\\tableofcontents\n"
            "\\renewcommand{\\tableofcontents}{\\clearpage\\oldtableofcontents\\clearpage}\n")


def draft_fingerprint(md: str) -> str:
    """The manuscript's content hash, stamped into the PDF so staleness is checkable.

    The first version of the staleness check compared mtimes, and mtime is a proxy for the
    wrong thing: it asks whether the build happened after the edit, not whether the artifact
    matches the text. Git does not store mtimes, so after a plain `git clone` the order is
    arbitrary and a reviewer running `pytest` on an untouched tree gets a red suite telling
    him to rebuild a PDF that is already correct. Content answers the question mtime only
    gestures at.
    """
    return hashlib.sha256(md.encode("utf-8")).hexdigest()[:16]


def pdf_fingerprint(pdf: Path) -> str | None:
    """The hash this PDF was built from, or None if it predates the stamp."""
    if not shutil.which("pdfinfo"):
        return None
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=False).stdout
    m = re.search(r"draft-sha256:([0-9a-f]{16})", out)
    return m.group(1) if m else None


def _weights_missing(pdf: Path) -> list[str]:
    """Weights the finished PDF does not embed. Empty is the healthy answer.

    A missing glyph at least produces a warning. A font family whose bold the engine cannot
    resolve produces nothing at all: `\\textbf` sets in the regular face, the build reports
    success, and a reader has to notice that a 79-page paper has no emphasis anywhere. That
    happened here, so the finished file is inspected rather than the intent trusted.

    `pdffonts` ships with poppler and is not guaranteed present; without it this returns
    nothing rather than blocking a build it cannot check, and says so.
    """
    if not shutil.which("pdffonts"):
        print("NOTE: pdffonts not found (poppler); skipping the embedded-weight check.",
              file=sys.stderr)
        return []
    out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=False).stdout.lower()
    missing = []
    if "bold" not in out:
        missing.append("bold")
    if "italic" not in out and "oblique" not in out:
        missing.append("italic")
    return missing


def main() -> int:
    md = DRAFT.read_text(encoding="utf-8")
    d = parse_draft(md)
    BUILD_MD.write_text(build_markdown(d), encoding="utf-8")
    HEADER_TEX.write_text(header_tex(), encoding="utf-8")
    print(f"wrote {BUILD_MD.relative_to(REPO)} and {HEADER_TEX.relative_to(REPO)}")

    engine = next((e for e in ("xelatex", "tectonic", "lualatex") if shutil.which(e)), "xelatex")
    if engine != "xelatex":
        print(f"NOTE: xelatex not found; building with {engine}. The README names XeLaTeX, "
              f"and the two do not resolve font families identically — see the bold check "
              f"below, which exists because of exactly this.", file=sys.stderr)
    # TeX Gyre Termes first, and that order is load-bearing rather than taste. This list had
    # STIX Two Text at the front; on a machine with STIX installed and Termes absent, the
    # whole 79-page paper came out set in STIX with NO BOLD FACE EMBEDDED AT ALL — every
    # table label, run-in label and heading rendered at regular weight — and the build
    # printed OK. Termes is what the reviewed PDF was set in and it resolves cleanly, so it
    # leads; the rest are fallbacks for machines without it.
    #
    # Neither question fontconfig can answer decides this. "Is the family installed" is what
    # failed the first time. "Does the family list a bold style" fails too, and on the same
    # font: macOS ships STIX Two Text as one variable file, so `fc-list :family=STIX Two Text
    # style` reports Bold, Medium and SemiBold named instances that XeTeX cannot instantiate
    # from a .ttf it loads as a static face. Only the artifact settles it, so the build tries
    # a family, reads the finished PDF, and moves to the next one if the weights are absent.
    candidates = ["TeX Gyre Termes", "STIX Two Text", "Tinos", "Charter", None]
    tried: list[str] = []
    for serif in candidates:
        print(f"serif mainfont: {serif or '(engine default — Latin Modern)'}")
        cmd = [
            "pandoc", str(BUILD_MD),
            "-f", "markdown-tex_math_dollars-tex_math_single_backslash",
            f"--pdf-engine={engine}",
            "-V", "documentclass=article",
            "-V", "geometry:margin=1in",
            "-V", "fontsize=11pt",
            "-V", "linestretch=1.08",
            *(["-V", f"mainfont={serif}"] if serif else []),
            # The manuscript hash travels inside the artifact, so `git clone && pytest` can
            # ask whether this PDF was built from this text without consulting a clock.
            "-V", f"keywords=draft-sha256:{draft_fingerprint(md)}",
            "-V", "colorlinks=true", "-V", "linkcolor=black", "-V", "urlcolor=Blue",
            # Sixty-four pages, twelve sections and five appendices: without a contents page a
            # reader who wants §11 has to guess, and the appendices, where every robustness
            # answer now lives, are invisible from the front. `--toc` is deliberately NOT passed:
            # pandoc emits \tableofcontents straight after \maketitle, which puts it ahead of
            # the replication note and orphans the note onto the contents page. The note carries
            # its own \tableofcontents instead, so the order is title, note, contents, body.
            "--toc", "--toc-depth=2",
            "-H", str(HEADER_TEX),
            "--resource-path", str(REPO),
            "-o", str(OUT_PDF),
        ]
        print("running:", " ".join(cmd))
        try:
            r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, check=False)
        except FileNotFoundError:
            print("pandoc not found; wrote _build.md so the PDF can be built elsewhere.",
                  file=sys.stderr)
            return 2
        if r.returncode != 0:
            # A family the engine cannot load at all is the same kind of failure as a family
            # whose bold it cannot resolve; both mean "try the next one".
            sys.stderr.write(r.stdout + "\n" + r.stderr + "\n")
            if serif is not None:
                tried.append(f"{serif} (engine refused it)")
                continue
            print("PANDOC FAILED", file=sys.stderr)
            return r.returncode
        if r.stderr.strip():
            print("pandoc warnings:\n" + r.stderr.strip())
        if bad := _weights_missing(OUT_PDF):
            tried.append(f"{serif or 'engine default'} (no {' and no '.join(bad)} face)")
            if serif is not None:
                print(f"NOTE: {tried[-1]}; rebuilding with the next serif.", file=sys.stderr)
                continue
            print(f"ERROR: the PDF embeds no {' and no '.join(bad)} face, and every candidate "
                  f"failed the same way: {'; '.join(tried)}. Every table label, run-in label "
                  f"and heading is set at regular weight. Install TeX Gyre Termes (TeX Live: "
                  f"tex-gyre) or build with xelatex.", file=sys.stderr)
            return 3
        if tried:
            print("passed over: " + "; ".join(tried))
        print(f"OK -> {OUT_PDF.relative_to(REPO)} ({OUT_PDF.stat().st_size//1024} KB)")
        return 0
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
