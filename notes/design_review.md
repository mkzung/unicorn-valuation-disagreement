# Design review: the thing no guard catches

475 registered numbers and 230 tests did not catch §3.3, and could not have. Every figure
in it was correctly computed from the code that produced it, and the code did what the code
said. What was wrong was the *design* of the filter: it restricted to cells whose filings
never name two different letters, which is satisfied both by "every filer named the same
series" and by "nobody named anything", and the second is the common case. The median share
of rows carrying any letter inside that subset was zero. Two thirds of a bound on
security-identification was computed on cells whose security is unknown.

A drift guard compares a number against its own code. When the code is a faithful
implementation of the wrong question, the two agree forever.

## How it was actually found

A reviewer re-ran the filter and looked at what it selected — not at what it returned. Three
lines of pandas: group the subset by whether any row names a letter, and print the medians.
The vacuity is visible immediately and invisible from any other angle, including from a
green test suite and from reading the section carefully, which had been done four times.

## The practice this repository adopts

**Periodically re-derive each load-bearing number by a second route, and inspect what each
filter selects rather than what it returns.** Not a new test — the failure is that a test
cannot hold an opinion about whether the question is the right one. Concretely, for each
headline figure:

1. Recompute it from a different starting point where one exists. §2.2's N-CSR harvest and
   §3.3's series-fixed panel are now exactly this pair: hand-parsed schedules against
   structured bulk data, agreeing that two houses on one verifiable security file one number.
2. Print the composition of every filtered subset — how many rows/cells each branch of the
   filter admits, and the outcome separately by branch. A filter whose branches disagree is
   a filter measuring two things.
3. Ask what the sample would look like if the hypothesis were false, and check that the
   filter can produce it. §3.3's could not: cells with no named security could never show
   "same security, different price", so their inclusion could only dilute.
4. **A filter defined by the absence of a feature must print the share of observations that
   pass because the feature is present and compatible, separately from the share that pass
   because the feature is absent.** This is the reviewer's step and it is the one that would
   have caught §3.3 first: the filter was "no two different letters", 64% passed because
   there were no letters at all, and one line of output — positive versus vacuous — makes
   that visible immediately. The rule generalises past this case. It catches an empty
   `str.contains("")`, an empty pattern list, and any future filter written as a negation.

## Where this is scheduled

Before each version is sent out, and recorded in the round report. Rounds 22 and 23 both
found defects this way that the suite could not: 22 by re-reading every section against the
function that computes its numbers, 23 by re-running a filter and printing its composition.

## The related failure mode in the guards themselves

Three checks written in round 23 failed on *correct* text before they were fixed:

* the predicate guard banned a phrase as a substring and so rejected the corrected sentence,
  which contains the phrase inside a negation;
* the PDF guard looked for a literal superscript that `pdftotext` renders with a space;
* the staleness guard compared mtimes, which after `git clone` are arbitrary — it asked
  whether the build happened after the edit rather than whether the artifact matches the
  text, and told a reviewer to rebuild a PDF that was already correct.

The common shape is the same one as §3.3: **a proxy standing in for the property, checked
instead of the property.** A guard is subject to design review exactly like an analysis, and
a guard that has never been shown failing on the real defect has not been reviewed at all.

## Step five: a full rewriting pass is a verification method

Twice in consecutive rounds a wrong number was found by a *style* complaint rather than by
any check on numbers. A reviewer objected to four indistinguishable grey dots on one row of
a figure; running that down showed the ten-name panel was pooling seven named houses into a
single unit, and the house-level median it reported was 12.6% where the truth was 23.7%. A
reviewer then objected to sentence length; splitting one of the sentences surfaced "those ten
sit at the median of the distribution", a claim the correction above had already moved to the
60th percentile. The same phrase turned up a third time inside a phrase fix, which is prose
and goes stale like prose while no guard can see inside it.

The mechanism is worth stating because it is general. **A registry compares a value against
the code that computes it. Rewriting a sentence compares the claim against its meaning.**
Those are different comparisons and they fail at different things: 417 pinned numbers, all
green, could not see a sentence whose number was right and whose claim about it was wrong,
because the claim was a word — "median" — and not a figure.

So a full rewriting pass belongs on this list beside re-reading the code and re-running the
filters, and it is scheduled the same way: before a version goes out, and reported with what
it found rather than with what it polished. Its distinguishing property is that it cannot be
automated, because the thing it checks is whether the sentence still means what the analysis
now says.
