# Using Personal Research AI

This guide covers the current Streamlit app from startup through literature discovery and review. The app retrieves scholarly metadata and abstracts. It does not retrieve full text or produce a complete literature synthesis.

## Start the app

In PowerShell, open the project directory and create an environment the first time you set it up:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then start the app:

```powershell
python -m streamlit run app.py
```

Open the local address Streamlit prints in the terminal. Keep that terminal open while using the app. Stop the app with Ctrl+C in that terminal.

If `py -3.14` is unavailable, use the Python 3.14 executable installed on your computer to create the environment. The README has the verified workspace path as an example. Use the interpreter and environment selected for your own machine.

## Search for papers

1. In **Search settings**, enter a research topic. Search terms are sent to OpenAlex and Crossref, so do not include private or confidential information.
2. Choose a maximum number of raw records to fetch per service. The default is 10. Higher limits can retrieve more records and take longer.
3. Adjust the publication year bounds and publication types if needed. Turn off a year checkbox to remove that bound. Turning off both includes records with missing publication years.
4. Select **Search**. Review the status and counts shown for each service. The sources may return different results. A partial status means retrieval stopped before the final page or a provider reported a problem.
5. Use the **Library** tab to browse saved records, filter by text, inspect metadata, and download the currently filtered rows as CSV.

Search is bounded to a maximum of 250 raw entries and five pages per provider. Filtering and deduplication can leave fewer records than the selected limit. Provider totals describe that provider's candidates. They are not a combined count of all relevant papers.

## Save search evidence

Open **Search history** to download the displayed search attempts and settings as JSON. Use **Download latest run bundle** to save the latest search manifest, deduplicated record CSV, and per-source/page provenance CSV. These files describe a search run, while the Library contains accumulated saved records.

## Screen and annotate a run

1. Open **Literature review** after a search with results.
2. Enter the review question, inclusion criteria, and exclusion criteria, then select **Start review**. The review stays attached to that captured search run, even if you run another search later.
3. Select a paper. Read its available metadata and abstract, then choose a decision: **pending**, **include**, **exclude**, or **uncertain**. Add a reason and save the decision.
4. To add a paper analysis, choose one of the six fields: objective, method, dataset, results, limitations, or conclusion. Write a note, classify it as a paper statement, interpretation, or missing information, and provide an exact excerpt from the captured abstract. Check that the excerpt supports the note before saving. Analysis notes require an available abstract.
5. Download **review JSON** to preserve the full review for reopening. Download the **comparison CSV** for a spreadsheet view. The JSON is the complete workspace. The review is session-only until you download it.

To continue later, upload the saved review JSON in **Literature review** and select **Reopen review**. Imports are limited to 10 MiB. Save the JSON before closing or restarting the app.

## Optional local AI proposals

The optional proposal feature requires the separately installed local Ollama runtime and model described in [Local Model Setup](LOCAL_MODEL_SETUP.md). In **Literature review**, select **Check local analysis backend**. If it is available and the app reports enough memory, you can request a proposal for the selected paper. Generation uses that paper's abstract and citation metadata.

Inspect each proposed field and excerpt yourself. Accept or reject the proposal with a reviewer note. Accepted AI claims remain separate from reviewer-authored notes and appear in `ai_` columns in the comparison CSV. The JSON keeps pending and rejected proposals too. Model output is not verified scientific analysis, and the evaluation record reports unresolved field accuracy problems. AI use is optional.

## Data and troubleshooting

- The app stores the paper library and search history in `data/research.db` beside `app.py`. Back up this file using the project’s [Data and Backup](DATA_AND_BACKUP.md) instructions.
- `exports/` is reserved. Current downloads go through the browser and are not automatically saved there.
- If a search fails, inspect the per-service status and error message, then check network access to OpenAlex and Crossref.
- If an optional model check fails, follow [Local Model Setup](LOCAL_MODEL_SETUP.md). The app does not install, download, or start the model service.
- Run the isolated test suite with `python -m unittest discover -s tests -v`. The tests use temporary databases and synthetic fixtures.

For behavior boundaries and known acceptance gaps, read [Project Status](PROJECT_STATUS.md), the [Phase C Plan](PHASE_C_PLAN.md), and the [Phase C Acceptance Gaps](PHASE_C_ACCEPTANCE_GAPS.md).
