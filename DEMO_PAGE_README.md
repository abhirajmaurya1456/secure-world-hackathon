# PhishGuard Demo Page

`index.html` is a static demo interface created for the Bit & Build / Secure World hackathon submission.

It sends a user-entered URL to the deployed PhishGuard FastAPI backend and displays the verdict, risk score, model signals, known-domain context, and explanation.

Backend endpoint:

https://phishguard-backend-h2bo.onrender.com/analyze

This page is separate from the Chrome extension UI and is intended to provide a simple public demo URL for judges.

## Chrome Extension

The full PhishGuard browser extension is also publicly available on the Chrome Web Store.

**Install PhishGuard:**  
https://chromewebstore.google.com/detail/PhishGuard/anmjpjchoalbckbfecimhfemklbfmmbm

The extension provides automatic protection by analyzing URLs during browser navigation and displaying a warning before navigating to URLs classified as PHISHING.