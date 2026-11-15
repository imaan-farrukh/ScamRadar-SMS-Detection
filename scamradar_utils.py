"""ScamRadar helper functions — text normalisation and feature engineering (fixed rules, no learning)."""
import re
import numpy as np
import pandas as pd

# ---------- regular expressions ----------
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
URL_RE = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+\.(?:com|net|org|co\.uk|pk|info|biz|ac|me|ly)\b\S*)", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+\d{1,3}[\s\-]?|0)\d[\d\s\-]{7,}\d(?!\d)")
MONEY_RE = re.compile(r"[£$€]|\b(?:rs|pkr|rupees?|pounds?|usd)\b\.?", re.I)
NUMBER_RE = re.compile(r"\d[\d,\.]*\d|\d")

URGENT_RE = re.compile(r"\b(?:urgent|immediately|now|today|expire[sd]?|last chance|hurry|asap|final|limited|abhi|fori|jaldi)\b", re.I)
ACTION_RE = re.compile(r"\b(?:call|text|txt|reply|click|send|dial|visit|log ?on|rabta)\b", re.I)
SENSITIVE_RE = re.compile(r"\b(?:pin|otp|password|cvv|cnic|account|a/c|card|verify|login|details|kyc|code)\b", re.I)
PRIZE_RE = re.compile(r"\b(?:won|win|winner|prize|award(?:ed)?|congrat\w*|reward|lottery|claim|inaam|inam|mubarak|bonus|gift)\b", re.I)
THREAT_RE = re.compile(r"\b(?:block(?:ed)?|suspend(?:ed)?|freeze|frozen|hack(?:ed)?|deactivat\w*|close[ds]?|band|legal action|arrest)\b", re.I)

NUMERIC_FEATURES = ["char_count_log", "word_count_log", "upper_ratio", "digit_ratio", "exclaim_count",
                    "has_url", "has_email", "has_phone", "has_money",
                    "urgency_count", "action_count", "sensitive_count", "prize_count", "threat_count"]


def normalize_text(text):
    """Lower-case and replace links, e-mails, phones, money and numbers by generic tokens."""
    t = str(text).strip()
    t = EMAIL_RE.sub(" emailtoken ", t)
    t = URL_RE.sub(" urltoken ", t)
    t = PHONE_RE.sub(" phonetoken ", t)
    t = MONEY_RE.sub(" moneytoken ", t)
    t = NUMBER_RE.sub(" numtoken ", t)
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def build_features(texts):
    """Return a DataFrame: `clean_text` + 14 numeric features, computed from the raw message(s)."""
    s = texts if isinstance(texts, pd.Series) else pd.Series(list(texts))
    raw = s.fillna("").astype(str).str.strip()
    out = pd.DataFrame(index=raw.index)
    out["clean_text"] = raw.map(normalize_text)

    n_chars = raw.str.len()
    n_words = raw.str.split().str.len().fillna(0)
    letters = raw.str.count(r"[A-Za-z]")
    out["char_count_log"] = np.log1p(n_chars)
    out["word_count_log"] = np.log1p(n_words)
    out["upper_ratio"] = raw.str.count(r"[A-Z]") / letters.replace(0, 1)
    out["digit_ratio"] = raw.str.count(r"\d") / n_chars.replace(0, 1)
    out["exclaim_count"] = raw.str.count("!")

    no_email = raw.map(lambda t: EMAIL_RE.sub(" ", t))
    out["has_url"] = no_email.map(lambda t: int(bool(URL_RE.search(t))))
    out["has_email"] = raw.map(lambda t: int(bool(EMAIL_RE.search(t))))
    out["has_phone"] = raw.map(lambda t: int(bool(PHONE_RE.search(t))))
    out["has_money"] = raw.map(lambda t: int(bool(MONEY_RE.search(t))))
    for name, pat in [("urgency_count", URGENT_RE), ("action_count", ACTION_RE), ("sensitive_count", SENSITIVE_RE),
                      ("prize_count", PRIZE_RE), ("threat_count", THREAT_RE)]:
        out[name] = raw.map(lambda t, p=pat: len(p.findall(t)))
    return out


