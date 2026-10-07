# Compliance & IP — the clean operating standard (v2, 2026-06-27)

**Bottom line:** facts cannot be owned; an original, multi-source, value-added compilation of facts is *mine*. This is how academic researchers build unicorn datasets, and the paper needs no permission emails — provided it is built the careful way set out below.

## The principle (grounded)
- **Facts aren't copyrightable** — *Feist v. Rural* (1991). Valuations, founding dates, round sizes, IPO prices = facts. No one owns them.
- **Compilation copyright is "thin"** — protects only original *selection/arrangement*, not the underlying facts. "US copyright law does not prevent the extraction of unprotected data from an otherwise protectable database." Scraping facts and aggregating them into a database is "generally fine in the US."
- **A derived compilation is original work** in its own right (independent copyright from its selection and arrangement plus the computed columns), so diluting a fact set with my own data and metrics makes the result mine for the factual core.

## The four rules this project follows
1. **Take facts, not compilations.** Never reproduce a single vendor's full proprietary table verbatim as "their dataset." Pull individual facts from **≥2 sources** and rebuild. (Also defeats the **UK/EU sui-generis database right**, which can protect a "substantial part" of one DB even for factual contents — multi-source = no substantial part of any one.)
2. **Acquire cleanly.** Public (non-logged-in) pages, official free tiers, or licensed access. Don't click-accept a ToS and then breach it; don't scrape behind a login; don't exceed export caps. (*hiQ v. LinkedIn*: scraping *public* data is broadly defensible; breaching an accepted ToS is the real risk.) ⇒ **PitchBook stays out** (export caps + no-publish term); **no automated Yahoo scraping** in production.
3. **Attribute everything.** Crunchbase requires a visible hyperlink; cite Forge, SEC, news per source.
4. **Publish derived analysis, not raw dumps.** The gaps, dispersion measures and classifications are my own computed columns; a vendor's raw rows are not mine to repost.

## Source-by-source (refined)
- **SEC (N-PORT/N-CSR/S-1/424B/Form D)** — public domain; republish freely. **The spine.**
- **Crunchbase** — license **expressly allows publishing "analysis and aggregate statistics derived from the data"** (notify them on publish + attribute; don't redistribute raw). Free **Venture Program** tier exists; **Enterprise** = "internal research and analysis"; the **2013 Snapshot is CC-BY**. Individual facts via the website are usable as facts. **Green for derived analysis.**
- **Forge** — cite **individual** figures (index level + per-company estimates) **with attribution** as facts/estimates (standard practice — news outlets do it routinely); use them as **inputs to my own computed metrics**. Avoid reproducing the **entire 42-row table** verbatim as "the Forge dataset." A permission email would only be needed to reproduce the full series verbatim, which the paper does not do. **Not a blocker.**
- **Yahoo Finance** — display layer only; get the underlying facts from the source. No automated scraping in production.
- **CB Insights** — don't reproduce their curated list; use as a lead, re-source the facts.
- **WRDS/PitchBook** — PitchBook out. WRDS CRSP/Compustat was scoped for the validation leg and then dropped: raw WRDS data may not be redistributed, and the realized IPO prices were available from public reporting, so the pipeline needs no licensed data (`notes/data_rights_and_method.md`).

## A result that falls out of the sourcing problem
The trackers **disagree on the count itself** — **CB Insights ~1,334 vs Crunchbase ~1,660 unicorns (Jan 2026)**, a 300+ gap from timing/sources/definitions. Build a transparent, **rules-based sample anyone can verify**; the count-level disagreement is itself a result reinforcing the valuation-disagreement thesis.

## Net position
Original multi-source **fact** compilation, my own metrics, and attribution: clean under US copyright, the UK/EU database right, and contract.
