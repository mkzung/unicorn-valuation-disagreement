"""Every way the sector split could have been drawn, and what that does and does not settle.

Section 4.2 reports that the secondary-to-headline gap separates on a demand contrast — AI,
data/AI infrastructure and defense against the rest — at a one-sided Mann-Whitney p of about
one in eighty. The soft spot is not the arithmetic: it is that a two-group split of
seventeen points was drawn by the author, nothing registers it as prior, and leave-one-out
cannot answer the objection because leave-one-out varies the sample while the objection is
about the partition. So the curve enumerates every partition instead of defending one.
Simonsohn, Simmons and Nelson (2020) set out the method; their third step, joint inference
across all specifications, is the part that matters here and the part an earlier version of
this module skipped.

Skipping it produced a wrong claim, and the correction is the reason this file exists in its
present form. That version reported two descriptive facts — roughly one partition in twenty
clears p<0.05, and the ones that clear are concentrated on the same three sectors — and read
the second as evidence that the labels carry structure. They do not. Both facts have to be
compared against a null in which the sector labels are shuffled across the seventeen names,
and against that null:

  count of significant partitions   observed sits near the middle of the null. More
                                    partitions separate than a 5% rule of thumb suggests,
                                    and no more than shuffled labels also deliver.

  concentration on a post-hoc core  observed sits near the middle of the null. The mechanism
                                    is plain once stated: under any labelling, the partitions
                                    that separate must contain whichever sectors hold the
                                    extreme gaps, because those are what produce separation.
                                    Concentration therefore distinguishes "some signal exists
                                    somewhere" from "none does". It cannot distinguish a
                                    correct prior from a label fitted to what stuck out.

  rank among equal-size partitions  observed is first of the equally-sized alternatives, and
                                    that is exactly what both a correct prior and a fitted
                                    label produce. It is reported, and it settles nothing.

What remains is a bound rather than a defence, which is the honest description: the curve
shows the contrast is not rescued by the space of alternatives, and the only thing that
separates a prior from a fit is a registration filed before the data are next extended.

The null also replaces a constant. Quoting 5% as the rate chance would deliver is a
continuous approximation; with seventeen points and a discrete rank statistic the attainable
level is lower, so the comparison is made against the permuted rate rather than against the
textbook figure.

Run:  python3 src/sector_specification_curve.py
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, norm, rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import robustness as rb

OUT = ROOT / "data" / "sector_specification_curve.csv"

PAPER_SPLIT = frozenset({"AI", "Data/AI", "Defense"})
MIN_PER_SIDE = 2          # a split needs two names each way for the test to mean anything
ALPHA = 0.05
SEED, DRAWS = 20260624, 2000
CORE_SIZE = 3             # a post-hoc "core" is the three sectors with the highest median gap


def _setup():
    """Gaps, labels, and the sector-space design matrix of every candidate partition."""
    g, _, _ = rb._sector_groups(True)
    gaps = g.gap_pct.to_numpy(float)
    labels = g.sector.to_numpy()
    sectors = sorted(set(labels))
    combos = [c for k in range(1, len(sectors)) for c in itertools.combinations(sectors, k)]
    M = np.zeros((len(combos), len(sectors)), bool)
    for i, c in enumerate(combos):
        for s in c:
            M[i, sectors.index(s)] = True
    return gaps, labels, sectors, combos, M


def _p_one_sided(masks: np.ndarray, ranks: np.ndarray, tie_term: float, n: int):
    """Normal-approximation one-sided Mann-Whitney p per row of `masks`.

    Vectorised because the null needs it: 2,032 partitions times 2,000 shuffles is four
    million tests, and scipy's exact path would take hours to say the same thing. The
    approximation is checked against scipy on the manuscript's own split in __main__.
    """
    n1 = masks.sum(1).astype(float)
    n2 = n - n1
    u = masks @ ranks - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    sd = np.sqrt(n1 * n2 / 12 * ((n + 1) - tie_term / (n * (n - 1))))
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (u - mu - 0.5) / sd
    return norm.sf(z), n1


def _masks_for(labels, sectors, M):
    """Sector-space partitions -> name-space boolean masks under one labelling."""
    ind = np.zeros((len(sectors), len(labels)), bool)
    for j, s in enumerate(sectors):
        ind[j] = labels == s
    return M @ ind


def curve() -> pd.DataFrame:
    """One row per candidate favored-sector set: its one-sided p and median gap difference.

    This took a `clean_only` flag that did nothing. `_setup` reads the clean subsample
    unconditionally, so `curve(False)` returned a frame equal to `curve(True)` — a switch a
    reader could reasonably have believed was a robustness check that had been run.
    """
    gaps, labels, sectors, combos, M = _setup()
    rows = []
    for combo in combos:
        fav = gaps[np.isin(labels, combo)]
        rest = gaps[~np.isin(labels, combo)]
        if len(fav) < MIN_PER_SIDE or len(rest) < MIN_PER_SIDE:
            continue
        rows.append({
            "sectors": "+".join(sorted(combo)),
            "n_sectors": len(combo),
            "n_favored": len(fav),
            "p_one_sided": float(mannwhitneyu(fav, rest, alternative="greater").pvalue),
            "median_gap_diff_pts": float(np.median(fav) - np.median(rest)),
        })
    d = pd.DataFrame(rows).sort_values("p_one_sided").reset_index(drop=True)
    d["rank"] = d.index + 1
    d["contains_paper_core"] = [set(PAPER_SPLIT) <= set(s.split("+")) for s in d.sectors]
    return d


def null_distribution(draws: int = DRAWS, seed: int = SEED) -> dict:
    """Shuffle the sector labels across names and rebuild the curve, `draws` times.

    Two statistics come back with a permutation p each: how many partitions clear ALPHA, and
    how concentrated those partitions are on the post-hoc core. The core is recomputed inside
    every draw — under a shuffled labelling the "obvious" three sectors are different ones,
    and holding the observed core fixed would compare the real analysis against a null that
    was denied the same freedom.
    """
    gaps, labels, sectors, combos, M = _setup()
    n = len(gaps)
    ranks = rankdata(gaps)
    _, counts = np.unique(gaps, return_counts=True)
    tie_term = float((counts ** 3 - counts).sum())

    def stats(lab):
        masks = _masks_for(lab, sectors, M)
        p, n1 = _p_one_sided(masks, ranks, tie_term, n)
        ok = (n1 >= MIN_PER_SIDE) & (n - n1 >= MIN_PER_SIDE)
        sig = np.where(ok & (p < ALPHA))[0]
        share = float(np.mean(p[ok] < ALPHA))
        if len(sig) == 0:
            return len(sig), np.nan, share
        med = pd.Series(gaps).groupby(pd.Series(lab)).median().sort_values(ascending=False)
        core = np.array([s in set(med.index[:CORE_SIZE]) for s in sectors])
        return len(sig), float((M[sig] | ~core).all(1).mean()), share

    obs_n, obs_conc, obs_share = stats(labels)
    rng = np.random.default_rng(seed)
    ns, concs, shares = [], [], []
    for _ in range(draws):
        a, b, c = stats(rng.permutation(labels))
        ns.append(a); shares.append(c)
        if not np.isnan(b):
            concs.append(b)
    ns, concs, shares = np.array(ns), np.array(concs), np.array(shares)
    return {
        "draws": draws,
        "obs_n_sig": obs_n,
        "null_n_sig_median": float(np.median(ns)),
        "p_count": float(np.mean(ns >= obs_n)),
        "obs_concentration": obs_conc,
        "null_concentration_median": float(np.median(concs)),
        "null_concentration_iqr": (float(np.percentile(concs, 25)), float(np.percentile(concs, 75))),
        "p_concentration": float(np.mean(concs >= obs_conc)),
        "obs_share_sig": obs_share,
        "null_share_sig_median": float(np.median(shares)),
    }


def summary(d: pd.DataFrame) -> dict:
    paper = d[d.sectors == "+".join(sorted(PAPER_SPLIT))].iloc[0]
    same_size = d[d.n_favored == paper.n_favored]
    return {
        "n_splits": len(d),
        "paper_p": float(paper.p_one_sided),
        "paper_rank": int(paper["rank"]),
        "paper_rank_among_equal_size": int((same_size.p_one_sided < paper.p_one_sided).sum()) + 1,
        "n_equal_size": len(same_size),
        "n_sig05": int((d.p_one_sided < ALPHA).sum()),
        "share_sig05": float((d.p_one_sided < ALPHA).mean() * 100),
    }


if __name__ == "__main__":
    d = curve()
    d.to_csv(OUT, index=False)
    k = summary(d)
    nul = null_distribution()

    # The vectorised p must agree with scipy where both are computed, or the null is fiction.
    gaps, labels, sectors, combos, M = _setup()
    ranks = rankdata(gaps)
    _, counts = np.unique(gaps, return_counts=True)
    pv, _ = _p_one_sided(_masks_for(labels, sectors, M), ranks,
                         float((counts ** 3 - counts).sum()), len(gaps))
    i = combos.index(tuple(sorted(PAPER_SPLIT)))
    assert abs(pv[i] - k["paper_p"]) < 5e-4, "the vectorised test disagrees with scipy"

    print(f"partitions with at least {MIN_PER_SIDE} names a side: {k['n_splits']:,}")
    print(f"the manuscript's split: p={k['paper_p']:.4f}, rank {k['paper_rank']} overall, "
          f"rank {k['paper_rank_among_equal_size']} of {k['n_equal_size']} favoring as many names")
    print(f"\njoint inference against {nul['draws']:,} label shuffles:")
    print(f"  partitions clearing p<{ALPHA}: {nul['obs_n_sig']} observed vs "
          f"{nul['null_n_sig_median']:.0f} median under shuffled labels "
          f"-> permutation p={nul['p_count']:.2f}")
    print(f"  share clearing p<{ALPHA}: {nul['obs_share_sig']*100:.1f}% observed vs "
          f"{nul['null_share_sig_median']*100:.1f}% under shuffled labels "
          f"(NOT the 5% a continuous approximation would give)")
    print(f"  concentration on the post-hoc core: {nul['obs_concentration']*100:.0f}% observed vs "
          f"{nul['null_concentration_median']*100:.0f}% median "
          f"(IQR {nul['null_concentration_iqr'][0]*100:.0f}-{nul['null_concentration_iqr'][1]*100:.0f}%) "
          f"-> permutation p={nul['p_concentration']:.2f}")
    print("\n  neither statistic separates the labelling from noise; the rank cannot either.")
    print(f"  wrote {OUT.relative_to(ROOT)}")
