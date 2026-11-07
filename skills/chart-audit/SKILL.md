---
name: chart-audit
description: Skeptically audit a chart (usually a PNG/screenshot, sometimes with CSV/Excel/code or an HTML artifact) for data validity, provenance, transformation errors, misleading visual design, unsupported claims, and rebuild-readiness (whether the title, subtitle, axis labels, legend, sources and footnote are accurate and complete enough for someone to rebuild the same chart from the image alone). Use whenever the user types /chart-audit or says audit, check, verify, fact-check, sanity-check, "is this chart right", "are my sources and footnotes right", or "can someone rebuild this" about any chart, graph, or visual, including charts an AI made earlier in this or another chat. Use it even if the user only says "double-check this" while a chart is in context.
---

# Chart Audit

The user builds many charts with AI and often does not know where the data came from, how it was pulled, or how it was transformed. Your job is to be the independent check. Assume the chart is wrong until specific evidence shows otherwise. A chart that looks clean and professional proves nothing: AI-made charts fail silently (wrong series ID, stale vintage, unit mix-ups, truncated axes, fabricated or "remembered" numbers) and still look polished.

Treat every earlier Claude output in the conversation, including the code that made the chart and any stated source, as an unverified claim, not as evidence. Re-running the same pipeline and getting the same numbers proves reproducibility, not correctness. Verification needs an independent route to the truth.

The user also makes charts so that other people can paste the image into their own AI and rebuild it. The image is the only thing guaranteed to travel, so the chart's own text (title, subtitle, axis labels, legend, sources, footnote) is part of what you audit, with two questions: is it **complete** (could a stranger rebuild the same numbers from it?) and is it **true** (does it match how the chart was actually built?). A footnote that is complete but wrong is worse than a missing one, because a rebuilder will faithfully reproduce the error. Step 8 and `references/rebuild-readiness.md` cover this.

## Core rules

1. Keep three states strictly separate in everything you report: **Verified** (matched against an independent source), **Inferred** (reasoned or read off the image, not confirmed), **Unverifiable** (no way to check from here). Never let "inferred" or "unverifiable" read as "verified."
2. Absence of evidence is a finding. If the chart has no source, no date of last update, no units, or no transformation note, that is itself an issue.
3. Report disconfirming evidence prominently and do not soften it. The user wants a real check, not reassurance.
4. Say exactly what you did and did not check (coverage), so the user knows how much weight the verdict carries.

## Workflow

### Step 0: Recover provenance
Find out how the chart was made before judging it.
- Look in the current conversation for the code, data files, queries, tool calls, and any stated source behind the chart.
- If the chart came from an earlier chat, search past chats (conversation_search, then read_conversation) for the build.
- Check attached files (CSV/Excel/code) with Read or Bash.
- If nothing is recoverable, record "provenance unrecoverable" as a finding and continue by reverse-engineering from the image. Do not invent a source to fill the gap.

### Step 1: Inventory the chart's claims
Write down, in a compact table, everything the chart asserts: title and subtitle, series names, chart type, axis labels, units, frequency, date range, source footnote, annotations, base year or index base, and any transformation implied (YoY, MoM, rebased, real vs nominal, smoothed, cumulative, spread vs level). Note what is missing from this list.

### Step 2: Visual integrity audit (what the picture does to the reader)
Look for: truncated or non-zero baselines on bars, dual axes that manufacture correlation, unlabeled or inconsistent units, mixed frequencies, log vs linear not stated, cherry-picked start/end dates, aspect ratio or scale that exaggerates moves, misleading color or sign conventions, legends that do not match lines, interpolated gaps drawn as real data, and smoothing not disclosed. See `references/checklist.md` for the full list, including macro-finance conventions that commonly go wrong.

### Step 3: Data lineage audit (where the numbers came from)
Identify for each series: the exact source and series identifier, frequency, vintage or pull date, revision risk, definition (for example which index, which currency, local vs hard currency, which tenor), and every transformation between raw data and plotted values. Flag joins, date alignment, timezone or fiscal-calendar mismatches, missing-data handling, unit conversions, and sign conventions. If the chart says "Source: X" check that X actually publishes that exact series.

### Step 4: Get the underlying values
- If a data file or code is available, load the data it actually plots (not a re-derived version).
- If only an image exists, digitize it: estimate values at the points you will test (Step 5) by reading them against the axes. Use Python with PIL or OpenCV for pixel-to-value mapping when precision matters, and calibrate with at least two labeled tick marks per axis. State the read-off tolerance, typically ±1 to 2 percent of the axis range.

### Step 5: Risk-based sampling against an independent source
Do not check points uniformly. Concentrate effort where errors hide, then sample the rest.

**Tier 1, always check:** first and last observation, the latest data point (stale data is the commonest failure), series maximum and minimum, every labeled or annotated point, every number the title or text cites, visible breaks, spikes and discontinuities, and any point that looks implausible.
**Tier 2, random sample:** a seeded random sample from the remaining points, at least 10 percent of points per series and never fewer than 8, stratified across the date range and across series so no series or era goes unchecked.
**Tier 3, structural checks on all points (cheap, so do them exhaustively):** date range and frequency match the claim, no duplicate or out-of-order dates, no unexplained gaps, row counts agree across series, no impossible values (negative prices, shares over 100 percent, sums of parts not equal to the total).
**Escalation rule:** if any Tier 1 or Tier 2 point mismatches beyond tolerance, double the sample for that series. If a second mismatch appears, compare the full series. A single mismatch is evidence of a systematic error until shown otherwise, so look for the pattern (off by a constant, shifted by one period, wrong unit, wrong series).

