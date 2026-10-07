"""Stock splits read off the panel, and the restatement lag that comes with them.

The event study needed round dates and a split history, and the split history was the half
nobody had a source for: N-PORT carries no security-level identifier, N-CSR prints a share
count on a fifth of its rows with no retrospect, and Form D misses the large rounds. It turns
out the panel carries the splits itself.

THE SIGNATURE, AND WHY ONE HALF OF IT IS EXACT AND THE OTHER IS NOT
A share count is a count. When a company splits k for one, a holder that did not trade files
exactly k times as many shares at the next report date, so the balance ratio is k to the
precision of an integer. The price side is not exact and must not be treated as though it
were: the same filing usually carries a fresh mark, so the price falls by roughly 1/k rather
than by exactly 1/k. Baron restated SpaceX at $57.41 in the same month Fidelity restated it at
$56.00, both from a tenfold share count.

So the detector holds the balance to a tight tolerance and asks the price side only to rule out
the alternative. A purchase multiplies the balance and the position value together; a split
multiplies the balance and leaves the value where it was. `VALUE_BAND` is therefore wide on
purpose — it separates a split from a trade, and nothing finer is being claimed of it.

WHY SIMULTANEITY IS THE DISCRIMINATOR, AND WHY IT IS NOT A MONTH
A split reaches every holder on one day; a purchase is one holder's decision. Confirmation
across houses is what separates them, and the reviewer who proposed this rule set the window at
a month. The data says a month is too short. Restatement is not simultaneous: Fidelity restated
SpaceX across February, March and April 2022, T. Rowe restated Perplexity in March 2026 and ARK
in April, Fidelity restated Discord in February and again in March. Requiring one month would
throw away most of the evidence and, worse, would count the desynchronisation as absence.

The window is therefore `WINDOW_MONTHS`, and the spread of restatement dates inside it is
reported rather than smoothed away, because it is the quantity §4.3's "unit convention" outliers
and §5's class guard have been silently absorbing.

WHAT COUNTS AS A HOUSE
Houses, never registrants. Four T. Rowe series restating Perplexity together are one
confirmation, not four; six Fidelity series restating Discord are one. Counting the registrant
is the error §5 spends a section correcting, and it inflates confirmation counts here by three
to six times.

Run:  python3 src/split_events.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import population as pop

OUT = ROOT / "data" / "split_events.csv"

MIN_K = 2               # a one-for-one "split" is not one
MAX_K = 200             # above this the ratio is a redenomination, not a split; see below
# Ratios companies actually split at. A k of 99 or 127 is arithmetic that happens to be close
# to an integer, not a corporate action, and Carbon Health at 99 and Pine Private at 127 are
# what the filter returns when it is allowed to believe any integer. Reported rather than
# dropped, because the point of the flag is that the reader can see which is which.
CANONICAL_K = {2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 50, 100}
BALANCE_TOL = 0.005     # share counts are integers, so this side is held tight
VALUE_BAND = (0.55, 1.8)  # position value survives a split and scales with a purchase; this
                        # only has to tell those two apart, and is deliberately not tighter
WINDOW_MONTHS = 3       # houses restate in different months, so confirmation is a window
MIN_HOUSES = 2          # one house moving alone is a trade until a second house agrees


def _fund_series(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per company, fund and report date, with the previous date's ratios."""
    d = pop.comparable(pop.load_marks()) if d is None else d
    d = d.assign(balance=pd.to_numeric(d.balance, errors="coerce"),
                 val_usd=pd.to_numeric(d.val_usd, errors="coerce"))
    d = d[(d.balance > 0) & (d.pps > 0)].dropna(subset=["dt"])
    # A fund can file several lines of one company on one date — different lots or classes —
    # and the split applies to the position, so the lines are summed before the ratio is taken.
    g = (d.groupby(["company", "fund", "house", "CIK", "dt"])
           .agg(balance=("balance", "sum"), val=("val_usd", "sum")).reset_index())
    g["pps"] = g.val / g.balance
    g = g.sort_values(["company", "fund", "dt"])
    prev = g.groupby(["company", "fund"])
    g["prev_dt"] = prev.dt.shift()
    g["rb"] = g.balance / prev.balance.shift()
    g["rp"] = g.pps / prev.pps.shift()
    g["rv"] = g.val / prev.val.shift()
    return g


