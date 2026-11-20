# ADR-001: Classify films using collection membership

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering Consultant

## Context

StreamVault needs to compare franchise and standalone film performance. The source data provides a `belongs_to_collection` field that identifies collection membership. The classification affects group sizes and financial comparisons.

## Decision

Classify a film as franchise when `belongs_to_collection` contains a collection object. Classify it as standalone when the field is empty or null. Apply this rule consistently to all candidate films.

## Alternatives considered

### Alternative A: Classify films manually using their titles

- **How it would work:** Use film titles and knowledge of sequels or shared stories to assign groups.
- **Why it is attractive:** It might identify relationships missing from the source data.
- **Why rejected:** Title-based decisions are subjective and difficult to reproduce consistently.

### Alternative B: Require both a collection ID and name

- **How it would work:** Classify a film as franchise only when both fields are populated.
- **Why it is attractive:** It appears to provide two checks for collection membership.
- **Why rejected:** It adds a condition beyond the agreed classification rule and could misclassify incomplete collection records.

### Alternative C: Use the `belongs_to_collection` field

- **How it would work:** Treat a populated collection object as franchise membership and an empty or null field as standalone.
- **Why it is attractive:** It uses the source's explicit collection relationship and applies one consistent test.
- **Why rejected:** Not rejected. This is the accepted approach.

## Consequences

- **What this buys:** A repeatable comparison. The analysis contains 96 franchise and 16 standalone films across all years; from 2000 onward, it contains 63 franchise and 8 standalone films.
- **What this costs:** The classification depends on the source recording collection membership correctly.
- **What it costs the client if I am wrong:** Misclassified films could change group medians and distort licensing priorities.
- **What would make me revisit this:** Evidence of incomplete or incorrect collection relationships, or a revised definition of franchise membership from StreamVault.

## What this survives

The same rule can be applied as the candidate list grows from 127 to approximately 500 titles. It avoids repeated manual decisions and keeps future comparisons consistent.