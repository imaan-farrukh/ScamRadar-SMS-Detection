"""Model loading and prediction for the ScamRadar web application.

* The saved scikit-learn pipelines are loaded once (cached); nothing is trained or evaluated here.
* Pre-processing is not re-implemented: `scamradar_utils.analyze_message` applies the same feature
  engineering and the saved pipeline (TF-IDF, chi2 selector, imputer, scaler, classifier) that were used in training.
* Messages are processed in memory only. They are never written to disk or logged.
"""
import json
from pathlib import Path

import joblib
import streamlit as st

import scamradar_utils as su

ROOT = Path(__file__).resolve().parent
MODEL_DIR, RESULT_DIR = ROOT / "models", ROOT / "results"
MAX_CHARS = 1500
MIN_CHARS = 3

# English messages -> research model (trained on the English training set only, evaluated in the notebook).
# Roman Urdu messages -> deployment model (English + Roman Urdu training data, NOT independently evaluated).
MODEL_FILES = {"English": MODEL_DIR / "english_model.joblib", "Roman Urdu": MODEL_DIR / "deployment_model.joblib"}
MODEL_ROLE = {"English": "Research model (English training data, evaluated on an untouched test set)",
              "Roman Urdu": "Deployment model (English + Roman Urdu training data, experimental, not independently evaluated)"}


@st.cache_resource(show_spinner=False)
def _load(path_str: str):
    return joblib.load(path_str)


def get_model(language: str):
    """Return (model, error_message). Never raises."""
    path = MODEL_FILES.get(language)
    if path is None:
        return None, f"Unknown language option: {language}"
    if not path.exists():
        return None, (f"The model file `{path.relative_to(ROOT)}` was not found. Run the notebook "
                      "`notebooks/CT158_UPDATED.ipynb` from top to bottom to create it.")
    try:
        return _load(str(path)), None
    except Exception as exc:  # incompatible scikit-learn version, corrupt file, ...
        return None, (f"The model file `{path.name}` could not be loaded ({type(exc).__name__}). "
                      "Install the package versions from requirements.txt or re-run the notebook.")


def validate(text: str):
    """Return an error message, or None when the input is acceptable."""
    cleaned = (text or "").strip()
    if not cleaned:
        return "Please paste an SMS message first."
    if len(cleaned) < MIN_CHARS:
        return "The message is too short to analyse."
    if len(cleaned) > MAX_CHARS:
        return f"The message is longer than {MAX_CHARS} characters. SMS messages are normally much shorter; please shorten it."
    if not any(ch.isalnum() for ch in cleaned):
        return "The message contains no letters or digits."
    return None


def analyze(text: str, language: str):
    """Return (result_dict, error_message). The result never contains the message text."""
    problem = validate(text)
    if problem:
        return None, problem
    model, err = get_model(language)
    if err:
        return None, err
    try:
        r = su.analyze_message(text.strip(), model)
    except Exception as exc:
        return None, f"The message could not be analysed ({type(exc).__name__}). Please try a different text."
    p = float(r["probability"])
    result = {"suspicious": bool(r["suspicious"]), "p_suspicious": p, "p_legitimate": 1.0 - p,
              "scam_type": r.get("scam_type"), "warning_signs": list(r.get("warning_signs") or []),
              "words_suspicious": [w for w, _ in (r.get("words_suspicious") or [])],
              "advice": r.get("advice", ""), "looks_roman_urdu": bool(r.get("roman_urdu")), "language": language,
              "model_role": MODEL_ROLE[language]}
    return result, None


def load_json(name: str):
    path = RESULT_DIR / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_csv(name: str):
    import pandas as pd
    path = RESULT_DIR / name
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, index_col=0)
    except Exception:
        return None
