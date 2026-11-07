# Chart audit checklist

Load this when running Step 2 (visual integrity) and Step 3 (lineage) of the audit. Each item is a failure mode that AI-generated charts show repeatedly. Work through the ones that apply to the chart type; skip the rest.

## Contents
1. Visual integrity
2. Data lineage and definitions
3. Transformations
4. Time and frequency
5. Macro-finance conventions (EM sovereign debt, capital flows, markets)
6. Common AI-specific failure modes
7. Digitizing a PNG

## 1. Visual integrity

| Check | What goes wrong |
|---|---|
| Bar baseline | Bars on a non-zero axis exaggerate differences. Bars must start at zero; lines need not. |
| Dual axes | Two y-axes let the author choose scales that create apparent correlation or crossover. Treat any dual-axis chart as suspect and test whether the story survives on a common scale or indexed. |
| Axis range | Range chosen to make a small move look large, or clipping that hides outliers. Check whether the axis crops data. |
| Log vs linear | Not stated. Equal vertical distances mean different things. |
| Units | Missing, inconsistent between series, or in the title only. Check percent vs percentage points vs basis points, millions vs billions, local currency vs USD. |
| Legend and color | Legend order or color does not match the lines. Red/green used with inverted meaning (for example, a rising spread shown as green). |
| Gaps and interpolation | Missing data drawn as a straight line across the gap, or zeros plotted for missing values. |
| Smoothing | Moving average or LOESS applied without disclosure, which hides the true timing of turns. |
| Cherry-picked window | Start or end date chosen to produce the trend. Check what the chart looks like with a longer window. |
| Aspect and scale | Very wide or very tall aspect ratio changes perceived slope. |
| Annotations | Labels and arrows that sit on the wrong date or assert causation. |
| Pie and stacked charts | Parts not summing to 100 percent or to the stated total; stacked areas that hide a series' own trend. |

## 2. Data lineage and definitions

Identify, for every series: source, exact series ID or ticker, frequency, vintage (pull date), revision behavior, and definition.

- **Series identity.** The most frequent silent failure is a plausible but wrong series: the right concept with the wrong tenor, the wrong country aggregate, the wrong index family, nominal instead of real, or seasonally adjusted instead of not.
- **Source claim.** Check that the named source actually publishes this series, at this frequency, under this name.
- **Vintage.** Revised series (GDP, flows, reserves) differ across vintages. Note whether the chart used real-time or latest-revised data and whether that matters to the claim.
- **Staleness.** The last plotted date should match the latest available release. A chart whose last point is months old but whose title implies "latest" is a finding.
- **Coverage.** Country or entity set is complete and consistent over time (changing sample composition creates fake trends).
- **Definition drift.** The definition changed within the sample (rebasing, methodology change, euro adoption, index rebalancing).

## 3. Transformations

State each transformation and verify it is applied correctly and consistently.

- Growth rates: YoY vs MoM vs annualized MoM. For a level $X_t$, year-over-year growth is
  $$g_t = \frac{X_t}{X_{t-12}} - 1 \quad \text{(monthly data)},$$
  and annualizing a monthly rate is $(1+g_t^{\text{m}})^{12}-1$, not $12\,g_t^{\text{m}}$ except as an approximation.
- Rebasing: confirm the index equals 100 at the stated base date, and that all series share the same base.
- Percent vs percentage points: a move from 4% to 5% is 1 percentage point, or 25 percent in relative terms. Labels often conflate them.
- Real vs nominal: deflator source and base year stated.
- Currency conversion: spot vs period-average vs PPP, and the direction of the quote (USD per local vs local per USD flips the meaning of "depreciation").
- Aggregation: simple vs weighted averages; the weights and their vintage.
- Cumulative sums: starting point and whether flows are net or gross.
- Smoothing, detrending, z-scores: window, and whether the full sample was used (look-ahead).
- Joins and alignment: merges on date can silently drop or duplicate rows, and daily/monthly series joined without resampling create fake leads and lags.

