# ADR-003: Keep zero revenue separate from unavailable revenue

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering Consultant

## Context

The financial analysis uses movie budgets and box-office revenue. A recorded revenue of zero and a missing revenue value represent different situations.

Treating both as zero would make unavailable financial information appear to be a confirmed zero value and could distort comparisons.

## Decision

Preserve recorded zero revenue as zero and represent unavailable revenue as missing. Do not replace missing revenue values with zero during transformation or analysis.

## Alternatives considered

### Alternative A: Replace missing revenue with zero

- **How it would work:** Fill every missing revenue value with zero before analysis.
- **Why it is attractive:** It produces a complete numeric column and makes calculations appear simpler.
- **Why rejected:** It treats unavailable information as confirmed zero revenue and can distort averages and other financial comparisons.

### Alternative B: Preserve zero and missing values separately

- **How it would work:** Keep recorded zero values as zero and retain unavailable values as missing.
- **Why it is attractive:** It preserves the distinction between what the source reports and what it does not provide.
- **Why rejected:** Not rejected. This is the accepted approach.

## Consequences

- **What this buys:** More accurate financial summaries and a clear record of which revenue values are available.
- **What this costs:** Analysis must account for missing values rather than treating every record as a complete financial observation.
- **What it costs the client if I am wrong:** Missing revenue could be mistaken for zero, leading to misleading financial comparisons and potentially poor licensing decisions.
- **What would make me revisit this:** A change in the source data that provides a reliable way to distinguish confirmed zero revenue from unavailable revenue.

## What this survives

The distinction remains important as more titles are added. New records can contain missing financial information without silently changing the meaning of the existing analysis.