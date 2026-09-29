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

## 📊 Evaluation & Testing

PhishGuard was developed using a large, realistic URL dataset containing **74,760 URLs**, followed by separate holdout evaluation and additional real-world/controlled tests.

### 1. Model Development Dataset

The primary dataset contains:

| Dataset | URLs |
|---|---:|
| Legitimate URLs | **37,380** |
| Phishing URLs | **37,380** |
| **Total** | **74,760** |

The phishing URLs were sampled from **77,321 unique verified phishing URLs** collected from PhishTank. The legitimate URLs came from the legitimate subset of **LegitPhish v2**, providing naturally occurring paths and query strings rather than only simple domain-only URLs.

This balanced dataset was used for model development and evaluation.

### 2. ML Model Evaluation

The feature-based Random Forest model used a **hostname-aware train/test split** to reduce domain leakage:

- Total dataset: **74,760 URLs**
- Training set: **62,143 URLs**
- Holdout test set: **12,617 URLs**
- Features: **19 URL-based security features**
- Model: Random Forest, 300 trees

**Random Forest results:**

- Accuracy: **98.89%**
- Precision: **98.95%**
- Recall: **98.33%**
- F1 Score: **98.64%**

Additional modelling approaches were also evaluated on the realistic URL dataset:

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Feature-based Random Forest | **98.89%** | 98.95% | 98.33% | 98.64% |
| Raw URL Character Model | **99.01%** | 99.76% | 97.81% | 98.78% |
| Region-aware Model | **99.13%** | 99.61% | 98.26% | **98.93%** |

The region-aware model achieved the highest benchmark F1 score, but it was **not directly used as the production decision model**. The final Security Engine V2 instead combines complementary model signals with deterministic security indicators and known-domain context.

### 3. Final Security Engine Validation

After model development, a **separate controlled validation set of 30 URLs** was used to evaluate the complete Security Engine V2.

These 30 URLs were **not used to train the models**.

The final validation set contained:

- **17 benign URLs**
- **13 phishing / phishing-like URLs**
- **30 URLs total**

Results:

| Evaluation | Result |
|---|---:|
| Final controlled evaluation | **29/30 (96.67%)** |
| Manual URL tests | **11/12 (91.67%)** |
| Real-site tests | **10/10 (100%)** |
| Controlled phishing tests | **8/8 (100%)** |

For the 30-URL controlled evaluation:

- **29/30** URLs were classified correctly.
- **12/13** phishing/phishing-like URLs were detected.
- **17/17** tested benign URLs avoided a `PHISHING` verdict.
- False-positive rate on the tested benign URLs: **0.00%**.

One synthetic stress case was intentionally retained as a false negative rather than tuning the system specifically to force a positive result.

### 4. What These Numbers Mean

The **98.89% / 99.01% / 99.13%** figures are ML benchmark results obtained from the large **74,760-URL dataset and its holdout evaluation**.

The **96.67%** figure is the result of a separate **30-URL controlled end-to-end validation of Security Engine V2**.

The controlled evaluation is intended to measure how the complete security engine behaves on selected manual, real-site, and controlled phishing scenarios. It is not presented as a general real-world accuracy estimate.

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

The PhishGuard Chrome extension is publicly available on the Chrome Web Store.

**Install PhishGuard:**  
https://chromewebstore.google.com/detail/PhishGuard/anmjpjchoalbckbfecimhfemklbfmmbm

The extension is available for free use and can be installed directly from the Chrome Web Store.

## Live Demo

PhishGuard includes a static web demo that provides a simple user-facing interface for testing the deployed detection engine.

**Demo:** https://abhirajmaurya1456.github.io/secure-world-hackathon/

The demo allows users to:
- Enter a URL and analyze it
- View SAFE, SUSPICIOUS, or PHISHING verdicts
- View risk score and risk level
- See ML model signals and explainable detection reasons
- Test predefined safe and controlled phishing URLs

The static demo is implemented in `index.html` and communicates with the deployed FastAPI backend on Render.

For details about the static demo page and its deployment, see [`DEMO_PAGE_README.md`](DEMO_PAGE_README.md).

> Note: The demo page itself is static; URL analysis is performed by the deployed PhishGuard backend.

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
├── index.html          
├── DEMO_PAGE_README.md 
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
