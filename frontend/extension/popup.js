const API_URL = "https://phishguard-backend-h2bo.onrender.com/analyze";
const urlElement = document.getElementById("url");
const statusElement = document.getElementById("status");
const resultElement = document.getElementById("result");
const verdictElement = document.getElementById("verdict");
const riskScoreElement = document.getElementById("riskScore");
const probabilityElement = document.getElementById("probability");
const reasonsElement = document.getElementById("reasons");
const analyzeButton = document.getElementById("analyzeBtn");


// ------------------------------------------------------------
// Get current tab
// ------------------------------------------------------------

async function getCurrentTab() {

    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    return tabs[0];
}


// ------------------------------------------------------------
// Display result
// ------------------------------------------------------------

function displayResult(data) {

    resultElement.style.display = "block";

    verdictElement.textContent = data.verdict;

    verdictElement.className = "";

    if (data.verdict === "SAFE") {
        verdictElement.classList.add("safe");
    }

    else if (data.verdict === "SUSPICIOUS") {
        verdictElement.classList.add("suspicious");
    }

    else if (data.verdict === "PHISHING") {
        verdictElement.classList.add("phishing");
    }


    riskScoreElement.textContent =
        `Risk Score: ${data.risk_score}/100`;


    probabilityElement.textContent =
        `RF Probability: ${data.rf_probability}% | Raw URL Probability: ${data.raw_probability}%`;


    reasonsElement.innerHTML = "";


    data.reasons.forEach(reason => {

        const li = document.createElement("li");

        li.textContent = reason;

        reasonsElement.appendChild(li);

    });
}


// ------------------------------------------------------------
// Load stored result
// ------------------------------------------------------------

async function loadStoredResult(tab) {

    const stored = await chrome.storage.local.get(
        `tab_${tab.id}`
    );

    const data = stored[`tab_${tab.id}`];


    if (!data) {

        statusElement.textContent =
            "No automatic analysis available yet.";

        return false;
    }


    urlElement.textContent = data.url;

    displayResult(data);

    statusElement.textContent =
        "Automatically analyzed.";

    return true;
}


// ------------------------------------------------------------
// Manual analysis
// ------------------------------------------------------------

async function analyzeURL() {

    statusElement.textContent =
        "Analyzing...";

    resultElement.style.display =
        "none";

    analyzeButton.disabled =
        true;


    try {

        const tab = await getCurrentTab();

        const url = tab.url;

        urlElement.textContent =
            url;


        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    url: url
                })
            }
        );


        if (!response.ok) {
            throw new Error(
                "API request failed"
            );
        }


        const data =
            await response.json();


        // Save the manually generated result
        await chrome.storage.local.set({
            [`tab_${tab.id}`]: data
        });


        displayResult(data);


        statusElement.textContent =
            "Analysis complete.";

    }

    catch (error) {

        console.error(error);

        statusElement.textContent =
            "Could not connect to PhishGuard API.";

    }

    finally {

        analyzeButton.disabled =
            false;
    }
}


// ------------------------------------------------------------
// Initialize popup
// ------------------------------------------------------------

async function initializePopup() {

    try {

        const tab =
            await getCurrentTab();

        urlElement.textContent =
            tab.url;

        const loaded =
            await loadStoredResult(tab);


        if (!loaded) {

            statusElement.textContent =
                "Analyzing current URL...";

            await analyzeURL();
        }

    }

    catch (error) {

        console.error(error);

        statusElement.textContent =
            "Could not load current tab.";

    }
}


// ------------------------------------------------------------
// Button
// ------------------------------------------------------------

analyzeButton.addEventListener(
    "click",
    analyzeURL
);


// ------------------------------------------------------------
// Start
// ------------------------------------------------------------

initializePopup();