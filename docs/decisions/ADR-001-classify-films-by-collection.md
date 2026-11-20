# ADR-001: Classify films using collection membership

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering Consultant

## Context

StreamVault needs to compare franchise films with standalone films. The source data provides a collection field, but some films do not belong to a collection.

A consistent classification rule is necessary to avoid making subjective decisions about which films count as franchises.

## Decision

Classify a film as a franchise film when it has a non-empty collection ID and collection name. Classify a film with a blank or null collection value as standalone.

## Alternatives considered

### Alternative A: Classify films manually

- **How it would work:** Review each film and decide whether it belongs to a franchise.
- **Why it is attractive:** It allows individual judgement where collection information may be incomplete.
- **Why rejected:** Manual classification introduces subjective decisions and makes the analysis harder to repeat consistently.

### Alternative B: Use the source collection information

- **How it would work:** Use the collection information supplied for each film to determine its classification.
- **Why it is attractive:** It provides a consistent rule that can be applied to all candidate films.
- **Why rejected:** Not rejected. This is the accepted approach.

## Consequences

- **What this buys:** Consistent classification and repeatable franchise-versus-standalone comparisons.
- **What this costs:** The classification depends on the accuracy and completeness of the supplied collection information.
- **What it costs the client if I am wrong:** Incorrect collection information could place films in the wrong group and affect the comparison results.
- **What would make me revisit this:** Evidence that the collection information is incorrect or that the client defines franchise membership differently.

## What this survives

The rule can be applied consistently as the candidate list grows from 127 to approximately 500 titles. It does not require manual classification of every new film.