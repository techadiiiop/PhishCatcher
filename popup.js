// Load and display current analysis when popup opens
async function loadAnalysis() {
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab && tab.url) {
      // Display URL
      const urlElement = document.getElementById('siteUrl');
      if (urlElement) {
        let displayUrl = tab.url;
        if (displayUrl.length > 50) {
          displayUrl = displayUrl.substring(0, 47) + '...';
        }
        urlElement.textContent = displayUrl;
      }
      
      // Get stored analysis for this tab
      const key = `analysis_${tab.id}`;
      const result = await chrome.storage.local.get(key);
      const analysis = result[key];
      
      if (analysis && analysis.confidence !== undefined) {
        updateDisplay(analysis);
      } else {
        // No analysis yet
        document.getElementById('confidenceFill').style.width = '0%';
        document.getElementById('verdict').textContent = 'Not analyzed yet';
        document.getElementById('verdict').style.color = '#ffffff';
      }
    }
    
    // Load stats from local storage
    const totalAnalyzed = localStorage.getItem('totalAnalyzed') || '0';
    const totalThreats = localStorage.getItem('totalThreats') || '0';
    document.getElementById('totalAnalyzed').textContent = totalAnalyzed;
    document.getElementById('totalThreats').textContent = totalThreats;
    
  } catch (error) {
    console.error('Error loading analysis:', error);
    document.getElementById('siteUrl').textContent = 'Error loading';
  }
}

// Update the popup display with analysis result
function updateDisplay(analysis) {
  const confidencePercent = Math.round(analysis.confidence * 100);
  const confidenceFill = document.getElementById('confidenceFill');
  const verdictElement = document.getElementById('verdict');
  
  // Update confidence bar
  if (confidenceFill) {
    confidenceFill.style.width = `${confidencePercent}%`;
    
    // Change color based on confidence
    if (analysis.is_phishing) {
      confidenceFill.style.background = '#dc2626';
    } else if (confidencePercent > 50) {
      confidenceFill.style.background = '#f59e0b';
    } else {
      confidenceFill.style.background = '#22c55e';
    }
  }
  
  // Update verdict text
  if (analysis.is_phishing) {
    verdictElement.textContent = `⚠️ PHISHING DETECTED (${confidencePercent}%)`;
    verdictElement.style.color = '#fecaca';
  } else {
    verdictElement.textContent = `✅ Safe (${confidencePercent}% confidence)`;
    verdictElement.style.color = '#bbf7d0';
  }
  
  // Update stats
  let totalAnalyzed = parseInt(localStorage.getItem('totalAnalyzed') || '0');
  let totalThreats = parseInt(localStorage.getItem('totalThreats') || '0');
  
  totalAnalyzed++;
  if (analysis.is_phishing) {
    totalThreats++;
  }
  
  localStorage.setItem('totalAnalyzed', totalAnalyzed);
  localStorage.setItem('totalThreats', totalThreats);
  
  document.getElementById('totalAnalyzed').textContent = totalAnalyzed;
  document.getElementById('totalThreats').textContent = totalThreats;
}

// Manual scan button
document.getElementById('scanBtn').addEventListener('click', async () => {
  const scanBtn = document.getElementById('scanBtn');
  const originalText = scanBtn.textContent;
  scanBtn.textContent = '🔄 Scanning...';
  scanBtn.disabled = true;
  
  try {
    // Send message to background to trigger scan
    const response = await chrome.runtime.sendMessage({ type: 'MANUAL_SCAN' });
    
    if (response && response.success) {
      // Wait a moment for analysis to complete
      setTimeout(() => {
        loadAnalysis();
      }, 1500);
    } else {
      alert('Scan failed. Make sure Flask backend is running on localhost:5000');
    }
  } catch (error) {
    console.error('Scan error:', error);
    alert('Error: Make sure Flask backend is running (python app.py)');
  } finally {
    scanBtn.textContent = originalText;
    scanBtn.disabled = false;
  }
});

// Load analysis when popup opens
document.addEventListener('DOMContentLoaded', loadAnalysis);