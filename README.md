# PhishGuard

> Explainable phishing and malicious-URL detection using machine learning, security rules, and a Chrome extension.

PhishGuard is a security research and educational prototype that analyzes website URLs and estimates whether they are **SAFE, SUSPICIOUS, or PHISHING**.

It combines machine-learning models, deterministic security rules, URL-structure analysis, and known-domain context to produce an explainable risk assessment.

## 🚨 Problem

Phishing attacks often use deceptive URLs to trick users into visiting malicious websites.

PhishGuard combines multiple URL-level signals to provide:

- Phishing risk score
- Risk level
- Security verdict
- Explainable reasons
- Browser warning before navigating to URLs classified as phishing

## ✨ Key Features

- Machine-learning based URL classification
- Explainable security decisions
- SAFE / SUSPICIOUS / PHISHING verdicts
- Risk score from 0–100
- URL structure and security-pattern analysis
- Known-domain context using Tranco
- Chrome extension integration
- Automatic warning for PHISHING-classified navigation
- Go Back / Continue Anyway options
- REST API for URL analysis

## 🏗️ System Architecture

```text
                 ┌──────────────────┐
                 │  Chrome Browser  │
                 └────────┬─────────┘
                          │ URL
                          ▼
                 ┌──────────────────┐
                 │ Chrome Extension │
                 └────────┬─────────┘
                          │ HTTPS
                          ▼
                 ┌──────────────────┐
                 │   FastAPI API    │
                 └────────┬─────────┘
                          ▼
              ┌─────────────────────────┐
              │    Security Engine V2   │
              └───────────┬─────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
       ML Models     Security Rules   Domain Context
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                 ┌──────────────────┐
                 │ Verdict + Score  │
                 │ + Explanations   │
                 └──────────────────┘
```

## 🔍 How It Works

1. Extract URL-level features.
2. Analyze hostname, path, and query structure.
3. Run the URL through machine-learning models.
4. Check deterministic security indicators.
5. Check known-domain context.
6. Combine the signals in the security engine.
7. Generate a risk score and verdict.
8. Return explainable reasons.

### Verdicts

| Risk Score | Verdict | Risk Level |
|---|---|---|
| 0–39 | SAFE | LOW |
| 40–69 | SUSPICIOUS | MEDIUM |
| 70–100 | PHISHING | HIGH |

## 🤖 Machine Learning

PhishGuard experiments with multiple machine-learning approaches.

### Feature-based Random Forest

The baseline model uses extracted URL features and a Random Forest classifier.

**Evaluation:**

- Accuracy: **98.89%**
- Precision: **98.95%**
- Recall: **98.33%**
- F1-score: **98.64%**

### Raw URL Model

A character-level TF-IDF representation of URLs is combined with Logistic Regression.

**Evaluation:**

- Accuracy: **99.01%**
- Precision: **99.76%**
- Recall: **97.81%**
- F1-score: **98.78%**

### Region-aware Model

A separate experiment models hostname, path, and query regions using character-level TF-IDF features.

**Evaluation:**

- Accuracy: **99.13%**
- Precision: **99.61%**
- Recall: **98.26%**
- F1-score: **98.93%**

The region-aware model was retained as an experimental benchmark rather than the final security engine because its targeted real-world stress evaluation was lower.

## 🛡️ Security Engine V2

The final prototype uses a layered security engine rather than relying on a single machine-learning prediction.

It combines:

- Feature-based Random Forest prediction
- Raw URL model prediction
- URL structure analysis
- Security-sensitive keyword detection
- Strong URL indicators
- Path and query complexity
- Known-domain context

The engine produces a numerical risk score and human-readable reasons.

## 🌐 Chrome Extension

The Chrome extension provides the user-facing security layer.

### Normal Flow

```text
User navigates to URL
        ↓
PhishGuard analyzes URL
        ↓
SAFE / SUSPICIOUS / PHISHING
```

### Phishing Flow

```text
User navigates to URL
        ↓
PhishGuard detects PHISHING
        ↓
Navigation redirected to warning page
        ↓
User sees risk score + reasons
        ↓
Go Back / Continue Anyway
```