# =====================================================================
# Explanation layer: warning signs, scam type, advice, model explanation
# =====================================================================
SCAM_TYPE_RULES = [
    ("Wrong-number refund scam", re.compile(r"ghalti se|galti se|wapis bhej|wapas bhej|sent by mistake|by mistake|refund", re.I)),
    ("Government scheme scam", re.compile(r"\b(?:bisp|ehsaas|benazir|income support|kafalat|nadra|govt|government|sarkari)\b", re.I)),
    ("Card update / link scam", re.compile(r"atm card|card suspend|kyc|update.*link|link.*update", re.I)),
    ("Account hack warning", re.compile(r"\bhack", re.I)),
    ("Account freeze (FBR) threat", re.compile(r"\bfbr\b|\bfreez|frozen", re.I)),
    ("Account block threat", re.compile(r"\bblock|band ho|suspend|deactivat", re.I)),
    ("Prize / lottery / reward scam", PRIZE_RE),
    ("Fake delivery / parcel notice", re.compile(r"deliver|parcel|courier|package|shipment", re.I)),
    ("Loan / credit offer", re.compile(r"\bloan|credit|refused|debt|mortgage", re.I)),
    ("Adult / dating spam", re.compile(r"adult|xxx|sexy|dating|lonely|chat with|babe|18\+", re.I)),
    ("Premium-rate / subscription spam", re.compile(r"\b(?:txt|text|reply|send)\b.{0,40}\b\d{4,6}\b|stop to|\d+p\b|per ?(?:wk|week|min)|subscri|unsubscribe|premium", re.I)),
]
OTHER_TYPE = "Other suspicious message"

ADVICE = {
    "Prize / lottery / reward scam": "Real prizes never ask for fees, PINs or personal details. Ignore the message and do not call or click anything.",
    "Government scheme scam": "Government schemes do not ask for your PIN or bank details by SMS. Check only on the official website or helpline.",
    "Account block threat": "Banks do not ask for PINs or OTPs by SMS or phone. Call the number printed on the back of your card or use the official app.",
    "Account freeze (FBR) threat": "Government agencies do not freeze accounts by SMS or ask for OTPs. Never share an OTP.",
    "Account hack warning": "Never change a password or share a code through a number sent in an SMS. Open the official app yourself.",
    "Card update / link scam": "Do not open the link. Go to your bank's official website or app and check for notices there.",
    "Wrong-number refund scam": "Do not send money back. Ask the sender to contact their bank; check your own account in the official app.",
    "Fake delivery / parcel notice": "Do not click the link or pay a 'delivery fee'. Check the parcel only on the courier's official website.",
    "Loan / credit offer": "Do not call or reply. Use only licensed lenders and never pay a fee in advance.",
    "Adult / dating spam": "Do not reply or open links. Block the number.",
    "Premium-rate / subscription spam": "Do not reply — replying may start paid subscriptions. Block the number.",
    OTHER_TYPE: "Do not click links, call numbers or share personal details. Verify through the organisation's official channel.",
}

NUM_NAMES = {"char_count_log": "message length", "word_count_log": "number of words", "upper_ratio": "many CAPITAL letters",
             "digit_ratio": "many digits", "exclaim_count": "exclamation marks", "has_url": "contains a link",
             "has_email": "contains an e-mail", "has_phone": "contains a phone number", "has_money": "mentions money",
             "urgency_count": "urgency words", "action_count": "call / text / click words", "sensitive_count": "PIN / OTP / account words",
             "prize_count": "prize / reward words", "threat_count": "threat words (blocked, hacked…)"}
TOKEN_NAMES = {"urltoken": "[link]", "phonetoken": "[phone number]", "numtoken": "[number]", "moneytoken": "[money]", "emailtoken": "[e-mail]"}
ROMAN_URDU_WORDS = {"apka", "apna", "apke", "aap", "hai", "hain", "ha", "krein", "karein", "kren", "abhi", "gya", "gaya", "dia", "diya",
                    "lie", "liye", "mubarak", "inaam", "inam", "bhai", "shukar", "wapis", "ghalti", "rabta", "hasil", "krne", "karne", "jaldi", "fori"}


