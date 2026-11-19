## Five questions to keep open while you read
|Details|
|---|
|What counts as a franchise entry, and how would you determine that from an API response rather than from your own knowledge of films?|
|A request fails, or an identifier returns nothing. What does your pipeline do — and how does the reader of your diagnosis find out it happened?|
|A film has four genres and two production companies. What is one row in your table, and what does that choice do to every average you compute afterwards?|
|A revenue figure of zero: is that a missing value or a real one? How would you tell, and what does each answer do to the comparison?|
|If the all-years answer and the 2000-onward answer disagree, what do you tell Kwame to do?|
|Not turning blanks into missing values|


**Read the constraints list again after the Learning Path’s topic on vectorisation, and again after the topic on proving the join. Constraints that look like trivia now will look like instructions then.**

The complete working sequence
This is the order TO follow .
1. Stage 1 — Preserve and investigate the original candidate list
   Profiling completed
   We have already profiled the 127 original entries.
   
   Findings recorded:
   - 1 blank ID
   - 1 N/A
   - 1 suspicious -1
   - 1 IMDb-format ID
   - 117 unique numeric IDs
   We will preserve the original CSV and use the findings in Deliverable 1.
   
   Output: profiling notebook and candidate-list findings.
2. Stage 2 — Build TMDb extraction
   Current stage
   We have successfully tested one live API request.
   
   Next:
   - Extract the usable numeric IDs.
   - Retrieve movie details.
   - Retrieve cast and crew credits.
   - Record successful and unsuccessful requests.
   - Save the raw API responses locally.
   - Avoid repeating API calls when cached responses are available.
   Output: extraction scripts and raw cached responses.
3. Stage 3 — Validate the extracted data
   
   Check:
   - Did TMDb return a response for each submitted ID?
   - Does the returned ID match the requested ID?
   - Are required fields present?
   - Are the returned records actually movies?
   - Are there failed requests, missing records or unexpected responses?
   We must account for every original candidate, not just the successful API responses.
   
   Output: extraction results and validation report.
4. Stage 4 — Transform the data
   
   We will:
   - Flatten the nested movie information.
   - Extract relevant cast and crew details.
   - Join movie details with credits using the TMDb ID.
   - Check that the joins have not duplicated or lost films.
   - Prepare a clean analysis dataset.
   Output: structured movie and credits datasets.
5. Stage 5 — Run data-quality checks
   
   Check:
   - Duplicate films.
   - Missing financial information.
   - Missing release dates.
   - Inconsistent or unusable records.
   - Whether all candidates have been accounted for.
   - Whether the data is sufficient for each analysis.
   We will distinguish between a film that is unsuitable for one particular calculation and a film that must be excluded entirely.
   
   Output: quality-check results and final candidate reconciliation.
6. Stage 6 — Perform the licensing analysis
   
   This is where we answer the actual business questions.
   
   We will:
   - Analyse both required time periods.
   - Compare standalone films with franchise opportunities.
   - Identify relevant cast and crew patterns.
   - Examine financial and audience evidence.
   - Evaluate the franchise bundles against the standalone options.
   - Consider the $14 million budget.
   We will use Pandas and NumPy where appropriate, including vectorised calculations rather than unnecessarily processing rows one at a time.
   
   Output: analysis tables, comparisons and evidence for the recommendation.
7. Stage 7 — Measure performance and reproducibility
   
   We will test the complete workflow from a clean start.
   
   Specifically:
   - Can it run from top to bottom?
   - Does it reuse cached API responses?
   - Does it avoid unnecessary API calls?
   - Can another person run it after cloning the repository?
   - Are dependencies documented in requirements.txt?
   - Is the API key kept out of Git?
   - Have we measured and recorded runtime?
   Output: reproducible project, runtime evidence and setup instructions.
8. Stage 8 — Complete the decision notes
   
   Document:
   - What we decided.
   - Why we decided it.
   - Alternatives considered.
   - Assumptions and limitations.
   - What could go wrong.
   - The financial or business cost if our assumptions are wrong.
   - Whether the approach will work when the list grows from 127 to approximately 500 films.
   Output: decision notes.
9. Stage 9 — Write the one-page client memo
   
   Present:
   - The recommendation.
   - The strongest supporting evidence.
   - The main financial and licensing considerations.
   - Important uncertainties.
   - The implications for StreamVault's decision.
   The memo must be understandable to a non-technical decision-maker.
   
   Output: one-page client memo.
10. Stage 10 — Complete the additional improvement
    
    Choose one improvement that is justified by what we discover during the project.
    
    It must solve a real problem, not simply add technology for its own sake.
    
    Output: implemented improvement and explanation of its value.
11. Stage 11 — Final submission check
    
    Check all five deliverables against the brief.
    
    Confirm that:
    - The numbers agree across the documents.
    - Every candidate is accounted for.
    - The analysis can be reproduced.
    - The recommendation follows from the evidence.
    - No claims are stronger than the data supports.
    - All required files are present and correctly named.
    Output: completed submission.