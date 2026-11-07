# Rebuild-readiness standard

Purpose: someone who has only the chart image, pasted into their own AI, should be able to rebuild the same chart with the same numbers. The image is the only thing guaranteed to travel, so every breadcrumb must be on the image, legible at pasted resolution. Two tests apply to every piece of on-chart text: **complete** (does a reader have what they need?) and **true** (does it match how the chart was actually built?). A footnote that is complete but wrong is worse than a missing one, because the rebuilder will faithfully reproduce the wrong thing.

## Contents
1. Required elements
2. Accuracy rules (is the text true?)
3. Legibility rules (can an AI read it?)
4. The cold-read test
5. Drafting replacement text
6. Minimal footnote template

## 1. Required elements

Rate each element Present / Partial / Missing, and separately True / Wrong / Unchecked.

| Element | What it must contain |
|---|---|
| Title | The measure, the scope (who/where) and the period. A description, not an unsupported conclusion. |
| Subtitle | Units, transformation (for example z-score, YoY, rebased to 100), frequency, and the sample or universe in one line. |
| Axis labels | Every axis, including secondary and shared axes: quantity and unit (percent, percentage points, basis points, index, z-score). Time axis: frequency and period convention. State log scale and whether panels share a y-axis. |
| Legend and encodings | Every series named by entity and definition, line styles explained (dashed = median), shaded bands defined (min to max, IQR, recession), event shading defined. Colors consistent across panels. |
| Series sources | For each series or group: publisher, dataset name, and the exact identifier (series ID, ticker, table and indicator code), with units, seasonal adjustment and frequency. If many series share a pattern, give the pattern and the exception list. |
| Retrieval and vintage | Date pulled and the last observation date of the data. Vintage or revision caveat when the series is revised. |
| Transformations in order | Each step from raw to plotted, with parameters: formula, base period, window length, rebase date, deflator, sample versus population standard deviation, smoothing, aggregation weights. |
| Universe and membership | Inclusion rules and the full member list (or the rule that generates it), the classification source and version (for example IMF WEO Oct 2026 groups), and the sample size $n$ per panel. |
| Missing data and composition | How gaps are handled, minimum count for a group statistic, and where membership changes over time (series ending early). |
| Annotations | Source or computation for every annotated number (for example "US low: -2.04 (May-26)"). |
| Chart provenance line | Who or what built it and when, only if it helps reproduction (tool or library is optional). |

Every title, subtitle, axis, legend and footnote claim needs a place in this table. Extra text that is not in the table is fine, but missing rows are findings.

## 2. Accuracy rules (is the text true?)

Check each on-chart claim against the recovered provenance (code, data, tool calls) and, where possible, an independent lookup.

- Series IDs exist, name the claimed publisher, and have the claimed units, adjustment and frequency (look up the metadata, do not trust the footnote).
- The stated period equals the plotted data range; last-observation dates in the footnote match the data.
- $n$ in panel titles equals the number of plotted series; the listed members equal the members in the code.
- The method text matches the code: statistic names (mean versus median), band definition (IQR versus min to max), standard deviation convention, minimum-count rule.
- The legend matches the lines (names, colors, styles); panel titles match panel content.
- Units in the subtitle agree with the axis labels and with the data (percent versus percentage points versus basis points).
- Footnote claims about sources, adjustment, classification and retrieval date are supported by the build record, not written from habit.
- Terms are used consistently ("z-score" does not become "standardized index" in another place).

A wrong claim is a Major finding at least. If the wrong claim would lead a rebuilder to different numbers, it is Critical.

## 3. Legibility rules (can an AI read it?)

The image will be downscaled and read by a vision model or OCR.

- Footnote text should stay readable when the image is about 1500 px wide; very small gray text and clipped or overlapping text are findings.
- Do not rely on color alone to separate series; labels or distinct line styles help a reader who gets a compressed image.
- Do not let legends or annotations cover data or other text.
- Keep the footnote in plain prose or short lines, not rotated or on busy backgrounds.
- Long identifier lists belong in the footnote with the pattern form (for example `CSCICP02xxM460S`, where xx is the ISO country code), not omitted.

## 4. The cold-read test

Goal: find what a rebuilder would have to guess.

1. Spawn a fresh agent (the Agent tool, general-purpose) that receives only the chart image: no conversation history, no code, no data, no provenance. Give it this task:

   > You are given only this chart image. Write a rebuild specification for it: for every series, the source, exact identifier, units, frequency and adjustment; every transformation with parameters; the sample and its membership; the date range and retrieval date; how gaps are handled; what each axis, band, line style and shaded area means. Use only what is printed on the image. Do not search the web for the chart's origin. For every item you cannot determine from the image, write GUESS and say what you would have to assume. At the end, list each GUESS labeled BLOCKER (the rebuilt numbers would differ), AMBIGUOUS (several plausible choices), or COSMETIC (look only).

2. If the Agent tool is unavailable, do the cold read yourself as a separate pass before consulting provenance: write the specification from the image alone, committing to it in writing, and say in the report that this pass is less independent than a fresh agent.
3. Compare the cold-read spec with the true provenance. Any item the reader got wrong while believing it was printed (for example, read "interquartile" and rebuilt an IQR band) is a Wrong-text finding. Any BLOCKER is a Major finding at least.
4. Report the count of BLOCKER, AMBIGUOUS and COSMETIC guesses.

Rebuild-readiness result: **READY** (no blockers and no wrong claims), **PARTIAL** (ambiguous items only, or minor wrong text), **NOT READY** (one or more blockers or a material wrong claim).

## 5. Drafting replacement text

When gaps exist, write the replacement text the user can paste into their chart prompt: title, subtitle, axis labels, legend labels and footnote. Rules:

- Use only facts established in the audit (recovered provenance or independent lookup). Never invent an identifier, date, parameter or source to fill a gap.
- Mark anything unknown as `[FILL: what is needed]` so the user sees exactly what to supply.
- Keep each element short; the footnote can be several lines but should read as plain sentences.
- Fix wrong claims in the draft and list each fix in the findings table.
- Put the draft in a code block so it copies cleanly.

## 6. Minimal footnote template

```
Data: [publisher, dataset name], [series ID or pattern], [units], [SA/NSA], [frequency]; [second source...]. Retrieved [date]; latest observation [date].
Sample: [universe and inclusion rule], n=[count]; [classification source and version]. Members: [list or rule]. Series ending early: [name (last obs)].
Method: [transformation 1 with formula and parameters]; [transformation 2]; group statistics = [mean/median/range] across members, shown when at least [k] report; [gap or ratio definition].
Notes: [shaded periods and what they mark]; [annotation sources]; [known caveats].
```
