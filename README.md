# ScamRadar – SMS Phishing Detection

**Detect the Scam. Protect Your Inbox.**

ScamRadar is a Machine Learning-based SMS phishing detection system designed to identify suspicious messages and help users recognize potential scam activity.

Users can paste an SMS and receive a prediction, warning signs, and guidance on what to do next.

## Live Demo

🚀 **[Try ScamRadar Live](https://scamradar-sms-detection-ifk.streamlit.app/)**

## Features

- SMS scam and phishing detection
- Machine Learning-based text classification
- English SMS detection
- Experimental Roman Urdu SMS detection
- Warning signs and suspicious pattern identification
- Interactive Streamlit interface
- Privacy-conscious message processing

## Technologies Used

- Python
- Machine Learning
- Scikit-learn
- TF-IDF
- Logistic Regression
- Pandas
- Streamlit
- Joblib

## Project Files

- `app.py` – Streamlit application
- `engine.py` – Prediction and model loading
- `scamradar_utils.py` – Text processing and explanation rules
- `ui_style.py` – UI styling
- `requirements.txt` – Project dependencies
- `english_model.joblib` – English SMS model
- `deployment_model.joblib` – Deployment model
- `config.toml` – Configuration
- `logo.png` and `logo.svg` – Project branding

## Model Information

**English:** Uses a tuned Logistic Regression pipeline evaluated through cross-validation and an independent test set.

**Roman Urdu:** Uses an experimental deployment model trained on English and Roman Urdu messages. Its performance has not been independently validated.

## Installation

```bash
git clone https://github.com/imaan-farrukh/ScamRadar-SMS-Detection.git

cd ScamRadar-SMS-Detection

pip install -r requirements.txt

streamlit run app.py
```

## Privacy

Messages are processed in memory and are not stored or used for model training.

## Limitations

ScamRadar may produce false positives or false negatives. Its predictions should not be treated as a guarantee that a message is safe.

Never share OTPs, passwords, PINs, or banking information in response to suspicious messages.

## Future Improvements

- Improve Roman Urdu detection
- Expand multilingual SMS datasets
- Enhance model performance
- Improve detection of emerging phishing patterns

## Author

**Imaan Farrukh**

BS Computer Science

GitHub: [imaan-farrukh](https://github.com/imaan-farrukh)

---

⭐ If you find this project interesting, consider giving the repository a star!
