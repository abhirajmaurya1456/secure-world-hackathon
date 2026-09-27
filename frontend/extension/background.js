console.log("🔥 PhishGuard background.js LOADED");

const API_URL = "https://phishguard-backend-h2bo.onrender.com/analyze";


// ============================================================
// ANALYZE URL
// ============================================================

async function analyzeURL(url) {

    try {

        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url
            })
        });


        if (!response.ok) {

            throw new Error(
                `API error: ${response.status}`
            );
        }


        return await response.json();

    } catch (error) {

        console.error(
            "PhishGuard API error:",
            error
        );

        return null;
    }
}


// ============================================================
// UPDATE EXTENSION BADGE
// ============================================================

function updateBadge(tabId, data) {

    if (data.verdict === "PHISHING") {

        chrome.action.setBadgeText({
            tabId: tabId,
            text: "!"
        });

        chrome.action.setBadgeBackgroundColor({
            tabId: tabId,
            color: "#d93025"
        });

    }

    else if (data.verdict === "SUSPICIOUS") {

        chrome.action.setBadgeText({
            tabId: tabId,
            text: "?"
        });

        chrome.action.setBadgeBackgroundColor({
            tabId: tabId,
            color: "#f9ab00"
        });

    }

    else {

        chrome.action.setBadgeText({
            tabId: tabId,
            text: ""
        });
    }
}


// ============================================================
// MESSAGE HANDLER
// ============================================================

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (!message || !message.type) {
            return;
        }


        // ========================================================
        // CONTINUE ANYWAY
        // ========================================================

        if (message.type === "CONTINUE_ANYWAY") {

            const tabId =
                Number(message.tabId);

            const url =
                message.url;

            const bypassKey =
                `bypass_${tabId}`;


            console.log(
                "➡️ Continue Anyway requested:",
                tabId,
                url
            );


            // ----------------------------------------------------
            // Store a persistent tab-level bypass.
            //
            // It remains active while this tab stays on the
            // same URL.
            // ----------------------------------------------------

            chrome.storage.local.set({

                [bypassKey]: {

                    url: url,

                    timestamp: Date.now()

                }

            }).then(() => {

                console.log(
                    "🟢 Bypass stored:",
                    bypassKey
                );


                // ------------------------------------------------
                // Navigate only after bypass has been stored.
                // ------------------------------------------------

                chrome.tabs.update(
                    tabId,
                    {
                        url: url
                    }
                );

            }).catch(error => {

                console.error(
                    "Could not store bypass:",
                    error
                );

            });


            sendResponse({
                success: true
            });


            return true;
        }


        // ========================================================
        // GO BACK
        // ========================================================

        if (message.type === "GO_BACK") {

            const tabId =
                Number(message.tabId);


            console.log(
                "↩️ Go Back requested:",
                tabId
            );


            const safeKey =
                `lastSafe_${tabId}`;


            chrome.storage.local.get(
                safeKey
            ).then(async (result) => {

                const safeData =
                    result[safeKey];


                // ------------------------------------------------
                // CASE 1:
                // We have a known SAFE page.
                // ------------------------------------------------

                if (
                    safeData &&
                    safeData.url
                ) {

                    console.log(
                        "↩️ Returning to last safe URL:",
                        safeData.url
                    );


                    try {

                        await chrome.tabs.update(
                            tabId,
                            {
                                url: safeData.url
                            }
                        );


                    } catch (error) {

                        console.error(
                            "Could not navigate to safe URL:",
                            error
                        );
                    }


                    return;
                }


                // ------------------------------------------------
                // CASE 2:
                // No saved safe URL.
                // Try browser history.
                // ------------------------------------------------

                console.log(
                    "⚠️ No last safe URL available."
                );


                console.log(
                    "↩️ Trying browser history..."
                );


                try {

                    await chrome.tabs.goBack(
                        tabId
                    );


                } catch (historyError) {

                    console.log(
                        "⚠️ Browser history unavailable."
                    );


                    // ------------------------------------------------
                    // CASE 3:
                    // Nothing to go back to.
                    //
                    // Close the warning tab.
                    // ------------------------------------------------

                    console.log(
                        "🗑️ Closing warning tab."
                    );


                    try {

                        await chrome.tabs.remove(
                            tabId
                        );

                    } catch (closeError) {

                        console.error(
                            "Could not close tab:",
                            closeError
                        );
                    }
                }

            }).catch(error => {

                console.error(
                    "Go Back failed:",
                    error
                );

            });


            sendResponse({
                success: true
            });


            return true;
        }

    }
);


// ============================================================
// ON COMMITTED
// ============================================================
//
// This runs after a navigation has actually committed.
//
// We use this to remember SAFE pages for the Back button.
// ============================================================

