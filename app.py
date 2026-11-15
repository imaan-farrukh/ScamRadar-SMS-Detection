"""ScamRadar: SMS phishing and scam detection (Streamlit front end).

Run with:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import engine
import ui_style as ui

st.set_page_config(page_title="ScamRadar | Detect the Scam. Protect Your Inbox.", page_icon="assets/logo.png", layout="wide",
                   initial_sidebar_state="collapsed")
ui.inject()

DISCLAIMER = ("ScamRadar is an AI-assisted detection tool. It may produce false positives and false negatives. "
              "Never share OTPs, passwords, PINs, or banking information through suspicious messages.")
EXAMPLES = {
    "Prize scam (English)": "Congratulations! You have won a 1000 pound prize. Call 09050001234 now to claim your reward. Offer expires today!",
    "Normal message (English)": "Hi, I will be ten minutes late. Please start the meeting without me and I will join as soon as I arrive.",
    "Account threat (Roman Urdu)": "Aap ka Easypaisa account band hone wala hai. Abhi is link par click karke apni details verify karein warna account block ho jayega.",
}


# ------------------------------------------------------------------ state helpers
def _init_state():
    st.session_state.setdefault("counts", {"total": 0, "suspicious": 0, "legitimate": 0})


def _clear(prefix: str):
    st.session_state[f"{prefix}_text"] = ""
    st.session_state[f"{prefix}_result"] = None
    st.session_state[f"{prefix}_error"] = None


def _use_example(prefix: str, key: str):
    st.session_state[f"{prefix}_text"] = EXAMPLES[key]
    st.session_state[f"{prefix}_lang"] = "Roman Urdu" if "Roman Urdu" in key else "English"
    st.session_state[f"{prefix}_result"] = None
    st.session_state[f"{prefix}_error"] = None


def _percent(x: float) -> str:
    if x >= 0.999:
        return "more than 99.9%"
    if x <= 0.001:
        return "less than 0.1%"
    return f"{x * 100:.0f}%" if 0.005 < x < 0.995 else f"{x * 100:.1f}%"


# ------------------------------------------------------------------ result rendering
def render_result(r: dict):
    p_sus, p_leg = r["p_suspicious"], r["p_legitimate"]
    if r["language"] == "Roman Urdu":
        st.markdown('<div class="sr-note"><b>Experimental Roman Urdu mode.</b> This model was trained on English messages plus a small, templated '
                    'Roman Urdu sample and has not been independently evaluated. Treat the result with extra care.</div>', unsafe_allow_html=True)
    if r["language"] == "English" and r["looks_roman_urdu"]:
        st.markdown('<div class="sr-note">This message looks like Roman Urdu. The English model was not trained on Roman Urdu; '
                    'select <b>Roman Urdu</b> above for the experimental Roman Urdu mode.</div>', unsafe_allow_html=True)

    if r["suspicious"]:
        warn = "".join(f"<li>{ui.esc(w)}</li>" for w in r["warning_signs"]) or "<li>No individual rule-based warning sign was found; the decision comes from the overall wording.</li>"
        extra = f'<div class="sr-section">Possible scam type</div>{ui.chips([r["scam_type"]], "red")}' if r["scam_type"] else ""
        words = f'<div class="sr-section">Terms that pushed the model towards suspicious</div>{ui.chips(r["words_suspicious"], "red")}' if r["words_suspicious"] else ""
        st.markdown(f"""
