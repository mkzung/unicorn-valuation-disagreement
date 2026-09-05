"""Guards for the company classification (§5.2).

The labels decide which cells the paper's headline dollar figure is computed over, so the
things that can go wrong quietly are: a verified key that no longer matches any cluster
(the label silently stops applying), a label that covers fewer clusters than it claims, a
rule whose accuracy is asserted rather than measured, and a mismatch detector that fires on
everything and therefore says nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import company_class as cc
import population as pop


@pytest.fixture(scope="module")
def table():
    return cc.classify()


def test_every_verified_key_still_matches_a_cluster(table):
    """A hand-written key is a reference into data that can move under it. When entity
    resolution changes, a stale key does not error — the label just stops applying and the
    cluster quietly falls back to the rule. That is the failure this catches."""
    missing = [k for k in cc.VERIFIED if k not in table.index]
    assert not missing, f"verified labels reference clusters that no longer exist: {missing}"


def test_every_cluster_carries_a_label_and_a_basis(table):
    assert table.label.notna().all() and table.basis.notna().all()
    assert set(table.label) <= {cc.VENTURE, cc.NONVENTURE, cc.LISTED, cc.UNKNOWN}
    assert set(table.basis) <= {"verified", "rule", "unclassified", "unresolved"}


def test_the_verified_labels_cover_the_money(table):
    """The claim in §5.2 is that hand-checked labels cover almost all the booked value. If a
    panel expansion adds a large cluster nobody looked at, that claim quietly weakens."""
    share = table[table.basis == "verified"].nav.sum() / table.nav.sum() * 100
    assert share > 90, f"only {share:.1f}% of booked value carries a verified label"
    # A cluster may be looked at and still not resolve — AH Parent Inc is in VERIFIED with
    # `unclassified` and a note saying why. What must not happen is a large cluster nobody
    # looked at at all, which is membership in VERIFIED rather than the label it received.
    unchecked = table[(table.nav > 5e8) & ~table.index.isin(cc.VERIFIED)]
    assert unchecked.empty, (
        "clusters above $500M nobody has looked at: "
        f"{list(unchecked.index)} — add them to VERIFIED or explain the gap")


def test_the_rule_is_measured_against_the_verified_labels(table):
    """94% is printed in the manuscript. It has to come from a comparison that could fail."""
    acc = cc.rule_accuracy(table)
    assert acc["rule_fired"] >= 50, "too few overlaps for the accuracy figure to mean anything"
    assert acc["rule_abstained"] > 0, "a rule that never abstains is not the rule described"
    assert 0 < acc["accuracy_where_fired"] < 100, "an accuracy of 0 or 100 means the comparison is degenerate"


def test_the_totals_add_up_to_the_panel(table):
    """Four labels, no cell counted twice and none dropped."""
    _, c = pop.panel()
    g = c[c.guarded]
    t = cc.totals(table)
    assert t.cells.sum() == len(g), f"{t.cells.sum()} labelled cells against {len(g)} in the panel"
    assert abs(t.nav_busd.sum() - g.nav.sum() / 1e9) < 0.01
    assert abs(t.nav_pct.sum() - 100) < 0.01


def test_the_mismatch_detector_is_specific(table):
    """The first version flagged one row in six, because most security titles say COMMON
    STOCK and never name the issuer at all. A detector that fires on a sixth of the data is
    not evidence of anything, so this pins both edges: it must fire, and rarely."""
    m = cc.mismatch_stats()
    assert 0 < m["row_pct"] < 5, f"{m['row_pct']:.2f}% of rows flagged; the detector is not specific"
    assert m["clusters"] > 5, "too few clusters flagged for the check to be doing work"


def test_the_mismatch_detector_catches_the_case_it_was_built_for():
    """The filing that started this: a listed Singapore manufacturer's name on a private LNG
    developer's stock. Holdco variants and declared aliases must NOT fire."""
    import pandas as pd
    sample = pd.DataFrame({
        "ISSUER_NAME": ["VENTURE CORP LTD", "FANATICS INC", "DOUYIN CO LTD", "STRIPE INC", ""],
        "ISSUER_TITLE": ["VENTURE GLOBAL LNG INC SR C PP", "FANATICS HOLDINGS INC CLASS A PP",
                         "BYTEDANCE LTD SER E-1 PC PP", "COMMON STOCK", "SOCURE INC PP"],
    })
    got = cc.name_mismatch(sample).tolist()
    assert got == [True, False, False, False, False], got


def test_the_split_keys_are_real_and_fold(table):
    """SAME_ISSUER exists to stop the company count being inflated. Each side of a declared
    split has to be a cluster that actually reaches a cell, or the fold is fiction."""
    absent = [k for k in cc.SAME_ISSUER if k not in table.index]
    assert not absent, f"declared split keys that reach no cell: {absent}"
    ic = cc.issuer_counts(table)
    assert ic["venture_issuers"] < ic["venture_clusters"], "the fold collapses nothing"


