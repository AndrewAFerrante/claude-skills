#!/usr/bin/env python3
"""Generate a reproducible, risk-based sample plan for auditing a charted series.

Input: a CSV with a date column and one or more numeric series columns (the
data actually plotted, in wide form: one column per series).

Output: a CSV of points to verify against an independent source, with the tier
and reason each point was chosen, plus a short structural-check report on stdout.

Tiers
  1  always check: first, last, max, min, largest absolute jump, largest
     z-score outlier, and any user-supplied labeled dates
  2  seeded random sample, stratified over time, >= max(8, frac * n) per series
  3  structural checks run on every row (reported, not sampled)

Usage
  python sample_plan.py data.csv --date-col date --out plan.csv \
      [--frac 0.10] [--seed 42] [--labeled 2020-03-31,2022-02-28]
"""
import argparse
import sys

import numpy as np
import pandas as pd


def structural_checks(df, date_col, series_cols):
    """Tier 3: exhaustive, cheap checks. Returns a list of (severity, message)."""
    issues = []
    d = df[date_col]
    if d.isna().any():
        issues.append(("Major", f"{int(d.isna().sum())} unparseable/missing dates"))
    if d.duplicated().any():
        issues.append(("Major", f"{int(d.duplicated().sum())} duplicate dates"))
    if not d.is_monotonic_increasing:
        issues.append(("Major", "dates are not sorted ascending"))

    # Gap detection: flag spacings much larger than the typical spacing.
    diffs = d.sort_values().diff().dropna()
    if len(diffs) > 2:
        typical = diffs.median()
        big = diffs[diffs > 3 * typical]
        if len(big):
            where = ", ".join(str(x.date()) for x in d.loc[big.index].head(5))
            issues.append(("Minor", f"{len(big)} gaps > 3x typical spacing ({typical}); e.g. before {where}"))

    n = len(df)
    for c in series_cols:
        s = df[c]
        miss = int(s.isna().sum())
        if miss:
            issues.append(("Minor", f"{c}: {miss} of {n} values missing"))
        zeros = int((s == 0).sum())
        if zeros and zeros / max(n, 1) > 0.02:
            issues.append(("Minor", f"{c}: {zeros} exact zeros (missing data coded as 0?)"))
        # Stuck/flat runs often mean forward-filled or cached data.
        run = (s.diff() == 0).astype(int)
        longest = run.groupby((run == 0).cumsum()).sum().max()
        if longest >= 5:
            issues.append(("Minor", f"{c}: flat run of {int(longest)} identical consecutive values (stale/ffill?)"))
        # Suspiciously round values suggest remembered, not pulled, numbers.
        nn = s.dropna()
        if len(nn) >= 10:
            round_share = np.mean(np.isclose(nn, np.round(nn, 0)))
            if round_share > 0.6 and nn.abs().max() < 1e6 and nn.nunique() > 5:
                issues.append(("Minor", f"{c}: {round_share:.0%} of values are whole numbers (remembered/approximated data?)"))
    return issues


def tier1_points(df, date_col, s_name, labeled):
    s = df[["__idx__", date_col, s_name]].dropna(subset=[s_name])
    out = []
    if s.empty:
        return out

    def add(row_idx, reason):
        out.append((int(row_idx), reason))

    add(s["__idx__"].iloc[0], "first observation")
    add(s["__idx__"].iloc[-1], "latest observation (staleness check)")
    add(s.loc[s[s_name].idxmax(), "__idx__"], "series maximum")
    add(s.loc[s[s_name].idxmin(), "__idx__"], "series minimum")

    jumps = s[s_name].diff().abs()
    if jumps.notna().any():
        add(s.loc[jumps.idxmax(), "__idx__"], "largest one-period jump")

    sd = s[s_name].std()
    if sd and not np.isnan(sd):
        z = ((s[s_name] - s[s_name].mean()) / sd).abs()
        for i in z.sort_values(ascending=False).head(2).index:
            if z.loc[i] > 2.5:
                add(s.loc[i, "__idx__"], f"outlier (|z|={z.loc[i]:.1f})")

    for ld in labeled:
        # nearest observation to each labeled/annotated date
        j = (s[date_col] - ld).abs().idxmin()
        add(s.loc[j, "__idx__"], f"labeled/annotated date {ld.date()}")
    return out


