# Memo to Kwame

**From:** Data Engineering Consultant  
**Date:** 20 November 2026  
**Subject:** Film licensing analysis — findings and recommendation

## What I found

Franchise films had higher median box-office-to-production-budget figures than standalone films in both periods:

- **All years:** 5.62x for franchises versus 3.84x for standalone films.
- **2000 onward:** 5.05x versus 3.84x.

The difference remains in the more recent period, but the standalone comparison contains only eight films. Older films also produced some of the highest figures, and inflation has not been accounted for.

Three collections stood out: The Lord of the Rings (11.73x across 3 films), Ice Age (8.26x across 3) and The Avengers (6.87x across 4). These are median results from the individual films, not returns for buying the complete collections.

Among standalone films released from 2000 onward, Spirited Away (14.47x), Inception (5.24x), Interstellar (4.52x), Memento (4.45x) and The Departed (3.24x) had the highest figures.

Steven Spielberg appeared on 8 candidate films. Daniel Radcliffe, Emma Watson, Harrison Ford and Rupert Grint each appeared among the top five billed cast members on 8 films. These counts do not prove that a director or actor caused stronger financial results.

## What I built

| What you asked for | Status | Evidence |
|---|---|---|
| Review and reconcile the candidate list | Complete | 127 entries reduced to 117 unique valid IDs after removing 6 duplicates and 4 invalid entries. |
| Retrieve and prepare the film information | Complete with gaps | 112 films retrieved; 5 IDs could not be found and were excluded. |
| Compare franchise and standalone films across two periods | Complete | Comparisons completed for all years and 2000 onward. |
| Examine leading films, collections and people | Complete | Film rankings, collection comparisons, director and cast counts produced. |
| Check the data and the work | Passed | 29 automated tests and 12 data checks passed. |

## What I recommend

Prioritise The Lord of the Rings, Ice Age and The Avengers collections, together with the five leading standalone films, for further licensing investigation.

Before committing the $14 million budget, obtain the actual licensing prices, contract terms and complete lists of films in each offer. Compare the full cost of each deal with its expected value to StreamVault. Investigate the five missing films before treating the candidate list as complete.

## What I could not stand behind

The information available does not include licensing prices, contract terms, marketing and distribution costs, or expected streaming revenue. Box-office revenue compared with production budgets is therefore not profit or evidence of what StreamVault would earn from a licence.

The collection figures cover only the films retrieved for this analysis, not necessarily every film in a studio's offer. Historical figures are also not adjusted for inflation.

**The findings identify films worth investigating; they do not establish which deals are profitable or justify spending the $14 million.**