def candidates(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Fund-dates whose share count multiplied by a whole number without the value following."""
    g = _fund_series(d).dropna(subset=["rb", "rv"])
    k = g.rb.round()
    ok = ((k >= MIN_K) & (k <= MAX_K)
          & ((g.rb / k - 1).abs() < BALANCE_TOL)
          & g.rv.between(*VALUE_BAND))
    out = g[ok].copy()
    out["k"] = k[ok].astype(int)
    return out.reset_index(drop=True)


_MEMO: dict[str, pd.DataFrame] = {}


def events(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """Candidates confirmed by a second house within the window.

    The window slides over each company's own restatement dates rather than over the calendar,
    so a split whose restatements straddle a quarter boundary is one event and not two.

    The default call is memoised on the panel's cache key for the reason `round_dates.first_seen`
    gives: the selection ladder asks for it once per rung, and each miss re-resolves the whole
    marks file. The key is the source file's mtime and size, so the memo cannot outlive it.
    """
    if d is None:
        key = pop._cache_key()
        if key not in _MEMO:
            _MEMO.clear()
            _MEMO[key] = _events(None)
        return _MEMO[key].copy()
    return _events(d)


def _events(d: pd.DataFrame | None) -> pd.DataFrame:
    c = candidates(d)
    rows = []
    for (co, k), g in c.groupby(["company", "k"]):
        g = g.sort_values("dt")
        start = None
        for dt in g.dt.unique():
            if start is None or (dt - start).days > WINDOW_MONTHS * 31:
                start = dt
            g.loc[g.dt == dt, "_win"] = start
        for _win, w in g.groupby("_win"):
            rows.append({
                "company": co, "k": k,
                "first_dt": w.dt.min().date().isoformat(),
                "last_dt": w.dt.max().date().isoformat(),
                "restatement_span_days": int((w.dt.max() - w.dt.min()).days),
                "funds": w.fund.nunique(), "houses": w.house.nunique(),
                "registrants": w.CIK.nunique(),
                "canonical_k": k in CANONICAL_K,
                "houses_list": " | ".join(sorted(set(w.house))[:6]),
            })
    e = pd.DataFrame(rows)
    return (e[e.houses >= MIN_HOUSES]
            .sort_values(["houses", "funds"], ascending=False).reset_index(drop=True))


def restatement_lag(d: pd.DataFrame | None = None) -> dict:
    """How far apart houses are when they restate one split.

    The reviewer's third consequence, measured: if restatement were simultaneous the span
    would be zero and a one-month window would lose nothing. It is not zero.
    """
    e = events(d)
    if e.empty:
        return {"events": 0}
    return {"events": len(e),
            "companies": int(e.company.nunique()),
            "median_span_days": float(e.restatement_span_days.median()),
            "max_span_days": int(e.restatement_span_days.max()),
            "events_inside_one_month": int((e.restatement_span_days <= 31).sum()),
            "houses_inflated_by_counting_registrants":
                float((e.registrants / e.houses).median()),
            "events_at_a_canonical_ratio": int(e.canonical_k.sum())}


def guard_overlap(d: pd.DataFrame | None = None) -> dict:
    """Does the 4x class guard discard cells that sit inside a restatement window?

    §5 drops a company-date whose extreme house marks differ by more than fourfold, and reads
    those as unit or share-class artifacts. If one house has restated a split and another has
    not, the two marks differ by exactly the split factor and the guard fires on a dating
    difference rather than on a class difference. This measures how much of the guard's work
    that accounts for — and the answer is what decides whether the reviewer's second
    consequence is a real correction or a small one.
    """
    d = pop.load_marks() if d is None else d
    _, c = pop.panel() if d is None else (d, pop.cells(d))
    dropped = c[~c.guarded]
    e = events(d)
    if e.empty:
        return {"cells_dropped_by_guard": len(dropped), "inside_a_restatement_window": 0}
    win = {}
    for _, r in e.iterrows():
        win.setdefault(r.company, []).append(
            (pd.Timestamp(r.first_dt) - pd.Timedelta(days=WINDOW_MONTHS * 31),
             pd.Timestamp(r.last_dt) + pd.Timedelta(days=WINDOW_MONTHS * 31)))
    def inside(co, dt):
        return any(a <= dt <= b for a, b in win.get(co, []))
    hit = [inside(co, dt) for co, dt in zip(dropped.company, dropped.dt)]
    named = dropped[dropped.company.isin(set(e.company))]
    hit_named = [inside(co, dt) for co, dt in zip(named.company, named.dt)]
    return {"cells_dropped_by_guard": len(dropped),
            "inside_a_restatement_window": int(sum(hit)),
            "share_pct": float(sum(hit) / max(len(dropped), 1) * 100),
            # The conditional number, which is the fair one: among companies that DO have a
            # confirmed split, how much of the guard's work is the restatement lag?
            "dropped_on_a_company_with_an_event": len(named),
            "of_those_inside_a_window_pct":
                float(sum(hit_named) / max(len(named), 1) * 100),
            "companies_with_an_event": int(e.company.nunique())}


def validate(d: pd.DataFrame | None = None) -> pd.DataFrame:
    """The check the mechanism has to pass: a mid-restatement cell must be split by exactly k.

    If one house has restated a k-for-one split and another has not, the two are quoting the
    same security in units that differ by exactly k, so their price ratio is k and dividing the
    un-restated side by k has to make the cell agree. That is a prediction with a number in it,
    and it is what separates this from a story about why some ratios look tidy.

    Reported per event as the ratio between the two groups at the dates where both are present.
    """
    d = pop.comparable(pop.load_marks()) if d is None else d
    g = _fund_series(d)
    c = candidates(d)
    done = {(r.company, r.fund, r.dt) for r in c.itertuples()}
    rows = []
    for _, ev in events(d).iterrows():
        lo, hi = pd.Timestamp(ev.first_dt), pd.Timestamp(ev.last_dt)
        w = g[(g.company == ev.company) & (g.dt >= lo) & (g.dt <= hi)]
        for dt, s in w.groupby("dt"):
            # A fund has restated by `dt` if its jump happened at or before it.
            # The three are bound as defaults rather than captured: `.map` happens to
            # run this inside the iteration, so a captured `dt` is correct today, but the
            # correctness would rest on pandas evaluating eagerly rather than on the code.
            restated = s.fund.map(
                lambda f, co=ev.company, dates=tuple(w.dt.unique()), upto=dt:  # noqa: B008
                # B008 assumes a default is evaluated once at import. This lambda is
                # built inside the loop, so the call in its default runs per iteration,
                # which is the whole point: it snapshots this window's dates.
                any((co, f, x) in done for x in dates if x <= upto))
            if not restated.any() or restated.all():
                continue
            old, new = s.pps[~restated].median(), s.pps[restated].median()
            rows.append({"company": ev.company, "k": ev.k, "dt": dt.date().isoformat(),
                         "funds_restated": int(restated.sum()),
                         "funds_not": int((~restated).sum()),
                         "pps_not_restated": float(old), "pps_restated": float(new),
                         "observed_ratio": float(old / new),
                         "residual_pct": float(abs(old / new / ev.k - 1) * 100)})
    return pd.DataFrame(rows)


def main() -> None:
    d = pop.comparable(pop.load_marks())
    c = candidates(d)
    print(f"candidate fund-dates: {len(c)} on {c.company.nunique()} companies")
    e = events(d)
    e.to_csv(OUT, index=False)
    print(f"\nconfirmed by {MIN_HOUSES}+ houses inside {WINDOW_MONTHS} months: {len(e)}")
    print(e[["company", "k", "canonical_k", "first_dt", "last_dt", "restatement_span_days",
             "funds", "houses", "registrants"]].to_string(index=False))
    lag = restatement_lag(d)
    print(f"\nrestatement is not simultaneous: median span {lag['median_span_days']:.0f} days, "
          f"largest {lag['max_span_days']}, and only {lag['events_inside_one_month']} of "
          f"{lag['events']} fit inside a single month.")
    print(f"  counting registrants instead of houses would multiply the confirmation count by "
          f"{lag['houses_inflated_by_counting_registrants']:.1f}x at the median event.")
    v = validate(d)
    if not v.empty:
        ok = (v.residual_pct < 10).mean() * 100
        print(f"\nmid-restatement cells where both groups are present: {len(v)}. The price ratio "
              f"between them should be k; it is within a tenth of k in {ok:.0f}% of them.")
        print(v.sort_values("residual_pct").head(8).round(3).to_string(index=False))

    ov = guard_overlap()
    print(f"\nthe 4x class guard drops {ov['cells_dropped_by_guard']} cells; "
          f"{ov['inside_a_restatement_window']} of them ({ov['share_pct']:.1f}%) sit inside a "
          f"restatement window. Conditioning on the companies that have one at all, "
          f"{ov['of_those_inside_a_window_pct']:.0f}% of the "
          f"{ov['dropped_on_a_company_with_an_event']} cells dropped there are inside a window.")
    print(f"  wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
