import streamlit as st
import pickle
import numpy as np
import re

# =========================
# LOAD MODEL
# =========================
model = pickle.load(open("model.pkl", "rb"))
tfidf = pickle.load(open("tfidf.pkl", "rb"))

# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(text):
    text_lower = text.lower()

    urls = re.findall(r'http[s]?://\S+', text)

    urgency_words = ['urgent', 'verify', 'suspended', 'immediately', 'click']

    features = {
        "url_count": len(urls),
        "suspicious_url_count": sum(1 for u in urls if "http://" in u),
        "urgency_score": sum(text_lower.count(w) for w in urgency_words),
        "body_length": len(text)
    }

    return features

# =========================
# UI DESIGN
# =========================
st.set_page_config(
    page_title="AI Phishing Detector",
    page_icon="📧",
    layout="centered"
)

st.title("📧 AI-Powered Phishing Detector")
st.markdown("Analyze emails and detect phishing attempts with AI.")

st.divider()

# =========================
# INPUT
# =========================
email_input = st.text_area(
    "✉️ Paste your email content:",
    height=200,
    placeholder="Example: URGENT: Verify your account now..."
)

# =========================
# ANALYZE BUTTON
# =========================
if st.button("🔍 Analyze Email"):

    if email_input.strip() == "":
        st.warning("Please enter an email.")
    else:
        # Extract features
        features = extract_features(email_input)
        feature_values = np.array(list(features.values())).reshape(1, -1)

        # TF-IDF
        text_vec = tfidf.transform([email_input]).toarray()

        # Combine
        X = np.hstack((text_vec, feature_values))

        # Prediction
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0][1]

        st.divider()

        # =========================
        # RESULT DISPLAY
        # =========================
        if pred == 1:
            st.error(f"⚠️ Phishing Detected ({proba:.2f} confidence)")
        else:
            st.success(f"✅ Legitimate Email ({1 - proba:.2f} confidence)")

        # =========================
        # FEATURE DISPLAY
        # =========================
        st.subheader("🔍 Extracted Features")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("URL Count", features["url_count"])
            st.metric("Suspicious URLs", features["suspicious_url_count"])

        with col2:
            st.metric("Urgency Score", features["urgency_score"])
            st.metric("Body Length", features["body_length"])

        # =========================
        # SIMPLE EXPLANATION
        # =========================
        st.subheader("🧠 Why this result?")

        explanation = []

        if features["suspicious_url_count"] > 0:
            explanation.append("Contains suspicious links")

        if features["urgency_score"] > 0:
            explanation.append("Uses urgent language")

        if features["url_count"] > 2:
            explanation.append("Multiple links detected")

        if len(explanation) == 0:
            explanation.append("No strong phishing signals detected")

        for e in explanation:
            st.write(f"- {e}")