def tier2_points(df, s_name, exclude_idx, frac, seed):
    s = df.dropna(subset=[s_name])
    pool = s[~s["__idx__"].isin(exclude_idx)]
    if pool.empty:
        return []
    n_total = len(s)
    k = int(min(len(pool), max(8, np.ceil(frac * n_total))))
    rng = np.random.default_rng(seed)
    # Stratify over time: split pool into k contiguous bins, draw one from each.
    idxs = pool["__idx__"].to_numpy()
    bins = np.array_split(idxs, k)
    picks = [int(rng.choice(b)) for b in bins if len(b)]
    return [(i, "stratified random sample") for i in picks]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--date-col", default="date")
    ap.add_argument("--out", default="sample_plan.csv")
    ap.add_argument("--frac", type=float, default=0.10, help="Tier 2 fraction per series (default 0.10)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--labeled", default="", help="comma-separated annotated/cited dates")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if args.date_col not in df.columns:
        sys.exit(f"date column '{args.date_col}' not found; columns: {list(df.columns)}")
    df[args.date_col] = pd.to_datetime(df[args.date_col], errors="coerce")
    series_cols = [c for c in df.columns if c != args.date_col and pd.api.types.is_numeric_dtype(df[c])]
    if not series_cols:
        sys.exit("no numeric series columns found")
    df = df.reset_index(drop=True)

    # Tier 3 runs on the file as given (so ordering/duplicate problems are caught),
    # then we sort by date so "first"/"latest" mean earliest/latest date, not row order.
    issues = structural_checks(df, args.date_col, series_cols)
    df = df.dropna(subset=[args.date_col]).sort_values(args.date_col, kind="stable").reset_index(drop=True)
    df["__idx__"] = df.index

    labeled = [pd.Timestamp(x.strip()) for x in args.labeled.split(",") if x.strip()]

    rows = []
    for c in series_cols:
        t1 = tier1_points(df, args.date_col, c, labeled)
        t1_idx = {i for i, _ in t1}
        t2 = tier2_points(df, c, t1_idx, args.frac, args.seed)
        seen = {}
        for tier, pts in ((1, t1), (2, t2)):
            for i, reason in pts:
                if i in seen:  # merge reasons if a point is picked twice
                    seen[i]["reason"] += f"; {reason}"
                    continue
                seen[i] = {
                    "series": c,
                    "tier": tier,
                    "date": df.loc[i, args.date_col],
                    "plotted_value": df.loc[i, c],
                    "reason": reason,
                    "independent_source_value": "",
                    "abs_diff": "",
                    "status": "",
                }
        rows.extend(seen.values())

    plan = pd.DataFrame(rows).sort_values(["series", "tier", "date"])
    plan.to_csv(args.out, index=False)

    print(f"Sample plan written to {args.out} (seed={args.seed}, tier-2 frac={args.frac})")
    print("\nPoints per series (tier 1 / tier 2 / total of n):")
    for c in series_cols:
        sub = plan[plan.series == c]
        n = int(df[c].notna().sum())
        print(f"  {c}: {int((sub.tier==1).sum())} / {int((sub.tier==2).sum())} / {len(sub)} of {n}")

    print("\nTier 3 structural checks (all rows):")
    if not issues:
        print("  none flagged")
    for sev, msg in issues:
        print(f"  [{sev}] {msg}")

    print("\nFill independent_source_value and status (match / mismatch) in the plan, then apply the escalation rule:")
    print("  any mismatch -> double that series' sample; second mismatch -> compare the full series.")


if __name__ == "__main__":
    main()
