# data-quality-scorer

A Python pipeline that aggregates data quality scores (accuracy, completeness, uniqueness, formatting) across multiple CSV sources and outputs consolidated results to JSON with detailed logging.

---

## What It Does

- Scans multiple data sources (analysis, archive, deskpro, duns, fuzzy, prospect, public, supplier360)
- For each source, reads CSV files across five quality dimensions:
  - **Accuracy** — row-level record scores
  - **Completeness** — field-level completeness scores
  - **Uniqueness** — deduplication scores
  - **Data Quality** — overall DQ scores
  - **Data Formatting** — format compliance scores
- Aggregates per-account scores and computes source-level averages
- Outputs a consolidated `output.json`
- Logs all processing steps to `belden.log`

---

## Project Structure

```
data-quality-scorer/
│
├── main_1.py                    # Entry point
├── pure_utils.py                # CSV reading and per-account score aggregation
├── pure_finalscores_calculator.py  # Source-level average score calculation
├── .gitignore
└── README.md
```

---

## Expected Folder Structure

The pipeline expects data to be organized as follows:

```
F:/belden/
├── analysis/Scoring/
│   ├── accuracy scoring/       # account CSVs with column: Record_Score
│   ├── completeness/           # account CSVs with column: Complete_Score
│   ├── data formating/         # account CSVs with column: DF_Score
│   ├── data quality/           # account CSVs with column: DQ_Score
│   └── uniqueness scoring/
│       └── uniquesness_scores.csv  # columns: File, Uniqueness Score
├── archive/Scoring/
│   └── ...
└── (same structure for all sources)
```

> You can change the base directory by updating `base_root_directory` in `main_1.py`.

---

## Requirements

No external dependencies — uses Python standard library only.

- Python 3.7+
- `os`, `csv`, `glob`, `json`, `logging` (all built-in)

---

## How to Run

```bash
python main_1.py
```

---

## Output

**`output.json`** — consolidated scores per source:

```json
{
  "analysis": {
    "score": {
      "Score_Acurracy": 87.45,
      "Score_Completness": 92.10,
      "Score_Uniqueness": 95.30,
      "Score_Data_Quality": 88.70,
      "Score_Data_Format": 91.00
    }
  },
  ...
}
```

**`belden.log`** — detailed DEBUG-level log of all processing steps, warnings, and errors.

---

## Logging

All activity is logged to `belden.log` at `DEBUG` level, including:

- Files read and values parsed
- Missing files or columns (warnings)
- Per-account and per-source score calculations
- Any processing errors

---

## Notes

- If no CSVs are found for a source, all scores for that source are set to `null`
- Non-numeric values in score columns are skipped with a warning
- Scores are rounded to 2 decimal places in the final output
