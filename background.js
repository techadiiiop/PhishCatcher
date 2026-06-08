// Cache to avoid repeated analysis of same URL
const analysisCache = new Map();

// Listen for page navigation
chrome.webNavigation.onCompleted.addListener(async (details) => {
  // Skip Chrome internal pages
  if (details.url.startsWith('chrome://') || details.url.startsWith('edge://')) {
    return;
  }

  // Check cache (60 seconds)
  const cached = analysisCache.get(details.url);
  if (cached && (Date.now() - cached.timestamp) < 60000) {
    console.log('Using cached result for:', details.url);
    handleAnalysisResult(details.tabId, details.url, cached.result);
    return;
  }

  try {
    console.log('Analyzing URL:', details.url);
    
    // Call Flask backend
    const response = await fetch('http://localhost:5000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: details.url })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('Analysis result:', result);

    // Cache the result
    analysisCache.set(details.url, {
      timestamp: Date.now(),
      result: result
    });

    // Store for popup
    await chrome.storage.local.set({
      [`analysis_${details.tabId}`]: result,
      lastAnalysis: result
    });

    // Handle the result (show warning, redirect)
    handleAnalysisResult(details.tabId, details.url, result);

  } catch (error) {
    console.error('Analysis failed:', error);
  }
});

// Function to handle analysis results
function handleAnalysisResult(tabId, url, result) {
  if (!result.is_phishing) {
    console.log('Safe site, no action needed');
    return;
  }

  console.log('PHISHING DETECTED! Confidence:', result.confidence);

  // Send message to content script to show warning
  const warningType = result.confidence >= 0.7 ? 'PHISHING_WARNING' : 'SUSPICIOUS_WARNING';
  
  chrome.tabs.sendMessage(tabId, {
    type: warningType,
    confidence: result.confidence,
    is_phishing: result.is_phishing
  }).catch(err => console.log('Content script not ready yet:', err));

  // If high confidence, redirect to decoy after 3 seconds
  if (result.confidence >= 0.7) {
    setTimeout(() => {
      chrome.tabs.update(tabId, {
        url: `http://localhost:5000/decoy?redirect=${encodeURIComponent(url)}`
      });
    }, 3000);
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'MANUAL_SCAN') {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (tab) {
        // Manually trigger analysis
        try {
          const response = await fetch('http://localhost:5000/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: tab.url })
          });
          const result = await response.json();
          await chrome.storage.local.set({ [`analysis_${tab.id}`]: result });
          sendResponse({ success: true, result: result });
        } catch (error) {
          sendResponse({ success: false, error: error.message });
        }
      }
    });
    return true; // Keep channel open for async response
  }
  
  if (message.type === 'GET_ANALYSIS') {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      const key = `analysis_${tab.id}`;
      const data = await chrome.storage.local.get(key);
      sendResponse({ analysis: data[key] || null });
    });
    return true;
  }
});

// Clean up cache occasionally (every hour)
setInterval(() => {
  const now = Date.now();
  for (const [url, data] of analysisCache) {
    if (now - data.timestamp > 3600000) { // 1 hour
      analysisCache.delete(url);
    }
  }
}, 3600000);

console.log('PhishCatcher background service worker started');