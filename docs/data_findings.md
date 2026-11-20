
# Data findings — StreamVault

## Summary

The original candidate list contains 127 entries. After accounting for six duplicate entries and excluding four invalid identifiers, 117 unique numeric TMDb IDs remained for extraction.

Of those 117 IDs:

- 112 were successfully retrieved.
- 5 returned `not_found`; credits extraction was therefore marked `not_attempted`.
- All 112 successfully retrieved titles proceeded to transformation.

The transformed movie table contains 112 titles. The five IDs that could not be found are excluded from the analysis. Their actual titles and potential effect on the licensing decision could not be established from the available data.

## Reconciliation

| Stage | Rows | Delta | Reason |
|---|---:|---:|---|
| Original candidate list | 127 | — | Original entries supplied for investigation |
| After duplicate reconciliation | 121 | -6 | Six repeated entries accounted for |
| Unique valid numeric IDs | 117 | -4 | Four invalid entries excluded |
| Extraction log | 117 | 0 | All 117 unique numeric IDs accounted for |
| Successfully retrieved | 112 | -5 | Five IDs returned `not_found` |
| Transformed movie table | 112 | 0 | All successfully retrieved titles proceeded to transformation |

## Findings, ranked by risk

### F-01: Five candidate IDs could not be retrieved — Severity: Medium

- **What it is:** Five numeric candidate IDs could not be found by TMDb. They were recorded as `not_found`, and credits extraction was marked `not_attempted`.
- **How I detected it:** Compared the unique numeric IDs in the original candidate list with the extraction log and checked the recorded movie and credits statuses.
- **Scale:** 5 of 117 unique numeric IDs (approximately 4.3%). The affected IDs are `8471293`, `9412887`, `8471294`, `9412888`, and `7733901`.
- **Effect on the client's number:** These five candidates are absent from the 112-title transformed dataset and therefore from the licensing analysis. Their titles and financial figures could not be verified. As a result, I cannot calculate their financial impact or establish whether including them would change the licensing shortlist.
- **What I did about it:** Excluded the five unretrievable records from the transformed analysis dataset and retained their `not_found` statuses in the extraction log.
- **Residual risk:** The five IDs may represent candidate titles that have not been evaluated. Their identities and relevance should be confirmed against the original candidate source before the licensing decision is finalised.

### F-02: Duplicate and invalid candidate identifiers — Severity: Low

- **What it is:** The original candidate list contains repeated IDs and entries that are not valid numeric TMDb identifiers.
- **How I detected it:** Profiled the original ID list for blank values, non-numeric entries, negative values, and repeated identifiers.
- **Scale:** Six duplicate entries and four invalid entries were accounted for, reducing the original 127 entries to 117 unique numeric IDs. The invalid entries were a blank value, `N/A`, `-1`, and the IMDb-style ID `tt0468569`.
- **Effect on the client's number:** Duplicate entries could cause the same title to be counted more than once. Invalid identifiers could not be used for the TMDb extraction process.
- **What I did about it:** Used unique numeric TMDb IDs for extraction and retained the original list for traceability.
- **Residual risk:** The source list should be checked to confirm that each candidate has the correct TMDb identifier and that the IMDb-style identifier is not an intended candidate that needs mapping.

## Looked wrong, is not wrong

| Apparent problem | Why it looks wrong | Why it is actually fine |
|---|---|---|
| The extraction log contains 117 IDs but the transformed movie table contains 112 rows | The row counts do not match | Five IDs were explicitly recorded as `not_found`; the remaining 112 were successfully retrieved and transformed |
| Some candidate IDs appear more than once | Repeated IDs could inflate the number of titles | Duplicate entries were accounted for before extraction, so each unique numeric ID was processed once |
| Credits status is `not_attempted` for five IDs | It may look like the credits extraction failed | The movie lookup returned `not_found`, so there was no movie record for which to retrieve credits |

## Could not verify

- The actual titles represented by the five `not_found` IDs.
- Whether those five records are valid candidate titles with incorrect IDs or titles that are unavailable from TMDb.
- The potential revenue, budget, or licensing impact of excluding those five candidates.
- Whether the IMDb-style identifier `tt0468569` was intended to represent a candidate title and, if so, its corresponding TMDb ID.
- Whether the six duplicate entries were accidental or intentional repetitions in the original candidate list.