def detect_scam_type(text):
    t = str(text)
    for name, pattern in SCAM_TYPE_RULES:
        if pattern.search(t):
            return name
    return OTHER_TYPE


def detect_warning_signs(text):
    t = str(text)
    signs = []
    if PRIZE_RE.search(t): signs.append(" Unexpected prize / reward claim")
    if THREAT_RE.search(t): signs.append(" Threat about your account or card (blocked, frozen, hacked …)")
    if SENSITIVE_RE.search(t): signs.append(" Mentions PIN / OTP / password / account details")
    if URGENT_RE.search(t): signs.append("Urgency: pressure to act immediately")
    if URL_RE.search(EMAIL_RE.sub(" ", t)): signs.append(" Contains a link")
    if PHONE_RE.search(t): signs.append(" Contains a phone number to contact")
    if ACTION_RE.search(t): signs.append(" Asks you to call / text / reply / click")
    if MONEY_RE.search(t): signs.append(" Mentions money")
    letters = sum(c.isalpha() for c in t)
    if letters > 15 and sum(c.isupper() for c in t) / letters > 0.4: signs.append(" Mostly CAPITAL letters")
    return signs


def looks_roman_urdu(text):
    words = set(re.findall(r"[a-z]+", str(text).lower()))
    return len(words & ROMAN_URDU_WORDS) >= 2


def explain_message(text, model, top_n=5):
    """Words / features that pushed the model towards 'suspicious' (and towards 'legitimate') for THIS message."""
    feats = build_features([text])
    prep, clf = model.named_steps["prep"], model.named_steps["clf"]
    x = prep.transform(feats)
    x = x.toarray() if hasattr(x, "toarray") else np.asarray(x)
    contrib = x[0] * clf.coef_[0]
    items = []
    for n, c in zip(prep.get_feature_names_out(), contrib):
        if c == 0:
            continue
        label = " ".join(TOKEN_NAMES.get(w, w) for w in n[6:].split()) if n.startswith("text__") else "⟨" + NUM_NAMES.get(n[5:], n[5:]) + "⟩"
        items.append((label, float(c)))
    items.sort(key=lambda t: -t[1])
    towards_sus = [i for i in items if i[1] > 0][:top_n]
    towards_safe = [i for i in reversed(items) if i[1] < 0][:top_n]
    return towards_sus, towards_safe


def analyze_message(text, model, threshold=0.5):
    """Full ScamRadar analysis of one message."""
    proba = float(model.predict_proba(build_features([text]))[0, 1])
    suspicious = proba >= threshold
    signs = detect_warning_signs(text)
    scam_type = detect_scam_type(text) if suspicious else None
    sus_words, safe_words = explain_message(text, model)
    advice = ADVICE[scam_type] if suspicious else "No strong scam pattern found — but never share PINs, OTPs or passwords, and verify unexpected requests through official channels."
    return {"text": text, "probability": proba, "suspicious": suspicious, "warning_signs": signs, "scam_type": scam_type,
            "words_suspicious": sus_words, "words_legitimate": safe_words, "advice": advice,
            "roman_urdu": looks_roman_urdu(text)}


def format_report(r):
    """Markdown report for a result of analyze_message()."""
    icon = " **Potentially suspicious**" if r["suspicious"] else " **Looks legitimate**"
    lines = [f"> “{r['text'][:200]}”", "", f"### {icon} — suspicious probability **{r['probability']:.0%}**"]
    if r["scam_type"]:
        lines += ["", f"**Possible scam type:** {r['scam_type']}"]
    if r["warning_signs"]:
        lines += ["", "**Signals found in the text:**"] + [f"- {s}" for s in r["warning_signs"]]
    if r["words_suspicious"]:
        lines += ["", "**What pushed the model towards 'suspicious':** " + ", ".join(f"`{w}`" for w, _ in r["words_suspicious"])]
    lines += ["", f"**Recommended action:** {r['advice']}"]
    if r["roman_urdu"]:
        lines += ["", "* This looks like Roman Urdu. The model has seen only a small, templated Roman Urdu sample, so please treat the result with extra care.*"]
    return "\n".join(lines)