<div class="sr-result bad">
  <p class="title">Suspicious SMS</p>
  <p class="lead">ScamRadar classifies this message as potentially fraudulent. Do not reply, click links or call numbers in it.</p>
  <div class="sr-section">Model-estimated probability of scam</div>
  <div style="font-size:1.8rem;font-weight:700;color:#fca5a5">{_percent(p_sus)}</div>
  <div class="sr-bar"><div style="width:{p_sus*100:.1f}%;background:linear-gradient(90deg,#f59e0b,#ef4444)"></div></div>
  {extra}
  <div class="sr-section">Warning indicators found in the text</div>
  <ul style="margin:.2rem 0 0 1.1rem;color:#e2e8f0">{warn}</ul>
  {words}
  <div class="sr-section">Recommended action</div>
  <div style="color:#f1f5f9">{ui.esc(r["advice"])}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="sr-result good">
  <p class="title">Legitimate SMS</p>
  <p class="lead">No strong scam pattern was detected by the model.</p>
  <div class="sr-section">Model-estimated probability of legitimate</div>
  <div style="font-size:1.8rem;font-weight:700;color:#86efac">{_percent(p_leg)}</div>
  <div class="sr-bar"><div style="width:{p_leg*100:.1f}%;background:linear-gradient(90deg,#22d3ee,#22c55e)"></div></div>
  <div class="sr-section">Please remember</div>
  <div style="color:#f1f5f9">A legitimate classification does not guarantee that a message is safe. If a message asks for money, a PIN, an OTP or a password, verify it
  through the official channel of the organisation before acting.</div>
</div>""", unsafe_allow_html=True)
    st.caption("The percentage is the probability estimated by the logistic-regression model. It is not guaranteed to be a calibrated risk value. "
               f"Model used: {r['model_role']}.")
    st.markdown(f'<div class="sr-disclaimer"><b>Important.</b> {DISCLAIMER}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ detector panel (used on Home and on the detection page)
def render_detector(prefix: str):
    for k, v in {"result": None, "error": None, "text": "", "lang": "English"}.items():
        st.session_state.setdefault(f"{prefix}_{k}", v)

    st.markdown('<div class="sr-panel-title">Analyze an SMS message</div>'
                '<div class="sr-panel-sub">Paste the text of a suspicious message. It is analysed in memory and is not stored or logged.</div>', unsafe_allow_html=True)
    st.radio("Message language", ["English", "Roman Urdu"], horizontal=True, key=f"{prefix}_lang",
             help="Automatic language detection is not offered because it cannot be done reliably for short, mixed-language SMS.")
    st.text_area("SMS text", key=f"{prefix}_text", height=170, max_chars=engine.MAX_CHARS, label_visibility="collapsed",
                 placeholder="Paste the SMS here, for example: Congratulations! You have won a prize. Call now to claim it...")

    c1, c2, _ = st.columns([1.5, 1, 2.2])
    run = c1.button("Analyze Message", type="primary", key=f"{prefix}_run", width="stretch")
    c2.button("Clear", key=f"{prefix}_clear", on_click=_clear, args=(prefix,), width="stretch")

    with st.expander("Try an example message"):
        cols = st.columns(len(EXAMPLES))
        for col, key in zip(cols, EXAMPLES):
            col.button(key, key=f"{prefix}_ex_{key}", on_click=_use_example, args=(prefix, key), width="stretch")

    if run:
        result, error = engine.analyze(st.session_state[f"{prefix}_text"], st.session_state[f"{prefix}_lang"])
        st.session_state[f"{prefix}_result"], st.session_state[f"{prefix}_error"] = result, error
        if result:
            counts = st.session_state["counts"]
            counts["total"] += 1
            counts["suspicious" if result["suspicious"] else "legitimate"] += 1

    if st.session_state[f"{prefix}_error"]:
        st.error(st.session_state[f"{prefix}_error"])
    elif st.session_state[f"{prefix}_result"]:
        render_result(st.session_state[f"{prefix}_result"])


def render_counters():
    c = st.session_state["counts"]
    cols = st.columns(3)
    cols[0].markdown(ui.metric_card("Messages analyzed", c["total"], "this browser session only", "cyan"), unsafe_allow_html=True)
    cols[1].markdown(ui.metric_card("Flagged as suspicious", c["suspicious"], "this browser session only", "red"), unsafe_allow_html=True)
    cols[2].markdown(ui.metric_card("Classified as legitimate", c["legitimate"], "this browser session only", "green"), unsafe_allow_html=True)
    st.caption("The counters show only the messages analysed in this browser session. They are not stored and are not real-world usage statistics.")


# ------------------------------------------------------------------ pages
def page_home():
    _init_state()
    st.markdown(ui.brand(), unsafe_allow_html=True)
    st.markdown("""