chrome.webNavigation.onCommitted.addListener(
    async (details) => {

        // Only main frame
        if (details.frameId !== 0) {
            return;
        }


        const tabId =
            details.tabId;

        const url =
            details.url;


        // --------------------------------------------------------
        // Ignore browser/internal pages
        // --------------------------------------------------------

        if (
            url.startsWith("chrome://") ||
            url.startsWith("chrome-extension://") ||
            url.startsWith("edge://") ||
            url.startsWith("about:") ||
            url.startsWith("devtools://")
        ) {

            return;
        }


        // --------------------------------------------------------
        // Check Continue-Anyway bypass
        // --------------------------------------------------------

        const bypassKey =
            `bypass_${tabId}`;


        const bypassResult =
            await chrome.storage.local.get(
                bypassKey
            );


        const bypass =
            bypassResult[bypassKey];


        if (
            bypass &&
            bypass.url === url
        ) {

            console.log(
                "🟢 Continue-Anyway URL committed:",
                url
            );


            // IMPORTANT:
            // Do not save this URL as lastSafe.
            return;
        }


        // --------------------------------------------------------
        // Analyze the committed URL.
        // --------------------------------------------------------

        const data =
            await analyzeURL(url);


        if (!data) {
            return;
        }


        console.log(
            "📌 Committed URL result:",
            url,
            data.verdict
        );


        // --------------------------------------------------------
        // Only SAFE URLs become lastSafe.
        // --------------------------------------------------------

        if (data.verdict === "SAFE") {

            await chrome.storage.local.set({

                [`lastSafe_${tabId}`]: {

                    url: url,

                    timestamp: Date.now()

                }

            });


            console.log(
                "💾 Last safe navigation:",
                tabId,
                url
            );
        }

    }
);


// ============================================================
// NAVIGATION DETECTOR
// ============================================================
//
// onBeforeNavigate is used because we want to react as soon
// as the browser starts navigating to a URL.
// ============================================================

chrome.webNavigation.onBeforeNavigate.addListener(
    async (details) => {

        // Only main frame
        if (details.frameId !== 0) {
            return;
        }


        const tabId =
            details.tabId;

        const url =
            details.url;


        // --------------------------------------------------------
        // Ignore browser/internal pages
        // --------------------------------------------------------

        if (
            url.startsWith("chrome://") ||
            url.startsWith("chrome-extension://") ||
            url.startsWith("edge://") ||
            url.startsWith("about:") ||
            url.startsWith("devtools://")
        ) {

            return;
        }


        // ========================================================
        // CONTINUE ANYWAY BYPASS
        // ========================================================

        const bypassKey =
            `bypass_${tabId}`;


        const bypassResult =
            await chrome.storage.local.get(
                bypassKey
            );


        const bypass =
            bypassResult[bypassKey];


        if (bypass) {

            const sameURL =
                bypass.url === url;


            if (sameURL) {

                console.log(
                    "🟢 BYPASS ACCEPTED"
                );

                console.log(
                    "Allowed URL:",
                    url
                );


                // IMPORTANT:
                //
                // Do NOT remove the bypass here.
                //
                // The user explicitly chose Continue Anyway.
                // Multiple navigation events may occur.
                //
                // The bypass stays active for this tab + URL.
                //

                return;
            }


            // ----------------------------------------------------
            // Different URL:
            // user navigated somewhere else.
            // Clear old bypass.
            // ----------------------------------------------------

            console.log(
                "🔄 New URL detected. Clearing old bypass."
            );


            await chrome.storage.local.remove(
                bypassKey
            );
        }


        // ========================================================
        // ANALYZE URL
        // ========================================================

        console.log(
            "🔍 PhishGuard analyzing:",
            url
        );


        const data =
            await analyzeURL(url);


        if (!data) {
            return;
        }


        console.log(
            "🔍 PhishGuard result:",
            data
        );


        // ========================================================
        // SAVE ANALYSIS RESULT
        // ========================================================

        await chrome.storage.local.set({

            [`tab_${tabId}`]: data

        });


        // ========================================================
        // UPDATE BADGE
        // ========================================================

        updateBadge(
            tabId,
            data
        );


        // ========================================================
        // PHISHING WARNING
        // ========================================================

        if (data.verdict === "PHISHING") {

            console.log(
                "🚨 PHISHING DETECTED"
            );


            // ----------------------------------------------------
            // Get last SAFE URL
            // ----------------------------------------------------

            const safeKey =
                `lastSafe_${tabId}`;


            const safeResult =
                await chrome.storage.local.get(
                    safeKey
                );


            const safeData =
                safeResult[safeKey];


            console.log(
                "Previous safe page:",
                safeData
                    ? safeData.url
                    : "NONE"
            );


            // ----------------------------------------------------
            // Save warning information
            // ----------------------------------------------------

            await chrome.storage.local.set({

                [`warning_${tabId}`]: {

                    phishingUrl: url,

                    previousUrl:
                        safeData
                            ? safeData.url
                            : "",

                    timestamp: Date.now()

                }

            });


            // ----------------------------------------------------
            // Warning page
            // ----------------------------------------------------

            const warningURL =
                chrome.runtime.getURL(
                    "warning.html"
                ) +
                "?tabId=" +
                encodeURIComponent(tabId);


            console.log(
                "⚠️ Opening warning page:",
                warningURL
            );


            chrome.tabs.update(
                tabId,
                {
                    url: warningURL
                }
            );
        }

    }
);


// ============================================================
// TAB CLOSED
// ============================================================
//
// Clean up all PhishGuard state associated with a closed tab.
// ============================================================

chrome.tabs.onRemoved.addListener(
    async (tabId) => {

        console.log(
            "🗑️ Cleaning PhishGuard data for tab:",
            tabId
        );


        await chrome.storage.local.remove([

            `tab_${tabId}`,

            `warning_${tabId}`,

            `lastSafe_${tabId}`,

            `bypass_${tabId}`

        ]);

    }
);