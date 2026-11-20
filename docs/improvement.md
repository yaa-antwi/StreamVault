# Improvement beyond the brief: Quarterly comparison of licensing candidates

## The problem it solves

Adjoa currently reruns the licensing analysis each quarter. The candidate list is expected to grow from 127 to approximately 500 titles next year.

Running the analysis again will show the latest results, but it will not automatically explain what has changed since the previous quarter. Adjoa would have to compare the previous and current candidate lists and results herself.

This makes it harder to identify newly added titles, titles removed from consideration, resolved retrieval problems and changes in licensing rankings. It also means StreamVault could miss important changes between quarterly reviews.

## What I built

I propose extending the existing analysis to preserve each quarterly result and compare it with the previous run.

The comparison will show:

- New titles added to the candidate list.
- Titles removed from the candidate list.
- Titles that were previously unavailable but have now been retrieved.
- Titles whose retrieval problems remain unresolved.
- Changes in franchise and standalone rankings.
- Changes in the financial performance figures used to assess the candidates.

Each quarterly run will have its own saved results so that a new analysis does not overwrite the previous quarter's evidence.

## What it is worth to StreamVault

This gives Adjoa a clear record of how the candidate list and licensing findings change over time.

Instead of reviewing each quarter's results in isolation, she can identify which new titles deserve attention, whether previously missing titles affect the findings and whether the licensing priorities have changed.

For Kwame, this provides a clearer basis for discussing changes in the licensing shortlist. It also makes the quarterly review more consistent as the candidate list grows from 127 to approximately 500 titles.

## What it cost

The improvement requires additional development time to save quarterly results, compare them and produce a clear report of the changes.

It will also require storage for previous quarterly results and time to check that comparisons are accurate when titles are added, removed or successfully retrieved after an earlier failure.

The existing extraction, validation, transformation and analysis pipeline can be reused, limiting the amount of new development required.