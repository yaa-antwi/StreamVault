# Data findings — StreamVault

## Summary

The original candidate list contained 127 entries. After accounting for six duplicates and four invalid identifiers, 117 unique numeric TMDb IDs remained.

- 112 titles were successfully retrieved and transformed.
- 5 IDs returned `not_found`; credits extraction was marked `not_attempted`.
- The five unretrieved titles are excluded from the analysis. Their identities and potential effect on the licensing decision remain unknown.

## Reconciliation

| Stage | Rows | Delta | Reason |
|---|---:|---:|---|
| Original candidate list | 127 | — | Original entries |
| After duplicate reconciliation | 121 | -6 | Six duplicate entries |
| Unique valid numeric IDs | 117 | -4 | Four invalid entries |
| Extraction log | 117 | 0 | All unique numeric IDs accounted for |
| Successfully retrieved | 112 | -5 | Five IDs returned `not_found` |
| Transformed movie table | 112 | 0 | All retrieved titles transformed |

## Findings, ranked by risk

### F-01: Five candidate IDs could not be retrieved — Severity: Medium

- **What it is:** Five numeric IDs returned `not_found`; credits extraction was therefore `not_attempted`.
- **How I detected it:** Compared the original unique numeric IDs with the extraction log and checked retrieval statuses.
- **Scale:** 5 of 117 IDs (4.3%): `8471293`, `9412887`, `8471294`, `9412888`, `7733901`.
- **Effect on the client's number:** These titles are absent from the 112-title analysis. Their financial impact and effect on the licensing shortlist cannot be established.
- **What I did about it:** Excluded them from the transformed dataset and retained their statuses in the extraction log.
- **Residual risk:** The five candidates remain unevaluated. Their identities should be confirmed before the licensing decision.

### F-02: Duplicate and invalid candidate identifiers — Severity: Low

- **What it is:** The source list contains repeated entries and identifiers unsuitable for TMDb extraction.
- **How I detected it:** Checked for duplicates, blanks, non-numeric values and invalid identifier formats.
- **Scale:** Six duplicates and four invalid entries. The invalid entries were a blank, `N/A`, `-1` and IMDb-style ID `tt0468569`.
- **Effect on the client's number:** Duplicates could inflate title counts; invalid identifiers cannot be used for the extraction.
- **What I did about it:** Used unique numeric TMDb IDs for extraction and retained the original list for traceability.
- **Residual risk:** Confirm whether the IMDb-style ID represents an intended candidate and whether the duplicates were intentional.

## Looked wrong, is not wrong

| Apparent problem | Why it looks wrong | Why it is actually fine |
|---|---|---|
| Extraction log has 117 IDs but the movie table has 112 rows | Row counts differ | Five IDs returned `not_found`; the other 112 were transformed |
| Candidate IDs appear more than once | Repeated IDs could inflate title counts | Duplicates were accounted for before extraction |
| Five credits statuses are `not_attempted` | Credits may appear to have failed | No movie record was found for those IDs, so credits were not requested |

## Could not verify

- The titles represented by the five `not_found` IDs.
- Whether those IDs are incorrect or the titles are unavailable from TMDb.
- The financial impact of excluding those five candidates.
- Whether `tt0468569` represents an intended candidate requiring TMDb ID mapping.
- Whether the six duplicate entries were accidental or intentional.