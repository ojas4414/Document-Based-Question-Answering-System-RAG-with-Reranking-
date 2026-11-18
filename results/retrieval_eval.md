# Retrieval evaluation

- Date: 2026-11-19
- Eval set: 25 questions from `eval/questions.jsonl` (documents: infosys-esg-report-2025-26.pdf)
- Chunks in index: 186
- Protocol: FAISS returns a pool of 20; (a) keeps FAISS order, (b) reranks the pool; both are cut to the top 5.
- A chunk counts as relevant if it contains the question's answer span (whitespace-normalised, case-sensitive). MRR@5 scores 0 when the gold chunk is outside the top 5.
- Command: `.venv/Scripts/python.exe eval.py --questions eval/questions.jsonl --pool 20 --cut 5 --out results/retrieval_eval.md`

## Results

| System | recall@1 | recall@3 | recall@5 | MRR@5 |
|---|---|---|---|---|
| (a) FAISS only | 0.400 | 0.680 | 0.720 | 0.537 |
| (b) FAISS + reranker | 0.360 | 0.640 | 0.680 | 0.483 |

Gold span anywhere in the FAISS pool of 20 (ceiling for any reranker): 0.840
Questions where the reranker changed the top-5 rank of the gold chunk: 4 of 25

## Per question (rank of first relevant chunk, '-' = not found)

| # | Question | Rank in pool | Rank FAISS | Rank reranked |
|---|---|---|---|---|
| 1 | Who are the main groups of people whose interests the company weighs when deciding which sustainability issues matter most? | 2 | 2 | 2 |
| 2 | For how many consecutive years has Infosys received the Leadership rating in the IiAS corporate governance assessment? | 2 | 2 | 4 |
| 3 | When was the second BioConserve Summit held and who was it organised with? | 2 | 2 | 2 |
| 4 | How does the company distinguish its promise to employees from its workplace culture? | - | - | - |
| 5 | By what percentage has Infosys reduced its absolute Scope 3 emissions? | 3 | 3 | 3 |
| 6 | What was the survey about home-office power use meant to measure? | 2 | 2 | 3 |
| 7 | Which areas does the company's sustainability consulting business cover for clients? | 1 | 1 | 1 |
| 8 | How much money did the cloud building-operations platform save the real estate client? | 1 | 1 | 1 |
| 9 | By how much did the lake restoration work grow total water storage? | 1 | 1 | 1 |
| 10 | Which ISO standard is the environmental management system aligned with? | 2 | 2 | 2 |
| 11 | Which minister did the Infosys Springboard PM Internship interns meet at Hampi? | 11 | - | - |
| 12 | How many expectant mothers had been checked under the maternal health program by late 2025? | 1 | 1 | 1 |
| 13 | Which awards for young people in the UK capital did the company sponsor? | 1 | 1 | 1 |
| 14 | How many participants took part in the CIO Charity Run and Bike 2025 and how much did they raise? | 1 | 1 | 1 |
| 15 | How many female employees does the company have? | 7 | - | - |
| 16 | Where did Infosys restart Mitti Café? | - | - | - |
| 17 | Over what time frame does the World Economic Forum expect a large share of current job skills to become outdated? | - | - | - |
| 18 | What is the minimum office attendance required under the hybrid work policy? | 14 | - | - |
| 19 | Which Infosys center won Best Development Center - Small at the Awards for Excellence? | 3 | 3 | 3 |
| 20 | What commitment does the 'Respecting Each Other' tenet of the Code of Conduct articulate? | 4 | 4 | - |
| 21 | Who became vice chair of the board in 2026? | 1 | 1 | 1 |
| 22 | After a restatement of financial results, can executive pay be clawed back even if the executive did nothing wrong? | 1 | 1 | 1 |
| 23 | How many verticals and countries does the vertical regulatory compliance program cover? | 1 | 1 | 1 |
| 24 | How many new workers are expected to compete for jobs in emerging economies over the next decade? | 1 | 1 | 3 |
| 25 | What was the average total cost of a data breach in India in 2025? | - | - | - |
