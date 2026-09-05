"""
Prose-drift guard (v0.16).

`tests/test_metrics.py` pins each metric against the production loaders but never
reads the manuscript, so it cannot catch the failure mode that has bitten this
project twice — a number left STALE in the prose after the code moved (the v0.11
README n=9 robustness block; the v0.12 stale result-#7 numbers, both caught only by
manual inspection). These tests close that gap: every headline figure quoted in
`paper/draft.md` / `README.md` is registered in `src/paper_numbers.py`, recomputed
live from the code, and required to (a) match the value the paper states and
(b) actually appear in the prose. A drift in either direction now fails CI.

The registry intentionally reuses the production functions, so these tests also
re-exercise the whole offline pipeline (cross-section, IPO, cross-fund, time series,
Forge overlay, prediction markets, robustness) on every run.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import paper_numbers as pn


def test_registry_is_populated_and_well_formed():
    """The canonical registry covers every results section with sane records."""
    nums = pn.canonical_numbers()
    assert len(nums) >= 30                                   # all four signals + robustness
    sections = {n.section for n in nums}
    # Section labels are the paper's live numbering now (see SECTION_ALIASES): the registry
    # used to be filed under the pre-reframe numbers, so a failure message named a section the
    # manuscript did not have. The legs cut to a second paper took their entries with them.
    assert {"2.3", "3.1", "4.3", "5.1", "8", "9", "G", "B", "C.3"} <= sections
    # The set of checkable files is the registry's own, not a copy of it: a copy went stale
    # the moment figure captions became checkable, and failed a green registry for saying so.
    # A misspelled key still fails here, because it will not be in the map either.
    for n in nums:
        assert n.tol >= 0
        assert set(n.in_files) <= set(pn._FILE), f"{n.label} targets an unknown file"
        assert set(n.context) <= set(pn._FILE), f"{n.label} has context for an unknown file"
        if n.claim is None:                                  # numeric-only rows assert no prose
            assert n.in_files == ()


def test_no_code_drift():
    """Every quoted number still reproduces from the production code (|computed-paper|<=tol)."""
    nums = pn.canonical_numbers()
    drift = [f"§{n.section} '{n.claim or n.label}': code={n.computed:.4f} "
             f"paper={n.value:.4f} (tol {n.tol:g})" for n in nums if not n.code_ok]
    assert not drift, "CODE drift — the loaders no longer produce the quoted value:\n" + "\n".join(drift)


def test_no_prose_drift():
    """Every quoted number is actually present in the manuscript file(s) that state it.
    This is the guard test_metrics.py cannot provide — it reads the prose. Bare-token
    presence catches a number's TOTAL disappearance; per-file `context` phrases (on the
    common percentages where bare presence is loose) catch PARTIAL drift — one stale
    mention among several."""
    nums = pn.canonical_numbers()
    missing = []
    for n in nums:
        for problem in pn.prose_missing(n):
            missing.append(f"§{n.section} ({n.label}): {problem}")
    assert not missing, "PROSE drift — quoted figure missing from the manuscript:\n" + "\n".join(missing)


def test_common_percentages_have_context_guards():
    """The percentages too common for bare-substring presence (24%, 11%, 48%, 39%, 88%) must
    carry a per-file context phrase, so partial drift on a multiply-stated number is caught."""
    nums = {n.label: n for n in pn.canonical_numbers()}
    for label in ["median cross-fund spread %", "median |fund-mark error| %",
                  "median |headline error| %", "Anthropic cross-fund spread %",
                  "share of family-cells bit-identical (%)"]:
        assert nums[label].context, f"{label} needs a context guard"
        assert set(nums[label].context) == {"draft", "readme"}


# Quantities the prose states MORE THAN ONCE. Bare-token presence passes as long as the value
# exists SOMEWHERE, so a second, stale restatement slips through — the exact robustness-appendix failure
# (a leftover n=13 "p=0.023" beside the registry-pinned n=17 "p=0.012", caught by hand
# 2026-07-02). Here every match of the labelled pattern must be in the allowed set, so a stale
# twin fails CI wherever it hides. Patterns are draft-literal: en-dash in "Mann–Whitney",
# Unicode minus normalised by pn._norm, optional ** bolding.
UNIQUE_QUANTITIES = [
    # Test statistics (U/H/W) appear at FIRST mention only, so the p-value patterns carry an
    # optional statistic group.
    # This entry was dead for three rounds and nobody saw it, because the file it lives in is
    # the slow one and kept getting skipped. It watched "same private share by a median of
    # 24%", a sentence the reframe deleted; the pattern then matched nothing and the test
    # reported exactly that, to an empty room. Two live restatements replace it: the
    # house-level median, which the abstract and the conclusion both carry, and the ten-name
    # cross-fund median, which §4.3 and §5.1 both carry.
    ("house-level median spread (abstract + conclusion)",
     r"(?:Measured between houses it is|same private share a median of) \*{0,2}(\d+\.\d)%",
     {"12.1"}),
    ("ten-name cross-fund median (§4.3 + §5.1)",
     r"(?:has a median of|ten-company median of) \*{0,2}(\d+)% (?:across the ten|is not)", {"24"}),
    # The lookbehind matters: without it the pattern reads the last three digits of
    # "309,654 Level-3 private marks" as a fourth value of this quantity and fails on the
    # population count. A three-digit quantity needs its left edge asserted.
    ("clean Level-3 mark count (Appendix A)",
     r"(?<![\d,])(\d{3}) (?:raw )?(?:→ )?(?:clean )?Level-3", {"386", "409"}),
    # Appendix B defers to §6.2 by quoting its cell count, and that restatement went stale for
    # two rounds: it read 782 while the section itself had been recomputed twice. The registry
    # pins the figure inside §6.2 and cannot see a paraphrase in another section, which is what
    # this list is for. Any quantity the prose states twice belongs here, not in a presence
    # check. (The section numbers moved when the manuscript was rebuilt; the pattern moved with
    # them, which is the only kind of edit this list may take.)
    # §8.6 restates two of Table 8's own rows in the sentence under it, and the tie tolerance
    # moved one of them from 14 / 37 to 13 / 34 while the sentence kept the old pair. The
    # registry pins the table row and cannot see a paraphrase two lines below it.
    ("placebo counts restated under Table 8",
     r"a sign count on the wrong side of a coin, (\d+ of \d+, \d+ of \d+ and \d+ of \d+)",
     {"14 of 31, 17 of 41 and 13 of 31"}),
    ("stood-pat cell count (Appendix B cross-reference + §6.2)",
     r"§6\.2 answers (?:it|the question) on (?:the )?([\d,]+) such cells", {"760"}),
]


def test_quantity_uniqueness_no_stale_restatement():
    """Every occurrence of a multiply-stated quantity must carry its one current value —
    the guard class the presence-checks cannot provide (see UNIQUE_QUANTITIES note)."""
    draft = pn._norm((ROOT / "paper" / "draft.md").read_text(encoding="utf-8"))
    problems = []
    for label, pat, allowed in UNIQUE_QUANTITIES:
        found = set(re.findall(pat, draft))
        if not found:
            problems.append(f"{label}: pattern no longer matches the draft at all")
        elif not found <= allowed:
            problems.append(f"{label}: prose states {sorted(found)} — allowed {sorted(allowed)} "
                            "(stale restatement?)")
    assert not problems, "STALE-RESTATEMENT drift:\n" + "\n".join(problems)


def test_minus_sign_normalisation():
    """The prose uses the Unicode minus (U+2212); the guard must match an ASCII claim to it,
    otherwise every negative number (drawdowns, discounts) would false-fail."""
    assert pn._norm("−62%") == "-62%"                        # U+2212 -> ASCII hyphen
    # -62% went with the cycle appendix; -4.6% with the secondary leg. −1.08 is the
    # event-study step and is set with a real U+2212 in the manuscript.
    assert pn.appears_in("-1.08", "draft")                   # ASCII claim finds the U+2212 prose
    assert not pn.appears_in("-62.999% nonexistent token", "draft")


def test_gornall_strebulaev_reconciliation_present():
    """Appendix C.1 reconciles the secondary-at-par result with the 48% anchor finding. It carries no
    new *computed* number (so it is not in the registry), but it is load-bearing prose a future
    edit could silently drop — guard its key claims directly in the manuscript."""
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    assert "### C.1 Reconciling with Gornall" in draft         # the subsection exists
    # the two load-bearing claims: different objects (no contradiction) + same cross-sectional sign
    assert "option-adjusted fair value of the cap table" in draft
    # C.1 was rebuilt when the secondary leg was cut: the puzzle it used to resolve
    # ("why does the secondary price near par?") no longer exists in this paper, so
    # the guarded claims are the two that survive — different objects, same
    # cross-section — plus the explicit refusal to re-derive the anchor number.
    assert "One measures a level against a model. The other measures dispersion" in draft
    assert "locate the headline's untrustworthiness in the same companies" in draft
    assert "reconciliation, not a re-derivation" in draft
    # the G-S anchor figures it leans on (G-S's own, not our computed numbers)
    for tok in ["56% overvalued", "65 of 135"]:
        assert tok in draft, f"missing G-S anchor figure '{tok}'"
    # the increment must also surface in the README result list and the abstract clause (vi)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Reconciliation with the anchor paper" in readme
    assert "The objects differ" in draft   # the Appendix C.1 reconciliation argument is present


def test_scatter_labels_have_a_fixed_iteration_budget():
    """figures/headline_vs_forge.png is the only figure whose layout is solved iteratively.
    adjustText defaults to a one-second wall-clock budget, which made the rendered labels —
    and therefore the committed PNG — depend on how fast the machine happened to be. An
    explicit iter_lim replaces the clock with a fixed number of steps. This checks the call
    still carries one; it does not re-render, so it is a regression guard, not a proof."""
    src = (ROOT / "src" / "analyze.py").read_text(encoding="utf-8")
    call = src[src.index("adjust_text("):]
    call = call[:call.index(")\n")]
    assert "iter_lim=" in call, "adjust_text would fall back to its wall-clock time limit"


def test_harvest_lower_bound_disclosed():
    """The N-PORT harvest is capped per company, so §4.3's spreads are lower bounds. Two
    shipped files disagree about Fanatics on 2026-04-30 for exactly that reason, and a
    referee reading the replication package will find both. Assert the data really do
    still disagree (so this test can fail), and that the prose reconciling them survives."""
    import csv
    disp = {r["company"]: r for r in
            csv.DictReader(open(ROOT / "data" / "fund_marks_dispersion.csv"))}
    assert disp["Fanatics"]["n_families"] == "1"        # capped harvest: one family, no spread
    probe = [r for r in csv.DictReader(open(ROOT / "data" / "nport_expansion_probe.csv"))
             if r["company"] == "Fanatics" and r["report_date"] == "2026-04-30"]
    assert len({r["fund"] for r in probe}) == 7         # deeper sweep: seven funds
    assert len({r["registrant"] for r in probe}) == 3   # across three families

    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    assert "eighteen filings" in draft                          # the cap is stated
    assert "lower bound on what a complete sweep" in draft      # and what it implies
    dd = (ROOT / "notes" / "data_dictionary.md").read_text(encoding="utf-8")
    assert "nport_expansion_probe.csv" in dd                    # the probe is documented
    assert "0.0% spread" in dd                                  # against the row it contradicts


def test_readme_lists_the_stages_the_pipeline_actually_runs():
    """The README names every offline stage. Adding a stage and forgetting the sentence
    leaves a reader following a list that is missing steps, which is how the list came to
    be two stages short."""
    import re
    scripts = re.findall(r'\("src/(\w+)\.py"', (ROOT / "src" / "reproduce.py").read_text())
    listed = re.search(r"runs every offline stage in order \(([^)]*)\)",
                       (ROOT / "README.md").read_text())
    assert listed, "the README sentence naming the stages has moved or been reworded"
    named = {x.strip().strip("`") for x in listed.group(1).split(",")}
    assert set(scripts) == named, f"README/pipeline mismatch: {set(scripts) ^ named}"


def test_manifest_matches_live_registry():
    """If the committed manifest exists it must be current (regenerated by src/reproduce.py)."""
    man = ROOT / "notes" / "reproduction_manifest.md"
    if not man.exists():
        return
    text = man.read_text(encoding="utf-8")
    nums = pn.canonical_numbers()
    assert f"{len(nums)} canonical numbers" in text          # count in sync
    assert "0 code-drift, 0 prose-drift" in text             # last reproduce.py run was clean


def test_no_two_entries_compute_the_same_number_differently():
    """One computable quantity, one registry entry — enforced where it can be enforced.

    The failure this exists for: the share of multi-fund house groups filing one identical
    price was registered twice, once inline in §5.4 and once from `population.house_policy`
    in §5.10. Both recomputed the same expression to 89.0119%, and the two entries claimed
    89.0 (tol 0.2) and 88.8 (tol 0.3). The bands straddle the truth from opposite sides, so
    both passed for four rounds while three places in the shipped text printed 88.8%, two
    tenths of a point stale. A registry whose whole purpose is to make a stale number fail
    had absorbed one because the number had two owners.

    The rule is narrow enough to have no judgement in it: if two entries compute the same
    value, they must claim the same value. Exceptions are named below rather than inferred
    from a precision heuristic, and each one is checked for still being live, so an exemption
    cannot outlive the pair it exempts.
    """
    from collections import defaultdict
    # Places where the paper states one quantity twice at two precisions ON PURPOSE: once
    # rounded, in a sentence, and once exact, where it is the subject. A rule that tried to
    # infer this from decimal places would have to guess, so it is written down.
    allowed = [
        frozenset({"median |fund-mark error| %",
                   "the mark median IS ServiceTitan's own error (%)"}),
        frozenset({"median |headline error| %",
                   "the headline median IS Figma's own error (%)"}),
        frozenset({"median spread, one-series panel (%)", "old bound: median (%)"}),
        # Not a rounding pair but a measured coincidence, and the paper now says so. The
        # ten-name median across FUNDS and the same ten cells scored across HOUSE MEDIANS come
        # out identical, because on all ten names the widest and the narrowest fund sit in
        # different houses. §4.3 states it rounded, at 24%; §5.1 states it exact, at 23.7%,
        # and explains why the two scorings coincide. They were 24% and 12.6% until the
        # ten-name panel stopped pooling seven named managers into one "Other" unit.
        frozenset({"median cross-fund spread %",
                   "ten §4.3 cells scored between houses (%)"}),
        # The panel median, 12.134572143. The body says 12.1% because a sentence carrying
        # three decimals reads as false precision on a median of 4,271 cells; Table C.1 prints
        # 12.13% because the column beside it prints 16.42%, 15.34% and 12.90% and a column
        # that changes precision row to row is worse than one that carries a digit too many.
        # Both entries exist because a claim is a literal token: "12.1%" pins nothing about a
        # cell that reads 12.13%, which is how two cells of that table went stale unnoticed.
        frozenset({"population median spread (%)",
                   "panel median, at Table C.1's two decimals (%)"}),
    ]
    by_computed = defaultdict(list)
    for n in pn.canonical_numbers():
        by_computed[round(float(n.computed), 9)].append(n)
    bad, used = [], set()
    for computed, group in sorted(by_computed.items()):
        if len({round(float(n.value), 9) for n in group}) == 1:
            continue
        labels = frozenset(n.label for n in group)
        hit = next((a for a in allowed if a <= labels), None)
        if hit is not None:
            used.add(hit)
            continue
        bad.append(f"computed {computed} is claimed as "
                   f"{sorted({round(float(n.value), 9) for n in group})}:\n    "
                   + "\n    ".join(f"§{n.section} {n.label}" for n in group))
    assert not bad, ("one expression, two claims:\n  " + "\n  ".join(bad))
    dead = [sorted(a) for a in allowed if a not in used]
    assert not dead, ("exemption(s) for a pair that no longer collides — delete them:\n  "
                      + "\n  ".join(map(str, dead)))


def test_the_offline_pipeline_stays_offline():
    """README: "the offline pipeline needs no network". A script that calls out to SEC
    turns a clean reproduction into a five-minute failure on any machine without a
    connection, and `family_forecast.py` was added to the list on the mistaken reasoning
    that producing a committed data file makes a script part of the pipeline. Harvested
    inputs are produced separately by design; only derivations belong here."""
    import re
    src = ROOT / "src"
    listed = re.findall(r'\("src/(\w+)\.py"', (src / "reproduce.py").read_text())
    networked = {p.stem for p in src.glob("*.py")
                 if re.search(r"\burllib\b|\brequests\.", p.read_text())}
    offenders = sorted(set(listed) & networked)
    assert not offenders, f"offline pipeline contains network scripts: {offenders}"

    # The README names the network scripts and counts them. Both drift the moment one is
    # added, which is how it came to claim there were two when there were six.
    readme = (ROOT / "README.md").read_text()
    for name in networked:
        assert f"`src/{name}.py`" in readme, f"README does not mention the harvester {name}.py"
    counted = re.search(r"\b(\w+) scripts reach out to SEC\b", readme)
    assert counted, "the README sentence counting the harvesters has been reworded"
    words = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8,
             "Nine": 9, "Ten": 10}
    assert words.get(counted.group(1).capitalize()) == len(networked), (
        f"README says {counted.group(1)} harvesters, the tree has {len(networked)}")


def test_every_section_cross_reference_resolves_to_a_real_heading():
    """The manuscript points at itself 150-odd times. Inserting section 5 shifted Limitations
    and Conclusion by one, and a single missed "§5" would have sent a referee from the
    coverage caveat to the population panel with no sign anything was wrong. Cross-references
    are cheap to break silently and cheap to check, so check them: every §N.M must name a
    subsection heading that exists, and every §N a top-level one.
    """
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = draft.split("## References")[0]

    tops = set(re.findall(r"^## (\d+)\.", body, re.M))
    # Subsections are `### 5.1 ...` headings since the manuscript was rebuilt; the bold run-in
    # form is still scraped because the appendices carry lifted paragraphs that keep theirs.
    subs = (set(re.findall(r"^\*\*(\d+\.\d+) ", body, re.M))
            | set(re.findall(r"^### (\d+\.\d+) ", body, re.M)))
    assert len(tops) >= 8 and len(subs) >= 25, "the heading scrape has lost its anchor"

    bad = []
    for ref in set(re.findall(r"§(\d+(?:\.\d+)?)", body)):
        known = subs if "." in ref else tops
        if ref not in known:
            bad.append(f"§{ref}")
    assert not bad, (
        f"dangling cross-references {sorted(bad)}; sections present: "
        f"{sorted(tops)} / {sorted(subs)}")


# The finance journals this paper is written for cap the abstract: 100 words at the Journal of
# Finance, 150 at JFE and RFS, 200 at JFQA. It stood at 370 — two and a half times the modal
# limit — because nineteen rounds each added the round's best sentence and none took one out,
# and no guard here measures length.
#
# The ceiling IS the JFE/RFS limit, not a margin below it, so the abstract sits exactly on the
# number a submission has to clear and any sentence added to it has to be paid for by one
# removed. The Journal of Finance's 100 would cost a claim, and which claim to drop is a
# decision about where to submit, not a copy-edit; it is not made here.
ABSTRACT_MAX_WORDS = 150


def _abstract(draft: str | None = None) -> str:
    if draft is None:
        draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    m = re.search(r"^## Abstract\n(.*?)^\*\*Keywords", draft, re.S | re.M)
    assert m, "the abstract no longer sits between its heading and the keywords line"
    return m.group(1).strip()


def test_the_abstract_extractor_reads_the_abstract_and_nothing_else():
    """A word count is only a guard if it counts the right words.

    The failure mode is silent in both directions: an extractor that swallowed the whole
    manuscript would fail on a compliant abstract, and one that matched nothing would pass on
    any abstract at all. Driven on a synthetic front matter so both are shown.
    """
    doc = ("# Title\n\nauthor line\n## Abstract\n\nOne two three four five.\n\nSix seven.\n\n"
           "**Keywords:** a; b.\n\n**JEL classification:** G12.\n\n## 1. Introduction\n\n"
           "This body text must not be counted, and it is long enough to prove it.\n")
    got = _abstract(doc)
    assert len(got.split()) == 7, f"the extractor counted {len(got.split())} words: {got!r}"
    assert "Keywords" not in got and "Introduction" not in got and "author" not in got

    over = doc.replace("Six seven.", " ".join(["word"] * ABSTRACT_MAX_WORDS))
    assert len(_abstract(over).split()) > ABSTRACT_MAX_WORDS, (
        "an abstract over the ceiling does not read as over the ceiling")

    with pytest.raises(AssertionError):
        _abstract("# Title\n\nno abstract heading here at all\n")


def test_the_abstract_stays_inside_a_journal_limit():
    n = len(_abstract().split())
    assert n <= ABSTRACT_MAX_WORDS, (
        f"the abstract is {n} words against a ceiling of {ABSTRACT_MAX_WORDS}. Journals cap "
        f"this at 100-200; cut a clause rather than raising the number.")
    assert n > 80, f"the abstract is {n} words — that is not an abstract, it is a sentence"


def test_the_abstract_still_carries_the_paper_s_four_claims():
    """A ceiling invites cutting the wrong thing. These are what the abstract exists to say."""
    a = _abstract()
    for tok, what in [("309,654", "the population's size"),
                      ("0.004%", "the registrant-level artifact"),
                      ("12.1%", "the house-level median"),
                      ("597", "the tail count that composition cannot explain")]:
        assert tok in a, f"the abstract no longer states {what} ({tok})"


def test_the_roadmap_announces_every_top_level_section():
    """The introduction tells the reader what each section does. A section added without a
    roadmap line is a section the reader has no reason to reach."""
    draft = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    intro = draft.split("## 2.")[0]
    body = draft.split("## References")[0]
    # Every top-level section the manuscript actually has, rather than three written down here:
    # a section added without a roadmap line was the failure this test was built for, and a
    # hard-coded list cannot see one.
    tops = sorted(int(n) for n in set(re.findall(r"^## (\d+)\.", body, re.M)))
    assert len(tops) >= 8, "the section scrape has lost its anchor"
    for n in tops:
        if n == 1:
            continue                       # the introduction does not announce itself
        assert re.search(rf"Section {n}\b", intro), f"the roadmap never mentions Section {n}"
    for n, name in [(5, "how far apart"), (8, "compresses"), (10, "overturn"), (11, "conclu")]:
        assert name in intro.lower(), f"the roadmap does not say what Section {n} contains"


# A retraction is a claim like any other, and prose carries it the way prose carries a
# number: unevenly. When §7.2 stopped defending the sector contrast as specified in advance,
# eight other passages went on asserting it — including one two paragraphs below the
# retraction, in the same section. No numeric guard sees that, because no number moved.
RETRACTED_PHRASES = {
    "pre-specified": "the sector contrast is unregistered; §7.2 and §6 say so",
    "specified in advance": "same retraction — the grouping was never registered as prior",
    "not searched over post hoc": "the specification curve searches over it explicitly",
    "will be filed": "the paper promises no action on the author's behalf",
    "we commit to": "same",
}


def test_no_shipped_document_reasserts_a_retracted_claim():
    """Positions change; sentences do not follow. This pins the ones that already drifted."""
    offenders = []
    for rel in ["paper/draft.md", "README.md", "notes/data_dictionary.md",
                "notes/universe_definition.md"]:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for phrase, why in RETRACTED_PHRASES.items():
            if phrase in text:
                offenders.append(f"{rel} still says {phrase!r} — {why}")
    assert not offenders, "retracted claims are back in the prose:\n  " + "\n  ".join(offenders)


def test_the_banlist_would_actually_fire():
    """The list is worthless if nothing in it can be found. Prove the matcher works."""
    for phrase in RETRACTED_PHRASES:
        assert phrase in f"a sentence containing {phrase} in the middle".lower()


# A registry entry checks that the CURRENT number is present. It cannot see the previous one
# still sitting in the abstract, because presence is not exclusivity — and that is how §5's
# old median survived a rebuild of the whole section in the paragraph a referee reads first.
# Superseded values go here when a headline moves. These were bolded tokens until the
# manuscript was de-bolded to journal norms, and keying a banlist on markup meant the guard
# would have gone quiet the moment the asterisks came off. The bare digits are banned
# instead, which is strictly stronger: every one of them currently appears nowhere in any
# shipped document, so there is no legitimate occurrence to protect.
# token -> (why it is retired, words that must appear near it for the use to be the retired
# one). A bare token is not enough: two of these values came back as legitimate figures for
# entirely different quantities — 12.5% is now Fidelity against T. Rowe on Gusto (§2.3) and
# 40.7% is the letter-mixed cells' share above 24% (Table C.1). Banning the digits outright
# would have forced a true number out of the paper to keep a checker green, which is the
# wrong way round. The context words are what make the ban about the claim.
SUPERSEDED_POPULATION_NUMBERS = {
    "12.5%": ("the population median before claim instruments were excluded",
              ("population median", "median company-date", "median spread between houses")),
    "40.7%": ("share above 24% on the same superseded panel",
              ("of all company-dates exceed", "of cells exceed 24")),
    "$180.3B": ("disagreeing NAV on the same superseded panel", ()),
    "4,606": ("cell count before the exclusion", ()),
    "88.3%": ("within-house identical share before the exclusion", ()),
    "59th percentile": ("where the ten-name median sat before the exclusion", ()),
}


def _retired_use(text: str, token: str, context: tuple) -> bool:
    """True when `token` appears in the sense that was retired.

    With no context words the token is retired outright. With them, the ban fires only where
    one appears within 200 characters — close enough to be the same clause.
    """
    for m in re.finditer(re.escape(token), text):
        if not context:
            return True
        window = text[max(0, m.start() - 200):m.end() + 200].lower()
        if any(c.lower() in window for c in context):
            return True
    return False


def test_no_document_still_quotes_a_superseded_population_number():
    """The guard pins what the paper says; this pins what it must no longer say."""
    offenders = []
    for rel in ["paper/draft.md", "README.md", "notes/data_dictionary.md",
                "notes/universe_definition.md"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for token, (why, ctx) in SUPERSEDED_POPULATION_NUMBERS.items():
            if _retired_use(text, token, ctx):
                offenders.append(f"{rel}: {token} — {why}")
    assert not offenders, "superseded figures still in the prose:\n  " + "\n  ".join(offenders)


def test_the_superseded_list_would_actually_fire():
    """A banlist nobody can trip catches nothing, and one that trips on everything is worse.

    Both directions on the two entries that now carry context: the retired sentence must be
    caught, and the live sentence using the same digits for a different quantity must not.
    """
    for token in SUPERSEDED_POPULATION_NUMBERS:
        assert any(ch.isdigit() for ch in token), token
        assert len(token) >= 5, f"{token} is short enough to collide with something innocent"

    retired = "Measured this way the population median is 12.5% between houses"
    live = ("the widest gap between them, on Gusto, is 12.5% ($19.03 against $21.40 on "
            "31 March 2026)")
    _, ctx = SUPERSEDED_POPULATION_NUMBERS["12.5%"]
    assert _retired_use(retired, "12.5%", ctx), "the matcher would not fire on the old claim"
    assert not _retired_use(live, "12.5%", ctx), "the matcher fires on a legitimate reuse"

    retired40 = "40.7% of all company-dates exceed 24%"
    live40 = "| two or more letters named | — | 1,174 | 94 | 12.68% | 40.7% |"
    _, ctx40 = SUPERSEDED_POPULATION_NUMBERS["40.7%"]
    assert _retired_use(retired40, "40.7%", ctx40)
    assert not _retired_use(live40, "40.7%", ctx40)


def reaches(token: str, haystack: str) -> bool:
    """Does `haystack` state `token` on its own, or merely contain its characters?

    One predicate, two uses: the budget check below asks it of registry strings, and
    `test_every_registered_token_stands_on_its_own` asks it of the manuscript. Pinned by
    `test_a_figure_cannot_hide_inside_another`.

    A digit or a decimal point before the token makes it part of a bigger number; so does a
    digit after it, or a decimal point that has a digit of its own behind it. A FULL STOP does
    not — writing the rule as a blanket `(?!\\.)` flagged fourteen clean tokens whose only sin
    was ending a sentence, which is how a check acquires a reputation for crying wolf.
    """
    import re
    lead, trail = token[0], token[-1]
    pre = (r"(?<![\d.,])" if lead.isdigit() or lead == "."
           else r"(?<![0-9A-Za-z])" if lead.isalnum() else "")
    post = (r"(?!\d)(?!\.\d)" if trail.isdigit() or trail in ".%"
            else r"(?![0-9A-Za-z])" if trail.isalnum() else "")
    return re.search(pre + re.escape(token) + post, haystack) is not None


def test_no_count_in_the_prose_escapes_the_registry():
    """The budget below scans percentages and dollar amounts. A count is neither.

    `test_no_bold_figure_in_section_5_escapes_the_registry` looks for `\\d+%` and `$\\d+B`, so
    "29 events on two or more houses", "228 companies" and "105 of 116 multi-family cells"
    are outside it entirely — a count that goes stale when the panel moves fails nothing at
    all. Every other guard in this file has the same blind spot, which is why this exists.

    A count is read as a number followed by the noun it counts, because that is the shape a
    result takes and it keeps accession numbers, page ranges and ASC 820 out. A first attempt
    scanned bare digits instead and returned sixty-five findings, of which the first dozen
    were fragments of `12,920,570` and a journal page range: an instrument that has to be
    argued with is not a measurement.

    Measured with the predicate this test actually uses: 153 count phrases from §3 onward,
    15 the registry cannot reach. They are worked examples, filing counts quoted to show a
    method hazard, and the intermediate counts of Appendix E's four measurements. Each was
    read once. The budget only goes down.

    It was first set to 16, from a throwaway script whose reachability rule differed from
    `reaches` by one character class, and an injected count then slipped under it — a
    budget one too high absorbs exactly one defect and reports green. Measure the budget
    with the instrument that ships, and prove it fails on one more.
    """
    import re
    body = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    body = body.split("## 2. The microscope", 1)
    assert len(body) == 2, "section 2's heading has been reworded; this check has lost its anchor"
    prose = "\n".join(ln for ln in body[1].split("## References", 1)[0].split("\n")
                      if not ln.startswith("|"))
    reachable = set()
    for n in pn.canonical_numbers():
        if n.claim:
            reachable.add(pn._demark(n.claim))
        for phrase in n.context.values():
            reachable.add(pn._demark(phrase))
    registry = "\n".join(reachable)
    # Words that follow a number without being the thing counted.
    STOP = {"per", "and", "of", "to", "or", "in", "on", "the", "is", "are", "was", "against",
            "basis", "bps", "days", "day", "months", "month", "years", "year", "quarters",
            "quarter", "decimal", "decimals", "further", "more", "other", "such"}
    seen = set()
    for m in re.finditer(r"(?<![\d,.\-])(\d{1,3}(?:,\d{3})+|\d{2,4})\s+([a-z][a-z-]{2,})", prose):
        num, noun = m.group(1), m.group(2)
        if noun in STOP or re.fullmatch(r"(19|20)\d\d", num):
            continue
        seen.add((num, noun))
    assert len(seen) > 100, f"only {len(seen)} count phrases found; the scan has lost its grip"
    loose = sorted({num for num, _ in seen if not reaches(num, registry)})
    BUDGET = 15
    assert len(loose) <= BUDGET, (
        f"{len(loose)} counts in the prose the registry cannot reach (budget {BUDGET}): {loose}")
    assert len(loose) >= BUDGET - 3, (
        f"only {len(loose)} unregistered counts against a budget of {BUDGET} — lower the "
        f"budget to {len(loose)} so it keeps failing on the next one")


def test_no_two_registry_entries_share_a_section_and_a_label():
    """Section plus label is how a failure names itself, so it has to name one thing.

    Two entries can carry the same label and different numbers, and nothing notices until
    the numbers disagree — which is how a duplicate `rev_lagged_cells` reached the manifest
    in the round this test was written: the second copy was pinned to a stale value and the
    drift guard reported it as a drift, not as a duplicate, sending the reader to look at
    the data. The reproduction manifest prints the label as its "what" column, so a repeated
    one also gives the reader two rows they cannot tell apart. Two were live at the time:
    `C.5 those cells' median (%)` for both the named and the unnamed cells, and
    `C.2 median spread among those (%)` for both the frozen and the moving clusters.
    """
    import collections
    seen = collections.Counter((n.section, n.label) for n in pn.canonical_numbers())
    dups = {k: v for k, v in seen.items() if v > 1}
    assert sum(seen.values()) > 500, "the registry did not build; this guard proves nothing"
    assert not dups, (
        f"{len(dups)} (section, label) pair(s) registered more than once, so a failure "
        f"message cannot say which quantity it means: {sorted(dups)}")


def test_every_registered_token_stands_on_its_own():
    """A pinned number must be pinned to itself, not to digits inside a longer number.

    `paper_numbers.appears_in` is a bare `in`. That is what let `0.0%` be credited to
    "median 20.0%" in the budget check next door, and the same shape sits under all 571
    canonical numbers: register `24%` and any `124%` anywhere in the draft satisfies it.

    Measured, at the time of writing: 550 token-file checks, 0 satisfied only by an interior
    match. So `appears_in` is not rewritten — 550 working checks are not worth the risk of a
    regex — and this asserts the measurement instead. The day a short token starts passing
    by coincidence, this fails and `appears_in` gets the boundary.
    """
    checks = 0
    interior = []
    for n in pn.canonical_numbers():
        pairs = [(w, n.claim) for w in n.in_files] if n.claim else []
        pairs += list(n.context.items())
        for w, raw in pairs:
            tok = pn._demark(pn._norm(raw))
            prose = pn._prose(w)
            if tok not in prose:
                continue          # absence is prose_missing's job, not this one
            checks += 1
            if not reaches(tok, prose):
                interior.append(f"§{n.section} {n.label}: {tok!r} in {w}")
    assert checks > 500, f"only {checks} token-file checks reached; the scan has lost its grip"
    assert not interior, (
        f"{len(interior)} of {checks} registered tokens are satisfied only by an interior "
        f"match, so they are pinned to a coincidence: {interior[:5]}")


def test_a_figure_cannot_hide_inside_another():
    """The digits of one number sitting inside another is not a registration.

    This is not hypothetical. `0.0%` was credited to "median 20.0%" and `35%` to "0.35% apart
    at their widest", and when round 8 restated both host claims the two figures fell out of
    the reachable set and the budget check failed — the first sign that anything was wrong.
    Sixteen figures were hiding this way. Every pair below is a real one from that set.
    """
    for tok, host in [("0.0%", "median 20.0%"), ("35%", "0.35% apart at their widest"),
                      ("0.1%", "10.1%"), ("13%", "12.13%"), ("19%", "−48.19%"),
                      ("2.4%", "42.4%"), ("60%", "+160%"), ("50%", "| 12.50% |"),
                      ("$9B", "$19B")]:
        assert not reaches(tok, host), f"{tok} still credited to {host!r}"
    for tok, host in [("12.1%", "a median 12.1% wide"), ("4%", "4% of random placements"),
                      ("24%", "wider than 24%"), ("$9B", "a $9B round"),
                      ("29.1%", "puts 29.1% of cells")]:
        assert reaches(tok, host), f"{tok} no longer reached by {host!r}"


def test_no_bold_figure_in_section_5_escapes_the_registry():
    """A number restated in a second place is the drift the registry cannot see.

    The registry checks that each canonical token APPEARS. It says nothing about a second
    mention of the same quantity somewhere else, and that is how section 6 went on quoting a
    33% share-class guard for a rebuild after section 5.5 recomputed it to 32%, and how
    section 5.7 restated a bucket's share of value that only the table cell was pinned to.
    Both are now pinned by context phrases. This stops the next one: every bolded percentage,
    dollar figure or thousands-count from section 5 onward must be reachable from the
    registry, as a claim token or inside a context phrase.
    """
    import re
    text = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
    # The scope was "section 5 onward" when the population was one section. It is now spread
    # over the data section, the census and the staleness tests, so the anchor moves up to §3 —
    # a strict superset of what it used to cover, not a relaxation.
    body = text.split("## 2. The microscope", 1)
    assert len(body) == 2, "section 2's heading has been reworded; this check has lost its anchor"

    reachable = set()
    for n in pn.canonical_numbers():
        if n.claim:
            reachable.add(n.claim.replace("*", "").strip())
        for phrase in n.context.values():
            reachable.update(x.strip() for x in re.findall(r"[\d.,]+%|\$[\d.,]+B", phrase))
            reachable.add(phrase.replace("*", "").strip())

    # Structural cells of a table that sums to 100 are not results, and a bare count that a
    # claim token carries with its unit ("137 distinct issuers") is reachable through that
    # claim rather than on its own.
    # This used to scan for BOLD figures, which stopped existing when the manuscript was
    # de-bolded — a selector that finds nothing passes vacuously, which is worse than no
    # guard. It scans every percentage and dollar figure now and holds the count the registry
    # cannot reach to a budget: prose restates plenty of figures legitimately, but the number
    # of unregistered ones must not grow. Lower the budget when you register more; raising it
    # is the thing to argue about in review.
    # Prose only. Table cells are pinned row by row elsewhere, and including them buries the
    # thing this check is for: a headline figure restated in a sentence nobody registered.
    prose = "\n".join(l for l in body[1].split("\n") if not l.startswith("|"))
    STRUCTURAL = {"100%"}
    found = re.findall(r"(?<![\d.])[\d][\d.,]*%|\$[\d.,]+[BMT]", prose)
    assert len(found) > 300, "the figure scan has lost its anchor; it should find hundreds"
    # A figure counts as reached only where it stands on its own in the registry string.
    # A bare `in` let one number hide inside another's digits: `0.0%` was reached through
    # "median 20.0%" and `35%` through "0.35% apart at their widest", two figures the registry
    # never held. Both surfaced when round 8 restated those two claims and their host strings
    # went away. The boundary is what makes the check mean what its docstring says.
    loose = []
    for tok in sorted(set(found)):
        bare = tok.strip()
        if bare in STRUCTURAL or bare in reachable:
            continue
        if any(reaches(bare, r) for r in reachable):
            continue
        loose.append(tok)
    # Ninety-two figures in the prose from §3 onward are narrative rather than registered:
    # a company's headline round, an intermediate step in an argument, a percentage quoted
    # from another paper. Each was read once when the budget was set. The budget only ever
    # goes down; raising it is the thing to argue about in review.
    # It sat at 92 against a true 67 for three rounds, which is a ceiling that cannot fail on
    # the next twenty-five unregistered numbers — the defect
    # `test_headline_repetition.py::test_the_ceilings_are_not_slack` exists to stop, and this
    # budget had no such guard of its own. Both halves are asserted now.
    # The budget only goes down, and this one went up, from 55 to 72. That is not a relaxation:
    # the substring match above became a boundary match and stopped crediting a figure to a
    # registry string that merely contained its digits. Sixteen figures had been hiding that
    # way. Fifteen are narrative — a sensitivity band's endpoints, a quarter-by-quarter list,
    # a percentage derived from a count that IS pinned. The sixteenth was a permutation
    # p-value quoted in §8.6 with nothing behind it, and it is registered now. Against the
    # boundary matcher this budget has only ever gone down.
    BUDGET = 72
    assert len(loose) <= BUDGET, (
        f"{len(loose)} figures in the prose from section 3 onward that the registry cannot "
        f"reach (budget {BUDGET}): {loose[:25]}")
    assert len(loose) >= BUDGET - 3, (
        f"only {len(loose)} unregistered figures against a budget of {BUDGET} — lower the "
        f"budget to {len(loose)} so it keeps failing on the next one")


def test_no_loop_target_in_the_registry_builder_shadows_another_name():
    """A `for` target leaks, and this builder is long enough for that to be a real hazard.

    `canonical_numbers` is over thirteen hundred lines and every local is spelled `_x`. A loop
    added to print a table of mean house counts bound `_mh`, which had been set hundreds of
    lines earlier to the ten-name house-level median and is read hundreds of lines later: the
    C.2 percentile silently became "how many venture cells are narrower than 3.4 houses",
    which is 40.8 rather than 63. The registry's own code-drift check caught it because the
    downstream number happened to be pinned. Nothing structural stopped it.

    This is the structural stop. A name bound by a `for` in this function may not also be
    assigned anywhere else in it. Loops that need to reuse a name go in a nested function,
    where the target cannot escape.
    """
    import ast
    src = (ROOT / "src" / "paper_numbers.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    # The builder is five functions, not one; `_population` alone is seven hundred lines.
    builders = [n for n in tree.body
                if isinstance(n, ast.FunctionDef)
                and n.name in {"_build", "_cost", "_microscope", "_dynamic", "_instruments",
                               "_population"}]
    assert len(builders) == 6, f"found {len(builders)} builder functions; re-point this test"

    def names(node):
        return {t.id for t in ast.walk(node) if isinstance(t, ast.Name)}

    problems, seen_any = [], False
    for fn in builders:
        # A nested def has its own scope, which is the fix, so its body is skipped.
        nested = {id(n) for f in ast.walk(fn)
                  if isinstance(f, ast.FunctionDef) and f is not fn for n in ast.walk(f)}
        loop_targets, assigned = set(), set()
        for node in ast.walk(fn):
            if id(node) in nested:
                continue
            if isinstance(node, ast.For):
                loop_targets |= names(node.target)
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    assigned |= names(tgt)
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                assigned |= names(node.target)
        seen_any = seen_any or bool(loop_targets)
        # `_` is the conventional throwaway and carries nothing worth protecting.
        for name in sorted((loop_targets & assigned) - {"_"}):
            problems.append(f"{fn.name}: `{name}` is a loop target and is assigned elsewhere")
    assert seen_any, "no loop targets found at all; the walk is not reading the functions"
    assert not problems, (
        "a loop target that is also assigned elsewhere in the same function, so one block can "
        "silently overwrite another's value hundreds of lines away:\n  "
        + "\n  ".join(problems) + "\nPut the loop in a nested function.")