`scripts/sample_plan.py` generates the Tier 1 and Tier 2 sample plan, with a fixed seed, from a CSV of the plotted data, so the check is reproducible. Run it when you have tabular data.

**Independent sources.** Prefer an official or primary source different from the one the chart used (FRED, central bank or statistical office, IMF/World Bank databases, exchange or index provider, company filings). Use the FRED connector or web search to re-pull. If the chart's source is a terminal you cannot reach (Bloomberg, Haver, Refinitiv), say so, mark those points Unverifiable, and fall back to cross-checks: a public proxy series, known historical events, or identities that must hold. Never fill the gap with numbers from memory and call it verified.

### Step 6: Plausibility and cross-checks
Even when a source cannot be re-pulled, test the numbers: order of magnitude, base rates, consistency with well-known episodes (for example, known crisis dates should show up where they should), internal identities (parts sum to whole, growth rates consistent with levels), and consistency between the chart and any table or text beside it.

### Step 7: Claims audit
Compare what the title, caption, and any accompanying text say against what the data supports. Flag causal language on correlational data, "record high" or "lowest since" claims that were not tested against the full history, trend claims resting on two points, and conclusions the chart cannot support.

### Step 8: Rebuild-readiness audit (is the chart's own text complete and true?)
Read `references/rebuild-readiness.md` first. It holds the required-element table, the accuracy rules, the legibility rules, the cold-read procedure, and the footnote template. The breadcrumbs must live on the image itself, because that is what gets pasted into another AI.

1. **Element check.** Rate every required element (title, subtitle, axis labels, legend and encodings, series sources with exact identifiers, retrieval and vintage dates, transformations in order with parameters, universe and membership, missing-data and composition handling, annotation sources) as Present / Partial / Missing.
2. **Accuracy check.** Test each piece of on-chart text against the provenance from Step 0 and against an independent lookup where possible: series IDs exist with the stated publisher, units and adjustment; stated period equals the plotted range; $n$ equals the number of plotted series; the method text (mean versus median, IQR versus min to max, standard deviation convention) matches the code; the legend matches the lines; subtitle units agree with axis labels. Mark each True / Wrong / Unchecked.
3. **Legibility check.** Is the footnote readable when the image is downscaled, free of clipping and overlap, and not dependent on color alone?
4. **Cold-read test.** Spawn a fresh agent that receives only the image and asks it to write a rebuild specification, marking every item it had to GUESS as BLOCKER, AMBIGUOUS or COSMETIC (exact prompt in the reference file). Compare its spec with the true provenance: anything it got wrong while believing it was printed is a Wrong-text finding. If you cannot spawn an agent, do the pass yourself from the image alone before looking at provenance, and say the test was less independent.
5. **Draft replacement text.** Write the corrected title, subtitle, axis labels, legend labels and footnote using only facts established in the audit. Mark anything unknown as `[FILL: what is needed]`. Never invent an identifier, date, or parameter to fill a gap.

## Output format

Direct, no pleasantries. Use this structure exactly.

**Verdict:** one of PASS / PASS WITH CAVEATS / FAIL / CANNOT VERIFY, followed by one sentence of reasoning. Use PASS only if Tier 1 and Tier 2 checks matched an independent source and no material visual or lineage issue remains. If provenance was unrecoverable or the source was unreachable, the verdict cannot be PASS; use CANNOT VERIFY or PASS WITH CAVEATS and say why.

**Rebuild readiness:** one of READY / PARTIAL / NOT READY, on the line directly under the verdict, with one sentence of reasoning. READY means no blockers and no wrong claims in the chart's text; PARTIAL means only ambiguous items or minor wrong text; NOT READY means one or more blockers or a material wrong claim. This is judged separately from the data verdict: a chart can have correct data and still be NOT READY, or the reverse.

**Coverage:** a short table: series, points checked out of total, tiers covered, source used for the check, tolerance applied, and status (Verified / Inferred / Unverifiable).

**Findings:** a table ranked by severity, with columns: #, Severity (Critical / Major / Minor), Check (which step), Finding, Evidence, Fix. Critical means the chart's conclusion could be wrong, or wrong text would make a rebuilder produce different numbers. Major means a number or label is wrong or misleading, or a blocker exists for rebuilding. Minor means polish or disclosure.

**Rebuild readiness detail:** a compact table with one row per required element: element, Present/Partial/Missing, True/Wrong/Unchecked, and the gap. Follow it with the cold-read result: counts of BLOCKER, AMBIGUOUS and COSMETIC guesses, and the blockers listed.

**Drafted replacement text:** when any element is Partial, Missing or Wrong, give the corrected title, subtitle, axis labels, legend labels and footnote in a code block the user can paste into their chart prompt. Use only facts established in the audit and mark unknowns as `[FILL: ...]`.

**What I could not check:** an explicit list, so the user knows the residual risk.

**Corrected version (when fixable):** if the fix is clear (right series, right unit, right axis), offer to rebuild the chart, and say what changes. If the user asks for a script, give a reproducible Python block that re-pulls the data and re-runs the checks. Write any formulas in LaTeX.

Keep the whole report scannable. Lead with the verdict and the Critical findings.
