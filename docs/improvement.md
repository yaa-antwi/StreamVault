# Improvement beyond the brief: Repeatable, cache-first data extraction

## The problem it solves

Adjoa currently repeats the licensing analysis quarterly. Repeatedly requesting the same movie information creates unnecessary API requests, makes the process dependent on external availability and makes it harder to identify which titles were successfully retrieved.

As the candidate list grows from 127 to approximately 500 titles, repeating these requests could make the process slower and less reliable.

## What I built

I built a cache-first extraction process that:

- Saves retrieved movie and credits responses as raw JSON files in `data/raw/`.
- Checks for an existing cached response before making another API request.
- Reuses cached responses when they are available.
- Records the outcome of each extraction, including `cached`, `downloaded`, `not_found` and `request_error`.
- Handles unsuccessful requests without treating them as successful downloads.

I also tested the extraction functions. Both movie extraction and credits extraction tests passed.

## What it is worth to StreamVault

- Adjoa can reuse previously retrieved data when repeating the quarterly analysis.
- The process avoids unnecessary requests for information already stored locally.
- Extraction outcomes are recorded, making unsuccessful retrievals easier to identify and investigate.
- Keeping the original responses allows the data preparation process to be repeated without relying on another API request for every title.
- The approach can support growth in the candidate list without requiring every existing title to be retrieved again.

## What it cost

- Development and testing time to build the extraction process.
- Local storage for the saved movie and credits responses.
- No additional paid data service was introduced by this improvement.