<div class="sr-hero">
  <span class="sr-badge">SMS phishing detection</span>
  <h1>Stay Ahead of <span>SMS Scams.</span></h1>
  <p class="sr-tagline">Detect the Scam. Protect Your Inbox.</p>
  <p>An intelligent SMS phishing detection system that analyzes suspicious messages using machine learning and identifies potential scam activity.
  Paste a message and ScamRadar tells you whether it looks legitimate or suspicious, which warning signs it contains and what to do next.</p>
</div>""", unsafe_allow_html=True)
    render_counters()
    st.write("")
    with st.container(border=True):
        render_detector("home")
    st.write("")
    c = st.columns(3)
    c[0].markdown(ui.feature_card("text", "Text analysis", "Message wording, numbers, links, phone numbers and urgency cues are converted into features exactly as during model training."), unsafe_allow_html=True)
    c[1].markdown(ui.feature_card("radar", "Explainable result", "Rule-based warning indicators and the terms that influenced the model are shown next to the prediction."), unsafe_allow_html=True)
    c[2].markdown(ui.feature_card("lock", "Privacy by design", "Messages are processed in memory only. Nothing you paste is stored, logged or used for training."), unsafe_allow_html=True)


def page_detection():
    _init_state()
    st.markdown(ui.brand(small=True), unsafe_allow_html=True)
    st.title("SMS Detection")
    st.write("Paste an SMS message, choose its language and analyze it with the trained ScamRadar model.")
    left, right = st.columns([2.3, 1], gap="large")
    with left:
        with st.container(border=True):
            render_detector("detect")
    with right:
        render_counters_compact()
        st.markdown('<div class="sr-card"><h4>Which model answers?</h4>'
                    '<p><b>English:</b> the research model, trained on the English training set and evaluated on an untouched test set.<br><br>'
                    '<b>Roman Urdu:</b> the deployment model, trained on English and Roman Urdu messages. It is experimental and has not been independently evaluated.</p></div>',
                    unsafe_allow_html=True)


def render_counters_compact():
    c = st.session_state["counts"]
    st.markdown(ui.metric_card("This session", c["total"], f"{c['suspicious']} suspicious, {c['legitimate']} legitimate", "cyan"), unsafe_allow_html=True)
    st.write("")


def page_how():
    card = st.session_state.get("model_card") or engine.load_json("model_card.json") or {}
    params = card.get("research_model", {}).get("parameters", "see the notebook")
    st.markdown(ui.brand(small=True), unsafe_allow_html=True)
    st.title("How It Works")
    st.write("ScamRadar turns an SMS into numbers, applies a trained classifier and explains the result. The same steps are used for training and for prediction.")
    steps = [
        ("SMS input", "The user pastes a message and selects its language. The text is validated (not empty, not unusually long) and is processed in memory only."),
        ("Text preprocessing", "The text is normalised: lower-cased, and links, phone numbers, e-mail addresses, money amounts and other numbers are replaced by neutral tokens, so the model learns the pattern (a phone number is present) rather than one specific number. Fourteen additional numeric signals are computed, such as message length, share of capital letters and digits, and counts of urgency, action, prize and threat words."),
        ("TF-IDF feature extraction", "Words and word pairs are weighted with TF-IDF (term frequency times inverse document frequency). A chi-square test keeps the words that are most associated with the class. The vocabulary, the weights and the selected words were learned from the training data only and are stored inside the saved pipeline."),
        ("Machine learning classification", f"A tuned Logistic Regression assigns a weight to every feature, adds the weights and converts the total into the probability that the message is suspicious. Selected hyper-parameters: {params}. A message is flagged when the probability is at least 0.5."),
        ("Prediction and result", "The application shows the label, the model-estimated probability, rule-based warning indicators, a possible scam type and a safety recommendation. The rule-based parts explain the message; the decision itself comes from the model."),
    ]
    for i, (title, text) in enumerate(steps, 1):
        st.markdown(f'<div class="sr-card" style="margin-bottom:.8rem"><div class="sr-step"><div class="num">{i}</div><div><h4>{ui.esc(title)}</h4><p>{ui.esc(text)}</p></div></div></div>', unsafe_allow_html=True)

    st.subheader("Models compared in the research notebook")
    st.write("Seven classifiers and a dummy baseline were compared with 5-fold cross-validation on the English training set: **Logistic Regression, Linear SVM, Naive Bayes, "
             "K-Nearest Neighbours, Decision Tree, Random Forest and Gradient Boosting**. Four of them were tuned (Logistic Regression, Linear SVM, Naive Bayes, Random Forest). "
             "Only **one** model, the selected and tuned Logistic Regression, is used by this application; the other models were used for comparison only.")
    st.markdown('<div class="sr-note"><b>English and Roman Urdu models.</b> English messages are analysed by the research model (trained on English data only). '
                'Roman Urdu messages are analysed by a separate deployment model that also saw Roman Urdu training messages. '
                'The English model does not understand Roman Urdu reliably (see Model Performance), and the Roman Urdu mode remains experimental.</div>', unsafe_allow_html=True)


def page_about():
    st.markdown(ui.brand(small=True), unsafe_allow_html=True)
    st.title("About the Project")
    c = st.columns(2, gap="large")
    c[0].markdown(ui.feature_card("shield", "Project", "ScamRadar: An Intelligent Digital Fraud Awareness System. Category: Machine Learning / Cybersecurity. University project, course FDS."), unsafe_allow_html=True)
    c[1].markdown(ui.feature_card("layers", "Approach", "Binary classification of SMS messages into legitimate and suspicious (spam or smishing) using TF-IDF features and supervised learning."), unsafe_allow_html=True)
    st.write("")
    st.subheader("Research objective")
    st.write("Develop a machine learning based system that detects suspicious and scam SMS messages.")
    st.subheader("Main experiment: English SMS detection")
    st.write("The main experiment uses the English *SMS Phishing Dataset for Machine Learning and Pattern Recognition* (Mishra and Soni, 2022). After cleaning and removing duplicates, "
             "the data was split 80 / 20 (stratified). Models were trained, cross-validated and tuned on the training part only, and the selected model was evaluated once on the untouched test part.")
    st.subheader("Additional research: Roman Urdu generalization")
    st.write("To study how well an English-trained model recognises Pakistani scams, the *Roman Urdu Phishing SMS Dataset* (Siddiq, 2026) was used in separate, exploratory experiments. "
             "The results show that an English-only model does not generalise well to Roman Urdu messages. The Roman Urdu data is built from templates, so scores on it must be interpreted with caution.")
    st.subheader("Project team")
    st.table(pd.DataFrame({"Name": ["Imaan Farrukh"], "Roll number": ["CT-158"]}))
    st.markdown(f'<div class="sr-disclaimer"><b>Disclaimer.</b> {DISCLAIMER}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ model performance
def _plot_layout(fig, height=360):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
                      margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#e5e7eb"))
    return fig


def _confusion_fig(cm: dict, title: str):
    z = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
    fig = go.Figure(go.Heatmap(z=z, x=["Predicted legitimate", "Predicted suspicious"], y=["Actual legitimate", "Actual suspicious"],
                               text=[[str(v) for v in row] for row in z], texttemplate="%{text}", textfont=dict(size=22),
                               colorscale=[[0, "#0f1b34"], [1, "#3b82f6"]], showscale=False))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title=title)
    return _plot_layout(fig, 340)


def _metric_row(values: dict, sub: str = ""):
    cols = st.columns(len(values))
    for col, (label, val) in zip(cols, values.items()):
        col.markdown(ui.metric_card(label, f"{val:.3f}", sub, "cyan"), unsafe_allow_html=True)


def page_performance():
    st.markdown(ui.brand(small=True), unsafe_allow_html=True)
    st.title("Model Performance")
    st.write("All numbers on this page are read from the result files written by the research notebook. Nothing is calculated or invented by the web application.")
    test, cv_table = engine.load_json("english_test_metrics.json"), engine.load_csv("cv_model_comparison.csv")
    if test is None or cv_table is None:
        st.warning("Result files were not found in the `results/` folder. Run `notebooks/CT158_UPDATED.ipynb` from top to bottom to create them.")
        return
    tab_en, tab_ru, tab_dep = st.tabs(["English main experiment", "Roman Urdu exploratory experiment", "Deployment model"])

    with tab_en:
        st.subheader("Final evaluation on the untouched English test set")
        st.caption(f"Selected model: {test['model']} ({test['parameters']}). {test['n_test']:,} test messages, {test['n_test_suspicious']} of them suspicious. "
                   "The test set was used once, after model selection was finished.")
        _metric_row({"Accuracy": test["accuracy"], "Precision": test["precision"], "Recall": test["recall"], "F1-score": test["f1"], "ROC-AUC": test["roc_auc"]}, "test set")
        c1, c2 = st.columns(2)
        c1.plotly_chart(_confusion_fig(test["confusion"], "Confusion matrix (test set)"), width="stretch")
        roc = go.Figure(go.Scatter(x=test["roc_curve"]["fpr"], y=test["roc_curve"]["tpr"], mode="lines", line=dict(color=ui.CYAN, width=3), name="ROC curve"))
        roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color="#64748b", dash="dash"), name="chance"))
        roc.update_layout(title=f"ROC curve (AUC {test['roc_auc']:.3f})", xaxis_title="False-positive rate", yaxis_title="True-positive rate", legend=dict(orientation="h", y=-0.2))
        c2.plotly_chart(_plot_layout(roc, 340), width="stretch")
        cm = test["confusion"]
        st.write(f"Of {cm['tp'] + cm['fn']} suspicious messages, {cm['tp']} were caught and {cm['fn']} were missed. "
                 f"Of {cm['tn'] + cm['fp']} legitimate messages, {cm['fp']} were wrongly flagged.")
        st.caption(f"Supplementary probability-error metrics on the test set: MAE {test['mae_probability']:.4f}, MSE (Brier score) {test['mse_probability']:.4f}, "
                   f"RMSE {test['rmse_probability']:.4f}, R-squared {test['r2_probability']:.3f}. These regression-style metrics are computed between predicted probabilities and binary labels; "
                   "the classification metrics above are the primary metrics.")

        st.subheader("Model comparison: 5-fold cross-validation on the training set")
        show = cv_table[["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "Train F1"]].copy()
        st.dataframe(show.style.format("{:.3f}").background_gradient(cmap="Blues", subset=["F1"], vmin=0.85, vmax=1.0), width="stretch")
        real = show.drop(index=[i for i in show.index if "Dummy" in i])
        bars = go.Figure()
        for metric, color in [("Precision", ui.BLUE), ("Recall", ui.PURPLE), ("F1", ui.CYAN)]:
            bars.add_trace(go.Bar(x=real.index, y=real[metric], name=metric, marker_color=color))
        bars.update_layout(barmode="group", title="Precision, recall and F1 of every model (cross-validation)", yaxis=dict(range=[0.85, 1.0]), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(_plot_layout(bars, 380), width="stretch")

        tuning, nested = engine.load_csv("tuning_before_after.csv"), engine.load_csv("nested_cv.csv")
        if tuning is not None:
            st.subheader("Hyper-parameter tuning: before and after")
            cols = [c for c in ["F1 before", "F1 after", "F1 change", "Precision before", "Precision after", "Recall before", "Recall after"] if c in tuning.columns]
            st.dataframe(tuning[cols].style.format("{:.3f}"), width="stretch")
        if nested is not None:
            st.markdown("**Nested cross-validation** (tuning repeated inside each outer fold; less optimistic than the same-fold scores above)")
            st.dataframe(nested.style.format("{:.3f}"), width="stretch")

    with tab_ru:
        st.markdown('<div class="sr-note"><b>External exploratory evaluation.</b> This is not the main Phase 2 test result. The English-trained model was applied to Roman Urdu messages '
                    'to study generalization. Roman Urdu messages are templated, and the same dataset is also used in other exploratory experiments, so it is not an independent test set.</div>', unsafe_allow_html=True)
        ru = engine.load_json("roman_urdu_external.json")
        if ru is None:
            st.warning("`results/roman_urdu_external.json` was not found.")
        else:
            m = ru["metrics"]
            _metric_row({"Accuracy": m["Accuracy"], "Precision": m["Precision"], "Recall": m["Recall"], "F1-score": m["F1"]}, "Roman Urdu, exploratory")
            c1, c2 = st.columns([1, 1.4])
            c1.plotly_chart(_confusion_fig(ru["confusion"], "English-trained model on Roman Urdu"), width="stretch")
            rate = pd.Series(ru["flag_rate_by_type"]).sort_values()
            colors = [ui.RED if k.startswith("Phishing") else ui.GREEN for k in rate.index]
            fig = go.Figure(go.Bar(x=rate.values, y=[k.replace("Phishing - ", "[scam] ") for k in rate.index], orientation="h", marker_color=colors))
            fig.update_layout(title="% flagged as suspicious by message type", xaxis_title="% flagged")
            c2.plotly_chart(_plot_layout(fig, 340), width="stretch")
            st.write("The English-trained model flags many legitimate Pakistani bank and wallet messages (they contain numbers, amounts and words such as OTP) and misses some local phishing styles. "
                     "English models struggle with Roman Urdu because the vocabulary and spelling differ completely, spelling is not standardised, and the English training data teaches cues (such as currency symbols and premium-rate numbers) that do not occur in local scams.")
        exps = engine.load_csv("roman_urdu_template_experiments.csv")
        if exps is not None:
            st.subheader("Training experiments with template-aware splitting")
            st.dataframe(exps.style.format("{:.3f}"), width="stretch")
            st.caption("Rows D and E use held-out template groups. Very high scores here are a warning sign of an easy, templated task, not proof of real-world quality.")

    with tab_dep:
        card = engine.load_json("model_card.json")
        if card:
            st.session_state["model_card"] = card
            r, d = card["research_model"], card["deployment_model"]
            c1, c2 = st.columns(2, gap="large")
            c1.markdown(ui.feature_card("chart", "Research model (English)", f"{r['name']}, trained on {r['training_messages']:,} English training messages. Evaluated with cross-validation, nested cross-validation and one final test on the untouched English test set."), unsafe_allow_html=True)
            c2.markdown(ui.feature_card("layers", "Deployment model (Roman Urdu mode)", f"Same pipeline and hyper-parameters, trained on {d['training_messages']:,} messages ({d['english_messages']:,} English and {d['roman_urdu_messages']:,} Roman Urdu). It has not been independently evaluated, so no performance figures are reported for it."), unsafe_allow_html=True)
            st.write("")
            st.write(f"Decision threshold: {card['decision_threshold']} ({card['threshold_note']}).")
            st.caption("Library versions used for training: " + ", ".join(f"{k} {v}" for k, v in card["library_versions"].items()))
        else:
            st.warning("`results/model_card.json` was not found.")


pages = [st.Page(page_home, title="Home", icon=":material/shield:", default=True),
         st.Page(page_detection, title="SMS Detection", icon=":material/radar:", url_path="detection"),
         st.Page(page_how, title="How It Works", icon=":material/account_tree:", url_path="how-it-works"),
         st.Page(page_performance, title="Model Performance", icon=":material/bar_chart:", url_path="performance"),
         st.Page(page_about, title="About", icon=":material/info:", url_path="about")]
st.navigation(pages, position="top").run()
