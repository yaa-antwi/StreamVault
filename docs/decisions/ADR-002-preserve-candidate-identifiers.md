# ADR-002: Preserve and account for every candidate ID

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering Consultant

## Context

The original candidate list contains duplicate entries, invalid identifiers and IDs that could not be retrieved.

Removing these records without keeping track of them would make it difficult to explain why the final analysis contains fewer titles than the original list.

## Decision

Preserve the original candidate list and record the outcome of each identifier during extraction. Use unique valid numeric IDs for retrieval, while keeping duplicates, invalid entries and unsuccessful retrievals traceable.

## Alternatives considered

### Alternative A: Remove problematic IDs from the original list

- **How it would work:** Delete duplicates, invalid entries and IDs that cannot be retrieved.
- **Why it is attractive:** It produces a cleaner list for extraction and analysis.
- **Why rejected:** It removes the evidence needed to explain what happened to the original candidates.

### Alternative B: Preserve the original list and record each outcome

- **How it would work:** Keep the original entries, identify unique valid IDs and record whether each was downloaded, reused from cache or not found.
- **Why it is attractive:** It makes the extraction process traceable and allows excluded candidates to be investigated.
- **Why rejected:** Not rejected. This is the accepted approach.

## Consequences

- **What this buys:** A clear record of how the original 127 entries became 117 unique numeric IDs and how 112 titles were successfully retrieved.
- **What this costs:** Additional work to profile identifiers, maintain an extraction log and investigate unsuccessful retrievals.
- **What it costs the client if I am wrong:** Incorrect exclusions could leave relevant titles out of the licensing analysis without the client knowing.
- **What would make me revisit this:** A change in the candidate source format or evidence that the current identifier rules are excluding valid titles.

## What this survives

The approach can handle a larger candidate list without losing the ability to trace each original entry to its extraction outcome.