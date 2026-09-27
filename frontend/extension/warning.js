const urlElement =
    document.getElementById("url");

const riskScoreElement =
    document.getElementById("riskScore");

const reasonsElement =
    document.getElementById("reasons");

const backButton =
    document.getElementById("backButton");

const continueButton =
    document.getElementById("continueButton");


const params =
    new URLSearchParams(
        window.location.search
    );

const tabId =
    Number(params.get("tabId"));


// --------------------------------------------------
// LOAD WARNING DATA
// --------------------------------------------------

async function loadWarningData() {

    if (!tabId) {
        return;
    }

    const stored =
        await chrome.storage.local.get(
            `tab_${tabId}`
        );

    const data =
        stored[`tab_${tabId}`];

    if (!data) {
        return;
    }

    urlElement.textContent =
        data.url;

    riskScoreElement.textContent =
        `Risk Score: ${data.risk_score}/100`;

    reasonsElement.innerHTML = "";

    data.reasons.forEach(reason => {

        const li =
            document.createElement("li");

        li.textContent =
            reason;

        reasonsElement.appendChild(li);
    });
}


// --------------------------------------------------
// GO BACK
// --------------------------------------------------

backButton.addEventListener(
    "click",
    () => {

        console.log(
            "🟡 WARNING PAGE: GO_BACK clicked"
        );

        chrome.runtime.sendMessage({

            type: "GO_BACK",

            tabId: tabId

        });

    }
);


// --------------------------------------------------
// CONTINUE ANYWAY
// --------------------------------------------------

continueButton.addEventListener(
    "click",
    () => {

        console.log(
            "🟢 WARNING PAGE: CONTINUE_ANYWAY clicked"
        );

        chrome.runtime.sendMessage({

            type: "CONTINUE_ANYWAY",

            tabId: tabId,

            url:
                urlElement.textContent

        });

    }
);


// --------------------------------------------------
// INITIALIZE
// --------------------------------------------------

console.log(
    "🔥 PhishGuard warning.js NEW VERSION LOADED"
);

console.log(
    "Tab ID:",
    tabId
);

loadWarningData();