The extension performs URL-level navigation interception and warning. It is **not a network-level firewall or DNS blocker**.

## 📊 Evaluation

The final Security Engine V2 was evaluated using controlled test cases.

| Evaluation | Result |
|---|---:|
| Controlled evaluation | **29/30 (96.67%)** |
| Manual URL tests | **11/12 (91.67%)** |
| Real-site tests | **10/10 (100%)** |
| Controlled phishing tests | **8/8 (100%)** |

The controlled evaluation had **0% false-positive rate on the tested benign URLs**.

A remaining synthetic stress case was intentionally retained instead of tuning the system specifically to force a positive result.

## 📚 Datasets

### PhishTank

PhishTank was used as a source of verified online phishing URLs.

https://www.phishtank.org/

### LegitPhish

Legitimate URL data was obtained from the LegitPhish dataset.

https://data.mendeley.com/datasets/hx4m73v2sf/2

### Tranco

Tranco's ranking was used as known-domain context rather than as a safe allowlist.

https://tranco-list.eu/

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/abhirajmaurya1456/secure-world-hackathon.git
cd secure-world-hackathon
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## 🔌 API

### Analyze a URL

```http
POST /analyze
```

Example request:

```json
{
  "url": "https://www.youtube.com/"
}
```

The API returns the URL, verdict, risk level, risk score, model probabilities, known-domain information, detected indicators, explanations, and extracted features.

## 🧩 Chrome Extension Setup

1. Open Chrome.
2. Go to:

```text
chrome://extensions/
```

3. Enable **Developer mode**.
4. Select **Load unpacked**.
5. Select:

```text
frontend/extension/
```

6. Pin PhishGuard to the Chrome toolbar.

The extension is configured to use the deployed PhishGuard backend.

## 🌍 Live Backend

Backend:

https://phishguard-backend-h2bo.onrender.com

API documentation:

https://phishguard-backend-h2bo.onrender.com/docs

## 🏪 Chrome Web Store

The PhishGuard Chrome extension has been submitted for Chrome Web Store review.

The public store link will be added here after publication.

## 🔐 Privacy

PhishGuard sends website URLs to its backend over HTTPS for security analysis.

The extension does not intentionally collect passwords, payment information, keystrokes, or webpage form contents.

See the complete privacy policy:

https://github.com/abhirajmaurya1456/secure-world-hackathon/blob/main/PRIVACY_POLICY.md

## ⚠️ Limitations

PhishGuard performs URL-level analysis.

A malicious webpage hosted on a legitimate-looking domain may not contain sufficient malicious signals in its URL to be detected.

Therefore, PhishGuard does not guarantee detection of every phishing page.

Webpage-content analysis, browser behavior analysis, and additional threat-intelligence sources are possible future extensions.

## 🔮 Future Scope

- Webpage/content analysis
- HTML and JavaScript behavior analysis
- Additional threat-intelligence sources
- Improved adversarial robustness
- More diverse real-world datasets
- Browser-based behavioral detection
- More extensive continuous evaluation

## 📁 Project Structure

```text
secure-world-hackathon/
├── backend/
│   └── main.py
├── data/
│   ├── model/
│   ├── processed/
│   ├── raw/
│   └── test/
├── frontend/
│   └── extension/
├── ml/
├── presentation/
├── PRIVACY_POLICY.md
├── README.md
└── requirements.txt
```

## 🛠️ Tech Stack

- Python
- Scikit-learn
- Pandas
- NumPy
- FastAPI
- Uvicorn
- Chrome Extensions Manifest V3
- JavaScript
- HTML/CSS
- Random Forest
- Logistic Regression
- Character-level TF-IDF

## 🎯 Project Goal

PhishGuard was developed as a security research prototype for the **Secure World — Trust Nothing. Protect Everything.** hackathon.

The project focuses on combining machine learning with deterministic security reasoning to make phishing detection more explainable and actionable for users.

## 📄 License

This project is intended for educational, research, and hackathon purposes.
