# Memo to Kwame

**From:** Data Engineering Consultant  
**Date:** 20 November 2026  
**Subject:** Findings from the film licensing analysis

## What I found

Franchise films had higher median historical revenue-to-budget multiples than standalone films:

- **All years:** 5.62x vs 3.84x (96 franchise, 16 standalone).
- **2000 onward:** 5.05x vs 3.84x (63 franchise, 8 standalone).

The post-2000 standalone result should be treated cautiously because it covers only eight films. These multiples compare box-office revenue with production budgets; they do not measure profit or StreamVault's licensing returns.

**Strong collection results:**
- The Lord of the Rings: 11.73x (3 films).
- Ice Age: 8.26x (3 films).
- Avengers: 6.87x (4 films).

**Top post-2000 standalone titles:** Spirited Away (14.47x), Inception (5.24x), Interstellar (4.52x), Memento (4.45x) and The Departed (3.24x).

Steven Spielberg directed 8 candidate films. Daniel Radcliffe, Emma Watson, Harrison Ford and Rupert Grint each appeared among the top five billed cast members on 8 films. These counts do not establish that their involvement caused stronger financial performance.

Of 117 unique valid candidate IDs, 112 titles were retrieved. Five returned `not_found` and remain outside the analysis.

## What I built

| What you asked for | Status | Evidence |
|---|---|---|
| Review the candidate list | Complete | 127 entries reconciled into 117 unique valid IDs, 6 duplicates and 4 invalid entries |
| Retrieve and prepare title information | Complete, with exclusions | 112 titles retrieved; 5 IDs not found |
| Compare franchise and standalone films | Complete | Median multiples calculated for both periods, with group sizes |
| Examine titles and collections | Complete | Title rankings and collection summaries produced |
| Examine directors and lead cast | Complete | Director and top-five-billed cast counts produced |
| Check the prepared information | Complete | 29 automated tests and 12 data checks passed |

## What I recommend

Prioritise The Lord of the Rings, Ice Age and Avengers collections, alongside the five leading post-2000 standalone titles, for further licensing investigation. These are candidates for discussion, not confirmed purchases.

Do not approve the $14 million spend based on box-office results alone. Obtain licensing prices, contract terms and complete bundle lists, then compare the full costs with expected value. Also identify the five unretrieved titles and assess their effect on the shortlist.

## What I could not stand behind

This analysis cannot establish which titles will be profitable or whether the $14 million spend represents good value. Licensing prices, contract terms and expected streaming revenue were not available.

Collection results cover only the retrieved candidate films, not necessarily every film in a proposed bundle. The five unretrieved titles also remain unidentified.