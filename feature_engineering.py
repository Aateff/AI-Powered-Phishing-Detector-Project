# ==========================================
# feature_engineering.py
# ==========================================

import re
from urllib.parse import urlparse

# ------------------------------------------
# 1. GLOBAL CONFIG
# ------------------------------------------

URGENCY_WORDS = [
    "urgent", "immediately", "verify", "suspended",
    "click", "now", "action required", "expire"
]

SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".club", ".online", ".site"
]

SHORTENERS = [
    "bit.ly", "tinyurl.com", "goo.gl", "t.co"
]

# ------------------------------------------
# 2. URL EXTRACTION
# ------------------------------------------

def extract_urls(text):
    """
    Extract all URLs from text.
    """
    return re.findall(r'http[s]?://\S+', text)


# ------------------------------------------
# 3. URL FEATURES
# ------------------------------------------

def analyze_urls(urls):
    """
    Extract features from URLs.
    """
    suspicious_count = 0
    ip_based_count = 0
    shortener_count = 0

    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc

        # IP-based URL
        if re.match(r'\d+\.\d+\.\d+\.\d+', domain):
            ip_based_count += 1
            suspicious_count += 1

        # Suspicious TLD
        if any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
            suspicious_count += 1

        # URL shortener
        if any(short in domain for short in SHORTENERS):
            shortener_count += 1
            suspicious_count += 1

    return {
        "url_count": len(urls),
        "suspicious_url_count": suspicious_count,
        "ip_url_count": ip_based_count,
        "shortener_url_count": shortener_count
    }


# ------------------------------------------
# 4. TEXT FEATURES
# ------------------------------------------

def urgency_score(text):
    """
    Count urgency-related words.
    """
    text = text.lower()
    return sum(text.count(word) for word in URGENCY_WORDS)


def basic_text_stats(text):
    """
    Extract basic text features.
    """
    words = text.split()

    return {
        "body_length": len(text),
        "word_count": len(words),
        "avg_word_length": sum(len(w) for w in words) / (len(words) + 1)
    }


# ------------------------------------------
# 5. HTML / STRUCTURAL FEATURES (basic)
# ------------------------------------------

def detect_html_features(text):
    """
    Basic HTML-based signals.
    """
    hidden_text = 0

    # Detect hidden styles
    if "display:none" in text.lower() or "font-size:0" in text.lower():
        hidden_text = 1

    return {
        "html_hidden_text": hidden_text
    }


# ------------------------------------------
# 6. MAIN FEATURE BUILDER
# ------------------------------------------

def extract_features(text):
    """
    Main function to extract ALL features from an email.
    Returns a dictionary.
    """

    features = {}

    # -------- URLs --------
    urls = extract_urls(text)
    features.update(analyze_urls(urls))

    # -------- Text --------
    features["urgency_score"] = urgency_score(text)
    features.update(basic_text_stats(text))

    # -------- HTML --------
    features.update(detect_html_features(text))

    return features


# ------------------------------------------
# 7. VECTOR FORMAT (for ML)
# ------------------------------------------

def features_to_vector(feature_dict):
    """
    Convert feature dictionary to ordered list (vector).
    """
    ordered_keys = [
        "url_count",
        "suspicious_url_count",
        "ip_url_count",
        "shortener_url_count",
        "urgency_score",
        "body_length",
        "word_count",
        "avg_word_length",
        "html_hidden_text"
    ]

    return [feature_dict.get(k, 0) for k in ordered_keys]


# ------------------------------------------
# 8. TEST (run file directly)
# ------------------------------------------

if __name__ == "__main__":
    test_email = """
    URGENT: Your account is suspended.
    Click http://192.168.0.1/login or http://bit.ly/fake-link now!
    """

    feats = extract_features(test_email)
    vector = features_to_vector(feats)

    print("🔍 Features:")
    for k, v in feats.items():
        print(f"{k}: {v}")

    print("\n📊 Feature Vector:")
    print(vector)