## 4. Time and frequency

- Period-end vs period-average vs period-start dating.
- Mixed frequencies plotted as if comparable (daily market data with quarterly macro data).
- Business-day calendars, holidays, and time-zone cutoffs for market closes.
- Fiscal vs calendar year.
- Off-by-one period shifts after a lag or difference operation. A series shifted by one period is the classic cause of a mismatch that is small everywhere.

## 5. Macro-finance conventions (EM sovereign debt, capital flows, markets)

- **Spreads.** Which benchmark (US Treasury, swap curve), which index (EMBI Global Diversified vs EMBI Global vs CEMBI), stripped or blended, basis points. Spread to what, at what tenor.
- **Yields.** Local-currency vs hard-currency; yield to maturity vs coupon; constant-maturity vs index yield.
- **Breakevens.** Nominal minus real at the same tenor; the real leg may be a different instrument (for example, inflation-linked from a different country curve), and carry/indexation-lag effects matter at short tenors.
- **Capital flows.** Portfolio flows from EPFR vs IIF vs balance-of-payments data differ by construction. Check coverage (funds vs total), whether values are flows or stocks, and whether they are valuation-adjusted. State the sign convention (inflow positive?) and whether it is net or gross.
- **FX.** Quote direction, whether an index is trade-weighted or bilateral, nominal vs real effective exchange rate, and the sign of "depreciation."
- **Debt.** General vs central government; gross vs net; face vs market value; percent of GDP with which GDP vintage and which fiscal-year definition; whether guarantees and SOE debt are included.
- **Reserves.** Gross vs net, with or without gold, valuation effects.
- **Ratings and CDS.** Which agency scale and whether outlook is included; CDS tenor and currency.
- **Equity.** Total return vs price return; local-currency vs USD; which index.

## 6. Common AI-specific failure modes

Raise these as explicit suspicions, because they are how AI-built charts fail.

- **Numbers from memory.** The model "remembered" values rather than pulling them. Symptom: round numbers, smooth series, or values that match a famous episode too neatly. Treat as fabricated until traced to a pull.
- **Synthetic placeholder data.** A demo or simulated series left in the final chart. Look for generator code (`np.random`, `linspace`, hard-coded arrays) in the build.
- **Silent fallback.** The pull failed and the code substituted a default, an older cached file, or a different series without saying so.
- **Wrong series, right label.** The label says the concept; the ID pulls something adjacent.
- **Stale cache.** A previously saved CSV reused instead of a fresh pull, so the "latest" point is old.
- **Unit lost in a rename.** Columns renamed in cleaning, dropping the unit or multiplying by 100 twice.
- **Inconsistent edits across iterations.** The user asked for a tweak; the model regenerated the chart and changed data or parameters unrequested. Diff against the earlier version when one exists.
- **Overconfident source footnote.** A "Source:" line written from habit rather than from the pull actually performed.
- **Plausible-looking extrapolation.** Forecasts or filled values drawn in the same style as observed data.

## 7. Digitizing a PNG

Use only when no underlying data is available, and report the resulting values as Inferred, not Verified.

1. Load the image with PIL; identify the plot area.
2. Calibrate: find pixel coordinates of at least two labeled ticks per axis (more if the axis is log or non-linear) and fit $v = a\,p + b$ (or $v = a\,\ln p + b$ for log axes).
3. Isolate each series by color mask; for each target x position take the median y pixel of the matching mask pixels.
4. Convert to data units and report the tolerance, about one pixel of error converted to units.
5. Sanity-check the calibration by reading a labeled tick back out; if it does not round-trip, redo it.
6. Overlapping lines, anti-aliasing, and markers can corrupt the mask. If a series cannot be separated reliably, say so rather than guessing.

Compare digitized values against the independent source with a tolerance that is at least the digitization error; a "match" inside the noise only proves the shape is roughly right.
