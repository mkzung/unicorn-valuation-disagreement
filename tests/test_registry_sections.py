"""Every registry entry names a section the paper still has.

`src/paper_numbers.py` ties each quoted figure to the code that computes it and to the section
that quotes it. The second half was decorative: the section strings were the paper's numbering
from four rounds ago, so `add("5.6", ...)` pointed at a section that had become §5.2, and every
failure message sent a reader to a heading that did not exist.

It also hid a real defect. When the secondary and cycle legs were cut, six entries belonging to
them stayed in the registry and went on passing, because a bare token like `**82**` matches
somewhere in a 28,000-word manuscript whatever it was about. Nothing could notice that their
*section* had been deleted — the section string was already wrong, so wrongness carried no
information.

`SECTION_ALIASES` translates the legacy labels once. This asserts the result: every section a
registry entry names is a live heading, so cutting a section now breaks the build of anything
still registered against it. `paper2` is the one deliberate exception, for figures kept in the
registry because the second paper's data dictionary is still in this repository.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import paper_numbers as pn

DRAFT = (ROOT / "paper" / "draft.md").read_text(encoding="utf-8")
OFF_PAPER = {"paper2"}


def headings() -> set[str]:
    out = set()
    for m in re.finditer(r"^## (?:Appendix )?([A-Z]|\d+)[.] ", DRAFT, re.M):
        out.add(m.group(1))
    for m in re.finditer(r"^### ([A-Z]|\d+)\.(\d+) ", DRAFT, re.M):
        out.add(f"{m.group(1)}.{m.group(2)}")
    return out


def test_the_heading_scrape_is_not_empty():
    h = headings()
    assert len(h) > 50, f"scraped only {len(h)} headings: {sorted(h)}"
    for expected in ("1", "5.1", "G.4", "A", "A.1", "B", "C.5", "E"):
        assert expected in h, f"the scrape missed {expected}"


def test_the_alias_table_only_maps_labels_that_are_used():
    """A dead alias is a comment pretending to be code."""
    used = {m.group(1) for m in re.finditer(r'add\(\s*"([^"]+)"',
                                            (ROOT / "src" / "paper_numbers.py").read_text())}
    stale = sorted(set(pn.SECTION_ALIASES) - used)
    assert not stale, f"SECTION_ALIASES maps labels nothing uses: {stale}"


def test_the_alias_targets_are_live_sections():
    """Checked without building the registry, so this stays a fast test."""
    h = headings()
    bad = sorted(v for v in pn.SECTION_ALIASES.values() if v not in h and v not in OFF_PAPER)
    assert not bad, f"SECTION_ALIASES points at sections the paper does not have: {bad}"


@pytest.fixture(scope="module")
def registry():
    return pn.canonical_numbers()


def test_every_registered_section_exists(registry):
    h = headings()
    bad = sorted({n.section for n in registry} - h - OFF_PAPER)
    assert not bad, (
        f"registry entr(ies) filed under section(s) the paper does not have: {bad}. Either the "
        f"section was cut and its entries should go with it, or it was renumbered and "
        f"SECTION_ALIASES needs the new number.")


def _span(section: str) -> str | None:
    """A section and everything under it, up to the next heading at the same or higher level.

    `## Appendix G.` has to include G.1–G.4 or every figure in its body counts as absent.
    """
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in
             re.finditer(r"^(#{2,3}) (?:Appendix )?([A-Z]\.\d+|[A-Z]|\d+(?:\.\d+)?)[ .]", DRAFT, re.M)]
    for i, (pos, lvl, name) in enumerate(heads):
        if name != section:
            continue
        end = len(DRAFT)
        for pos2, lvl2, _ in heads[i + 1:]:
            if lvl2 <= lvl:
                end = pos2
                break
        return pn._norm(DRAFT[pos:end]).replace("**", "")
    return None


def test_the_span_helper_returns_a_section_and_its_children():
    """Vacuous if `_span` returns the whole paper or nothing."""
    s11, s = _span("G"), _span("5.1")
    assert s11 and s and len(s11) < len(DRAFT) / 3
    assert "G.4" in s11, "Appendix G's span dropped its own subsections"
    assert "### 5.2" not in s, "§5.1's span ran into the next section"
    assert _span("Z") is None


def test_every_pinned_figure_is_stated_in_its_own_section(registry):
    """The prose check is a substring search over 28,000 words; this makes it local.

    That is the hole the six dead entries fell through. Their sections had been cut, their
    tokens still matched somewhere — `82` on the listing-date gap in §9.1, `p=0.43` on the P4
    pre-test, `first` on fifty-six ordinary sentences — and the registry reported a clean run
    for three rounds. A figure that is registered against §5.2 and appears only in §9.1 is
    either mislabelled or orphaned, and both are worth stopping the build for.

    It caught two live breakages the moment it was written: an edit that added a table
    reference had turned "carries a wedge of 0.21 basis points" into "carries 0.21 basis
    points" and "Eight down rounds" into "eight down rounds", and both went on passing on
    restatements elsewhere in the paper.
    """
    bad = []
    for n in registry:
        if not n.claim or "draft" not in n.in_files or n.section in OFF_PAPER:
            continue
        span = _span(n.section)
        tok = pn._norm(n.claim).replace("**", "")
        if span is None:
            bad.append(f"{n.section} | {n.label}: no such section")
        elif tok not in span:
            bad.append(f"{n.section} | {n.label}: {tok[:40]!r} is not in §{n.section}")
    assert not bad, (
        f"{len(bad)} pinned figure(s) whose section does not state them:\n  "
        + "\n  ".join(sorted(bad)))


# A label prefix is a topic: "coordination rule: pairs dated" and "coordination rule: sign p"
# are two figures about one thing, and one thing is discussed in one place. The exceptions are
# read before they are written down.
TOPICS_SPLIT_ON_PURPOSE = {
    "series-fixed tail": "§3.3 states the count and the companies; C.5 adds the top-five share",
}


def _topics(registry):
    out: dict[str, set[str]] = {}
    for n in registry:
        if ":" not in n.label:
            continue
        out.setdefault(n.label.split(":", 1)[0].strip().lower(), set()).add(n.section)
    return out


def _topics_split(registry, allowed=None) -> list[str]:
    """The offenders, as a function so the firing test can drive it on a synthetic registry.

    Written inline first, which made the guard unfalsifiable: there was no way to show it
    detects a split without splitting one in the real registry.
    """
    allowed = TOPICS_SPLIT_ON_PURPOSE if allowed is None else allowed
    return sorted(f"{k!r} is filed under {sorted(v)}"
                  for k, v in _topics(registry).items()
                  if len(v) > 1 and k not in allowed)


def test_the_topic_scrape_finds_the_registry_s_own_grouping(registry):
    """Vacuous if labels stop using the prefix convention, which is how this dies quietly.

    Takes the module fixture. The first version called `canonical_numbers()` itself, which
    rebuilds all 429 figures from production code a second time inside a suite that is already
    the slow one — a guard against waste that was itself wasteful.
    """
    t = _topics(registry)
    assert len(t) > 20, f"only {len(t)} label prefixes; the convention has gone"
    assert max(len(v) for v in t.values()) <= 2, "a topic now spans three sections; re-read this"


def test_a_topic_is_not_split_across_sections(registry):
    """The only anchor a claimless entry has, and 78 of 429 entries are claimless.

    `test_every_pinned_figure_is_stated_in_its_own_section` cannot help there: with no claim
    there is no token to locate, so the section string is decorative and wrongness carries no
    information — the exact failure this module's docstring was written about, surviving in the
    18% of the registry it cannot reach.

    Two entries proved it. "coordination rule: uncensored pairs" and its step were filed under
    §8.4, correctly, until a subsection was inserted ahead of them and §8.4 came to mean
    something else. Their three topic-mates stayed at E.3. Nothing failed, because nothing
    compared them. Grouping by label prefix does, and it costs one exemption to run: of 31
    prefixes exactly one is split on purpose.
    """
    bad = _topics_split(registry)
    assert not bad, (
        "one topic, more than one section:\n  " + "\n  ".join(bad) +
        "\n  Either an entry drifted off its section, or the topic really does span two and "
        "belongs in TOPICS_SPLIT_ON_PURPOSE with the reason.")


def test_the_topic_guard_fires_on_the_pair_it_exists_for():
    """Shown failing on the real defect, in the shape it really had.

    "coordination rule: uncensored pairs" and its step sat at §8.4 while their three
    topic-mates sat at E.3, because a subsection was inserted ahead of them and §8.4 came to
    mean something else. Both carry no claim, so nothing else in this repository could look
    at them. A guard only ever seen passing has not been reviewed.
    """
    from types import SimpleNamespace as N
    drifted = [N(label="coordination rule: pairs dated", section="E.3"),
               N(label="coordination rule: uncensored pairs", section="8.4"),
               N(label="coordination rule: sign p", section="E.3"),
               N(label="venture cells", section="5.2")]          # no colon: not a topic
    assert _topics_split(drifted, allowed={}) == [
        "'coordination rule' is filed under ['8.4', 'E.3']"]

    healed = [N(label=n.label, section="E.3") for n in drifted[:3]] + drifted[3:]
    assert _topics_split(healed, allowed={}) == [], "the guard reports a topic that is whole"
    assert _topics_split(drifted, allowed={"coordination rule": "why"}) == [], \
        "an allowance does not silence the guard"


def test_the_split_exemptions_are_still_split(registry):
    """A dead exemption is a hole nobody is watching."""
    t = _topics(registry)
    stale = sorted(k for k in TOPICS_SPLIT_ON_PURPOSE if len(t.get(k, set())) < 2)
    assert not stale, f"exemption(s) for topics that no longer span two sections: {stale}"


def test_the_locality_check_can_fail(registry):
    """A number moved out of its section must be reported, and one left alone must not.

    Asserted on a real entry rather than a fabricated one: §5.1's population median is in §5.1,
    and the same token filed under §9 would have to fail.
    """
    pinned = [n for n in registry if n.claim and "draft" in n.in_files]
    assert pinned, "no draft-pinned entries; the check above is vacuous"
    sample = next(n for n in pinned if n.section == "5.1")
    tok = pn._norm(sample.claim).replace("**", "")
    assert tok in _span("5.1")
    assert tok not in _span("9"), (
        "the probe picked a token that appears in §9 too; choose another entry")
