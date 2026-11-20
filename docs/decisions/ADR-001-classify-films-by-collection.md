# ADR-001: Classify films using collection membership

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering Consultant

## Context

StreamVault needs to compare the financial performance of franchise films against standalone films. The source data provides a `belongs_to_collection` field, which identifies films associated with a collection. Films without a collection are treated as standalone.

The classification affects the size and composition of both groups. An incorrect rule could move films between the groups, changing their median revenue-to-budget multiples and potentially influencing which titles StreamVault prioritises for licensing discussions.

## Decision

Classify a film as a franchise film when its `belongs_to_collection` field contains a collection object. Classify it as standalone when the field is empty or null. Apply this rule consistently to every candidate film rather than making individual judgements based on film titles.

## Alternatives considered

### Alternative A: Classify films manually using their titles

- **How it would work:** Review film titles and use knowledge of their sequels, spin-offs or shared stories to decide whether they belong to a franchise.
- **Why it is attractive:** It might identify relationships that are not properly represented in the source collection field.
- **Why rejected:** A film's title does not reliably establish its collection membership. Manual decisions could classify similar cases differently, making the comparison subjective and difficult to reproduce.

### Alternative B: Require both a collection ID and collection name

- **How it would work:** Classify a film as a franchise film only when both fields contain values.
- **Why it is attractive:** It appears to provide two pieces of information to confirm collection membership.
- **Why rejected:** The tutor's classification rule is based on whether `belongs_to_collection` is empty or populated. Requiring both an ID and name introduces an additional condition that could incorrectly classify a film with a collection object but an incomplete name as standalone.

### Alternative C: Use the `belongs_to_collection` field

- **How it would work:** Treat a populated collection object as franchise membership and an empty or null value as standalone.
- **Why it is attractive:** It uses the source's explicit collection relationship and gives every film the same classification test.
- **Why rejected:** Not rejected. This is the accepted approach.

## Consequences

- **What this buys:** A repeatable classification rule for the franchise-versus-standalone comparison. In the current analysis, it produces 96 franchise films and 16 standalone films across all years, and 63 franchise films and 8 standalone films from 2000 onward.
- **What this costs:** The analysis depends on the source correctly recording collection membership. A missing or incorrect collection relationship could place a film in the wrong group.
- **What it costs the client if I am wrong:** Misclassified films could change the group medians and distort the comparison used to prioritise licensing candidates.
- **What would make me revisit this:** Evidence that the source collection relationships are incomplete or incorrect, or a revised definition of franchise membership from StreamVault.

## What this survives

The same rule can be applied when the candidate list grows from 127 to approximately 500 titles. It avoids introducing manual classification decisions each time new films are added, while keeping the basis of the comparison consistent.