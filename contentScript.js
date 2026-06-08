// Create and show warning overlay
function showWarningOverlay(confidence, isHighRisk) {
  // Remove existing overlay if present
  const existing = document.getElementById('phishcatcher-overlay');
  if (existing) {
    existing.remove();
  }

  // Create overlay div
  const overlay = document.createElement('div');
  overlay.id = 'phishcatcher-overlay';
  overlay.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 999999;
    background: ${isHighRisk ? '#dc2626' : '#f59e0b'};
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    max-width: 320px;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
  `;

  const confidencePercent = Math.round(confidence * 100);
  const title = isHighRisk ? '🚨 PHISHING DETECTED!' : '⚠️ Suspicious Page';
  const message = isHighRisk 
    ? 'This page appears to be a phishing attempt. Redirecting to safe page...' 
    : 'This page shows suspicious patterns. Be careful!';

  overlay.innerHTML = `
    <div style="display: flex; align-items: flex-start; gap: 12px;">
      <span style="font-size: 28px;">${isHighRisk ? '🚨' : '⚠️'}</span>
      <div style="flex: 1;">
        <strong style="font-size: 15px;">${title}</strong>
        <div style="font-size: 12px; margin-top: 4px;">${message}</div>
        <div style="font-size: 11px; margin-top: 8px; opacity: 0.8;">
          Confidence: ${confidencePercent}%
        </div>
      </div>
      <div style="font-size: 18px; cursor: pointer;">✕</div>
    </div>
  `;

  // Close on click anywhere
  overlay.addEventListener('click', (e) => {
    e.stopPropagation();
    overlay.remove();
  });

  document.body.appendChild(overlay);

  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (overlay.parentElement) {
      overlay.remove();
    }
  }, 10000);
}

// Add colored border to page for visual warning
function addPageBorder(isHighRisk) {
  const borderColor = isHighRisk ? '#dc2626' : '#f59e0b';
  const borderWidth = isHighRisk ? '4px' : '2px';
  
  const style = document.createElement('style');
  style.id = 'phishcatcher-border';
  style.textContent = `
    body {
      border: ${borderWidth} solid ${borderColor} !important;
      position: relative !important;
    }
    body::before {
      content: "${isHighRisk ? '⚠️ PHISHING SITE' : '⚠️ SUSPICIOUS'}";
      position: fixed;
      top: 0;
      left: 0;
      background: ${borderColor};
      color: white;
      padding: 4px 12px;
      font-size: 12px;
      font-family: monospace;
      z-index: 999999;
      border-radius: 0 0 8px 0;
    }
  `;
  
  const existing = document.getElementById('phishcatcher-border');
  if (existing) existing.remove();
  document.head.appendChild(style);
}

// Remove visual warnings
function removeWarnings() {
  const overlay = document.getElementById('phishcatcher-overlay');
  if (overlay) overlay.remove();
  
  const border = document.getElementById('phishcatcher-border');
  if (border) border.remove();
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received:', message.type);
  
  if (message.type === 'PHISHING_WARNING') {
    showWarningOverlay(message.confidence, true);
    addPageBorder(true);
  } else if (message.type === 'SUSPICIOUS_WARNING') {
    showWarningOverlay(message.confidence, false);
    addPageBorder(false);
  }
  
  sendResponse({ received: true });
});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
  removeWarnings();
});

console.log('PhishCatcher content script loaded');