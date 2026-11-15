# ScamRadar: SMS Phishing and Scam Detection

*Detect the Scam. Protect Your Inbox.*

ScamRadar is a machine learning project (binary text classification: legitimate versus suspicious SMS) with a Streamlit web
application. Project by Imaan Farrukh (CT-158), course FDS.

## Project structure

```
ScamRadar/
├── app.py                    Streamlit application (entry point)
├── engine.py                 model loading, input validation, prediction
├── ui_style.py               visual identity (CSS and small HTML helpers)
├── scamradar_utils.py        text normalisation, feature engineering, explanation rules (written by the notebook)
├── requirements.txt
├── .streamlit/config.toml    dark theme
├── assets/                   logo
├── data/                     raw and cleaned datasets (raw files are never modified)
├── models/
│   ├── english_model.joblib      research model: English training data only, evaluated in the notebook
│   └── deployment_model.joblib   deployment model: English + Roman Urdu training data, not independently evaluated
├── results/                  result tables and metrics exported by the notebook (read by the "Model Performance" page)
└── notebooks/
    └── CT158_UPDATED.ipynb   Phase 1 (data preparation) and Phase 2 (modelling) with all outputs
```

## Install and run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate        macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The application opens at http://localhost:8501. It only loads the saved models; it never trains anything.

If the saved models cannot be loaded (for example because another scikit-learn version is installed), re-create them by running the
notebook (next section). The application shows a clear message instead of crashing when a model or result file is missing.

## Re-run the notebook

Open `notebooks/CT158_UPDATED.ipynb` in Jupyter and run all cells from top to bottom (about 15 to 30 minutes on one CPU core, because of
the hyper-parameter searches and the nested cross-validation). The notebook automatically changes to the project root, reads the
datasets from `data/`, and writes `scamradar_utils.py`, `models/` and `results/`.

## Which model answers which message?

| Selected language | Model | Evidence |
|---|---|---|
| English | `models/english_model.joblib`: tuned Logistic Regression, trained on the English training set only | cross-validation, nested cross-validation and one final evaluation on the untouched English test set (notebook Sections 9 to 13) |
| Roman Urdu | `models/deployment_model.joblib`: same pipeline, trained on English and Roman Urdu messages | experimental: not independently evaluated; only exploratory template-aware experiments exist (Section 14.3) |

An "Auto Detect" option is intentionally not offered: language detection of short, mixed-language SMS is not reliable.
The research model is **not** used for Roman Urdu predictions because it does not generalise to Roman Urdu messages (Section 14.2).

## Privacy

Messages are processed in memory only. They are not stored, logged or used for training. The web application keeps only three
counters (messages analysed, flagged, legitimate) in the browser session.

## Limitations

ScamRadar is an AI-assisted detection tool. It may produce false positives and false negatives. The English training data is
older and UK-flavoured; the Roman Urdu data is small and built from templates. Never share OTPs, passwords, PINs or banking information
through suspicious messages, whatever the result of the tool.

## Data sources

* Mishra and Soni (2022), *SMS Phishing Dataset for Machine Learning and Pattern Recognition*, Mendeley Data, DOI 10.17632/f45bkkt8pr.1
* Siddiq (2026), *Roman Urdu Phishing SMS Dataset for Smishing Detection Research*, Zenodo, DOI 10.5281/zenodo.21810885
