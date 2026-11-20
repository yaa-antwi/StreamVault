
# Memo to Kwame

**From:** Data Engineering Consultant  
**Date:** 20 November 2026  
**Subject:** Findings from the film licensing analysis

## What I found

Franchise films had higher median historical box-office revenue-to-budget multiples than standalone films in both comparison periods.

- **All years:** Franchise films recorded 5.62x compared with 3.84x for standalone films. This comparison includes 96 franchise films and 16 standalone films.
- **2000 onward:** Franchise films recorded 5.05x compared with 3.84x for standalone films. This comparison includes 63 franchise films and only 8 standalone films.

The post-2000 standalone result should be treated cautiously because it is based on a much smaller group. These multiples compare historical box-office revenue with production budgets. They do not measure profit or the return StreamVault would earn from licensing the films.

The collection analysis identified the following strong historical results:

- The Lord of the Rings: 11.73x median title multiple across 3 candidate films.
- Ice Age: 8.26x across 3 candidate films.
- Avengers: 6.87x across 4 candidate films.

Among post-2000 standalone candidates, the five highest-ranked titles were Spirited Away (14.47x), Inception (5.24x), Interstellar (4.52x), Memento (4.45x) and The Departed (3.24x).

The people analysis also identified recurring names in the candidate films. Steven Spielberg appeared as director on 8 films. Daniel Radcliffe, Emma Watson, Harrison Ford and Rupert Grint each appeared among the top five billed cast members on 8 films. These counts describe the candidate list; they do not establish that a particular director or actor caused stronger financial performance.

Of the 117 unique valid candidate IDs, 112 titles were retrieved and analysed. Five returned `not_found` and remain outside the analysis. Their titles and possible effect on the shortlist could not be established.

## What I built

| What you asked for | Status | Evidence |
|---|---|---|
| Review the candidate list | Complete | Reconciled 127 original entries into 117 unique valid numeric IDs after accounting for 6 duplicate entries and 4 invalid entries |
| Retrieve and prepare title information | Complete, with exclusions | 112 titles retrieved and transformed; 5 IDs recorded as `not_found` |
| Compare franchise and standalone films | Complete | Median revenue-to-budget multiples calculated for all years and from 2000 onward, with group sizes reported |
| Examine individual titles and collections | Complete | Individual title rankings and collection summaries produced |
| Examine directors and lead cast | Complete | Director counts and top-five-billed cast counts produced |
| Check the prepared information | Complete | 27 automated tests and 13 data checks passed |

## What I recommend

Use the results to prioritise The Lord of the Rings, Ice Age and Avengers collections, alongside the five highest-ranked post-2000 standalone titles, for further licensing investigation. These are candidates for discussion, not confirmed purchases.

Do not approve the $14 million spend based on historical box-office performance alone. Before making the decision, obtain the proposed licensing prices, contract terms and complete list of films in each bundle. Compare the full bundle cost with its expected value to StreamVault. Also confirm the five unretrieved candidate titles and assess whether including them could change the shortlist.

## What I could not stand behind

I could not establish which titles will be profitable for StreamVault, whether the proposed $14 million represents good value, or whether any particular bundle should be purchased. The analysis contains historical film budgets and box-office revenue, but not licensing prices, contract terms or expected streaming revenue.

The collection summaries cover only the candidate films retrieved for this analysis. They do not establish that every film in a proposed bundle was included. The five unretrieved candidates also remain unidentified, so their effect on the final shortlist is unknown.