def test_the_cap_comparison_changes_only_the_cap():
    """Appendix C.3's bound is worth its two decimal places only if nothing else moved.

    Re-selecting each company's report date was tried first and produced a median of 3.6%
    against 34.7%, because a name's spread depends on where it sits in a repricing. The
    published date is therefore held fixed, and this asserts it: every row of the bulk
    recomputation must sit on the date `reconcile_versions` says the published cell used.
    """
    import pandas as pd
    import fund_marks_bulk as fmb
    import reconcile_versions as rv

    t = fmb.table()
    pub = rv.compare().set_index("company")
    for _, r in t.iterrows():
        want = pd.to_datetime(pub.loc[r.company, "date"], format="%d-%b-%Y").date().isoformat()
        assert r["date"] == want, f"{r.company}: cell on {r['date']}, published cell on {want}"
    assert len(t) == len(pub), "the recomputation lost or gained a company"


def test_the_bulk_cells_never_have_fewer_funds_than_the_published_ones():
    """The cap was one-directional. If a recomputed cell has FEWER funds than the published
    one, the resolver has lost rows rather than the harvest having capped them, and the whole
    comparison is measuring the wrong thing."""
    import fund_marks_bulk as fmb
    t = fmb.table()
    short = t[t.funds < t.published_funds]
    assert short.empty, f"cells with fewer funds than published: {short.company.tolist()}"


def test_the_p4_anchor_still_validates():
    """P4's event is a listing, and every date now comes from the company's own filing.

    What this asserts is the check that licenses those dates: the distance between each one
    and the last report date on which the company appears as a private holding. The
    substitution fails badly on names the cohort excludes — Grab's cells end sixteen months
    before it listed, ServiceTitan's twenty-six — so this is not a formality.
    """
    import listing_dates as ld
    import p4_pretest as p4
    v = p4.validate()
    assert len(v) >= 12, "too few dated listings for the cohort to be built at all"
    assert v.gap_days.abs().max() <= ld.ANCHOR_TOLERANCE, (
        f"a listing date is now {v.gap_days.abs().max()} days from its panel exit")


def test_the_p4_cohort_excludes_the_names_the_anchor_cannot_carry():
    """ServiceTitan and Cava stop appearing in 2022 and listed in December 2024 and June 2023.

    The note-text rule this module used to read let them in. Membership is now a validated
    listing date, which excludes them twice over: the gap fails the check, and both listed
    after the cut the registration reserves for its own test.
    """
    import p4_pretest as p4
    strict = set(p4.cohort().key)
    loose = set(p4.legacy_cohort(loose=True).key)
    assert {"NM:SERVICETITAN", "NM:CAVA"} <= loose, "the loose rule no longer reproduces"
    assert not ({"NM:SERVICETITAN", "NM:CAVA"} & strict), "a mis-anchored name is in the cohort"
    assert len(strict) >= 12, "the cohort has collapsed below a usable size"


def test_no_p4_window_reaches_past_its_own_listing():
    """The correction this round exists for.

    The first version took each company's last four cells, and Palantir's last cell falls
    nine days after it began trading — a mark on a security that already had a public price.
    A window that reaches past the event is not testing dispersion into it.
    """
    import pandas as pd
    import p4_pretest as p4
    t = p4.cohort()
    assert (pd.to_datetime(t.window_to) < pd.to_datetime(t.listing)).all()
    assert (t.days_to_listing > 0).all()


def test_a_level_3_mark_after_a_listing_is_usually_still_inside_the_lock_up():
    """What was on the far side of the line the window now stops at.

    The reading that would be wrong is "funds are slow to reclassify". Most of these marks
    fall inside the customary 180-day lock-up, where an unsaleable share is a Level-3
    measurement under ASC 820 and not a delay at all. If that ever stops being true — if the
    body of the distribution moves past the lock-up — the sentence in `main` has to change
    with it, so the majority is asserted rather than described.
    """
    import p4_pretest as p4
    g, s = p4.reclassification_lag(), p4.lag_summary()
    assert s["marks_inside_lockup"] > s["marks_past_lockup"]
    assert (g.last_days > 0).all(), "a post-listing mark is not after its listing"
    assert int((g.past_lockup == 0).sum()) >= 6, "the lock-up no longer explains the body"
    # The long tail is small positions, and saying so in prose while the data says otherwise
    # is exactly the drift this repository tests for.
    assert s["largest_late_mark_usd"] < 1e6


def test_post_listing_marks_are_too_few_to_carry_a_convergence_test():
    """Item C, answered with a count rather than a shrug.

    The design was to read P4 as convergence error: once a price is observable, marks should
    close on it. The sample that would carry it is the marks dated after a listing, and there
    are 57 of them on ten names, most inside a lock-up that prices the restriction rather
    than the company. Asserted so that if a later harvest changes the answer, the refusal
    fails instead of standing.
    """
    import p4_pretest as p4
    s = p4.lag_summary()
    assert s["post_listing_marks"] < 200 and s["post_listing_names"] < 20, (
        "the post-listing sample has grown; the convergence test may now be worth building")
