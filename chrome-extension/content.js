/**
 * Form Filling Assistant - Enhanced Content Script
 * Advanced form detection and auto-fill with fuzzy matching
 */

// Import field matcher (loaded via manifest)
// const { findBestMatch, validateValue, getFieldSignals } = window.FieldMatcher;

// Configuration
const CONFIG = {
  minConfidence: 0.3,
  highlightDuration: 3000,
  showConfidenceIndicator: true,
  partialFillMode: false, // Only fill high-confidence matches
  partialFillThreshold: 0.7,
  debugMode: true // Enable detailed logging
};

// Logging utility
const Logger = {
  prefix: '[Form Filler]',
  
  debug(...args) {
    if (CONFIG.debugMode) {
      console.log(`%c${this.prefix} DEBUG`, 'color: #888', ...args);
    }
  },
  
  info(...args) {
    console.log(`%c${this.prefix}`, 'color: #667eea; font-weight: bold', ...args);
  },
  
  success(...args) {
    console.log(`%c${this.prefix} ✓`, 'color: #28a745; font-weight: bold', ...args);
  },
  
  warn(...args) {
    console.warn(`%c${this.prefix} ⚠`, 'color: #ffc107; font-weight: bold', ...args);
  },
  
  error(...args) {
    console.error(`%c${this.prefix} ✗`, 'color: #dc3545; font-weight: bold', ...args);
  },
  
  table(data, title = '') {
    if (CONFIG.debugMode) {
      if (title) console.log(`%c${this.prefix} ${title}`, 'color: #667eea; font-weight: bold');
      console.table(data);
    }
  },
  
  group(name) {
    if (CONFIG.debugMode) console.group(`${this.prefix} ${name}`);
  },
  
  groupEnd() {
    if (CONFIG.debugMode) console.groupEnd();
  }
};

// Audit log for filled fields
const auditLog = [];

/**
 * Get all fillable form elements on the page
 */
function getAllFormElements() {
  const elements = [];
  const selectors = [
    'input[type="text"]',
    'input[type="email"]',
    'input[type="tel"]',
    'input[type="number"]',
    'input[type="date"]',
    'input[type="password"]',
    'input:not([type])',
    'textarea',
    'select',
    'input[type="radio"]',
    'input[type="checkbox"]'
  ];
  
  // Also check iframes
  const iframes = document.querySelectorAll('iframe');
  const iframeDocs = [];
  
  iframes.forEach(iframe => {
    try {
      if (iframe.contentDocument) {
        iframeDocs.push(iframe.contentDocument);
      }
    } catch (e) {
      // Cross-origin iframe, skip
    }
  });
  
  // Get elements from main document
  document.querySelectorAll(selectors.join(', ')).forEach(el => {
    if (isElementVisible(el) && !el.disabled && !el.readOnly) {
      elements.push({ element: el, source: 'main' });
    }
  });
  
  // Get elements from accessible iframes
  iframeDocs.forEach(doc => {
    doc.querySelectorAll(selectors.join(', ')).forEach(el => {
      if (isElementVisible(el) && !el.disabled && !el.readOnly) {
        elements.push({ element: el, source: 'iframe' });
      }
    });
  });
  
  return elements;
}

/**
 * Check if element is visible
 */
function isElementVisible(el) {
  if (el.type === 'hidden') return false;
  if (el.offsetParent === null && el.type !== 'radio' && el.type !== 'checkbox') return false;
  
  const style = window.getComputedStyle(el);
  if (style.display === 'none' || style.visibility === 'hidden') return false;
  
  return true;
}

/**
 * Fill a text input or textarea
 */
function fillTextInput(element, value, confidence) {
  element.value = value;
  element.dispatchEvent(new Event('input', { bubbles: true }));
  element.dispatchEvent(new Event('change', { bubbles: true }));
  element.dispatchEvent(new Event('blur', { bubbles: true }));
  
  highlightField(element, confidence);
  return true;
}

/**
 * Fill a date input
 */
function fillDateInput(element, value) {
  // Parse various date formats
  const datePatterns = [
    /(\d{2})[\/\-](\d{2})[\/\-](\d{4})/,  // DD/MM/YYYY or DD-MM-YYYY
    /(\d{4})[\/\-](\d{2})[\/\-](\d{2})/,  // YYYY/MM/DD or YYYY-MM-DD
    /(\d{2})\s+(\w{3})\s+(\d{4})/,        // DD MMM YYYY
  ];
  
  let isoDate = null;
  
  for (const pattern of datePatterns) {
    const match = value.match(pattern);
    if (match) {
      let day, month, year;
      
      if (pattern === datePatterns[0]) {
        day = match[1];
        month = match[2];
        year = match[3];
      } else if (pattern === datePatterns[1]) {
        year = match[1];
        month = match[2];
        day = match[3];
      } else {
        day = match[1];
        const monthStr = match[2].toLowerCase();
        const months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                       'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
        const monthIdx = months.findIndex(m => monthStr.startsWith(m));
        month = String(monthIdx + 1).padStart(2, '0');
        year = match[3];
      }
      
      isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
      break;
    }
  }
  
  if (isoDate) {
    element.value = isoDate;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }
  
  return false;
}

/**
 * Fill a select dropdown
 */
function fillSelect(element, value) {
  const options = Array.from(element.options);
  const valueLower = value.toString().toLowerCase().trim();
  
  // Try exact match first
  let match = options.find(opt => 
    opt.value.toLowerCase() === valueLower ||
    opt.text.toLowerCase().trim() === valueLower
  );
  
  // Try partial match
  if (!match) {
    match = options.find(opt => 
      opt.value.toLowerCase().includes(valueLower) ||
      opt.text.toLowerCase().includes(valueLower) ||
      valueLower.includes(opt.value.toLowerCase()) ||
      valueLower.includes(opt.text.toLowerCase().trim())
    );
  }
  
  // Fuzzy match for gender-like fields
  if (!match && ['male', 'female', 'm', 'f'].includes(valueLower)) {
    const genderMap = { 'male': ['male', 'm', 'man'], 'female': ['female', 'f', 'woman'], 
                        'm': ['male', 'm', 'man'], 'f': ['female', 'f', 'woman'] };
    const searchTerms = genderMap[valueLower] || [valueLower];
    
    match = options.find(opt => 
      searchTerms.some(term => 
        opt.value.toLowerCase().includes(term) ||
        opt.text.toLowerCase().includes(term)
      )
    );
  }
  
  // State/country fuzzy matching
  if (!match && window.FieldMatcher) {
    match = options.reduce((best, opt) => {
      const sim = Math.max(
        window.FieldMatcher.similarity(opt.value.toLowerCase(), valueLower),
        window.FieldMatcher.similarity(opt.text.toLowerCase(), valueLower)
      );
      if (sim > 0.7 && sim > (best?.similarity || 0)) {
        return { option: opt, similarity: sim };
      }
      return best;
    }, null)?.option;
  }
  
  if (match) {
    element.value = match.value;
    element.dispatchEvent(new Event('change', { bubbles: true }));
    highlightField(element, 0.8);
    return true;
  }
  
  return false;
}

/**
 * Fill radio buttons
 */
function fillRadioButton(element, value, allElements) {
  const name = element.name;
  if (!name) return false;
  
  // Get all radio buttons with this name
  const radios = allElements
    .filter(({ element: el }) => el.type === 'radio' && el.name === name)
    .map(({ element }) => element);
  
  if (radios.length === 0) return false;
  
  const valueLower = value.toString().toLowerCase().trim();
  
  // Try to find matching radio
  let matchingRadio = radios.find(radio => {
    const radioValue = radio.value.toLowerCase();
    const labelText = getLabelText(radio).toLowerCase();
    
    return radioValue === valueLower ||
           labelText.includes(valueLower) ||
           valueLower.includes(radioValue) ||
           (window.FieldMatcher && window.FieldMatcher.similarity(radioValue, valueLower) > 0.7) ||
           (window.FieldMatcher && window.FieldMatcher.similarity(labelText, valueLower) > 0.7);
  });
  
  // Gender-specific matching
  if (!matchingRadio && ['male', 'female', 'm', 'f'].includes(valueLower)) {
    const genderMap = { 'male': ['male', 'm'], 'female': ['female', 'f'], 'm': ['male', 'm'], 'f': ['female', 'f'] };
    const searchTerms = genderMap[valueLower] || [valueLower];
    
    matchingRadio = radios.find(radio => {
      const radioValue = radio.value.toLowerCase();
      const labelText = getLabelText(radio).toLowerCase();
      return searchTerms.some(term => 
        radioValue.includes(term) || labelText.includes(term)
      );
    });
  }
  
  if (matchingRadio) {
    matchingRadio.checked = true;
    matchingRadio.dispatchEvent(new Event('change', { bubbles: true }));
    matchingRadio.dispatchEvent(new Event('click', { bubbles: true }));
    highlightField(matchingRadio, 0.8);
    return true;
  }
  
  return false;
}

/**
 * Fill checkbox
 */
function fillCheckbox(element, value) {
  const valueLower = value.toString().toLowerCase().trim();
  const shouldCheck = ['yes', 'true', '1', 'on', 'checked', 'agree'].includes(valueLower);
  
  if (element.checked !== shouldCheck) {
    element.checked = shouldCheck;
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.dispatchEvent(new Event('click', { bubbles: true }));
    highlightField(element, 0.7);
    return true;
  }
  
  return false;
}

/**
 * Get label text for an element
 */
function getLabelText(element) {
  // Check for id-linked label
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) return label.textContent.trim();
  }
  
  // Check parent label
  const parentLabel = element.closest('label');
  if (parentLabel) return parentLabel.textContent.trim();
  
  // Check aria-label
  if (element.getAttribute('aria-label')) {
    return element.getAttribute('aria-label');
  }
  
  return '';
}

/**
 * Highlight a filled field
 */
function highlightField(element, confidence) {
  // Determine color based on confidence
  let color;
  if (confidence >= 0.8) {
    color = '#4caf50'; // Green - high confidence
  } else if (confidence >= 0.5) {
    color = '#ff9800'; // Orange - medium confidence
  } else {
    color = '#2196f3'; // Blue - low confidence
  }
  
  // Store original styles
  const originalBorder = element.style.border;
  const originalBoxShadow = element.style.boxShadow;
  const originalOutline = element.style.outline;
  
  // Apply highlight
  element.style.border = `2px solid ${color}`;
  element.style.boxShadow = `0 0 8px ${color}40`;
  element.style.outline = 'none';
  
  // Add confidence badge if enabled
  if (CONFIG.showConfidenceIndicator) {
    showConfidenceBadge(element, confidence);
  }
  
  // Remove highlight after duration
  setTimeout(() => {
    element.style.border = originalBorder;
    element.style.boxShadow = originalBoxShadow;
    element.style.outline = originalOutline;
  }, CONFIG.highlightDuration);
}

/**
 * Show confidence badge near element
 */
function showConfidenceBadge(element, confidence) {
  const badge = document.createElement('div');
  badge.className = 'form-filler-confidence-badge';
  badge.textContent = `${Math.round(confidence * 100)}%`;
  badge.style.cssText = `
    position: absolute;
    background: ${confidence >= 0.8 ? '#4caf50' : confidence >= 0.5 ? '#ff9800' : '#2196f3'};
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    z-index: 999999;
    pointer-events: none;
  `;
  
  const rect = element.getBoundingClientRect();
  badge.style.left = `${rect.right + window.scrollX + 5}px`;
  badge.style.top = `${rect.top + window.scrollY}px`;
  
  document.body.appendChild(badge);
  
  setTimeout(() => {
    badge.remove();
  }, CONFIG.highlightDuration);
}

/**
 * Main auto-fill function
 */
function autofill(data, options = {}) {
  const mergedConfig = { ...CONFIG, ...options };
  const allElements = getAllFormElements();
  let filledCount = 0;
  const fillResults = [];
  const processedRadioNames = new Set();
  const matchingMetrics = [];
  
  Logger.group('Auto-Fill Session');
  Logger.info(`Found ${allElements.length} form elements`);
  Logger.debug('Data keys:', Object.keys(data));
  Logger.debug('Options:', mergedConfig);
  
  for (const { element, source } of allElements) {
    // Skip already processed radio groups
    if (element.type === 'radio' && processedRadioNames.has(element.name)) {
      continue;
    }
    
    // Use advanced field matcher if available
    let match = null;
    if (window.FieldMatcher) {
      match = window.FieldMatcher.findBestMatch(element, data);
    } else {
      // Fallback to simple matching
      match = simpleMatch(element, data);
    }
    
    // Log matching attempt
    matchingMetrics.push({
      element: element.name || element.id || element.type,
      matchedKey: match.dataKey,
      confidence: match.confidence,
      matchedOn: match.matchedOn?.join(', ') || 'none'
    });
    
    if (!match.dataKey || match.confidence < mergedConfig.minConfidence) {
      Logger.debug(`Skipped: ${element.name || element.id} - confidence ${(match.confidence * 100).toFixed(1)}% < threshold`);
      continue;
    }
    
    // Check partial fill mode
    if (mergedConfig.partialFillMode && match.confidence < mergedConfig.partialFillThreshold) {
      Logger.debug(`Skipped (partial mode): ${match.dataKey} - confidence below threshold`);
      continue;
    }
    
    const value = data[match.dataKey];
    if (!value) continue;
    
    // Validate value format
    if (window.FieldMatcher && !window.FieldMatcher.validateValue(match.dataKey, value)) {
      Logger.warn(`Validation failed for ${match.dataKey}: "${value}"`);
      continue;
    }
    
    let filled = false;
    
    // Fill based on element type
    if (element.tagName === 'SELECT') {
      filled = fillSelect(element, value);
    } else if (element.type === 'radio') {
      filled = fillRadioButton(element, value, allElements);
      if (filled) processedRadioNames.add(element.name);
    } else if (element.type === 'checkbox') {
      filled = fillCheckbox(element, value);
    } else if (element.type === 'date') {
      filled = fillDateInput(element, value);
      if (filled) highlightField(element, match.confidence);
    } else {
      filled = fillTextInput(element, value, match.confidence);
    }
    
    if (filled) {
      filledCount++;
      
      const result = {
        field: match.dataKey,
        value: value,
        confidence: match.confidence,
        matchedOn: match.matchedOn,
        elementType: element.tagName.toLowerCase(),
        source: source,
        timestamp: new Date().toISOString()
      };
      
      fillResults.push(result);
      auditLog.push(result);
      
      Logger.success(`Filled ${match.dataKey} = "${value.substring(0, 20)}${value.length > 20 ? '...' : ''}" (${Math.round(match.confidence * 100)}% confidence)`);
    }
  }
  
  // Log summary
  Logger.info(`Fill complete: ${filledCount}/${allElements.length} fields`);
  Logger.table(matchingMetrics.filter(m => m.confidence > 0), 'Matching Metrics');
  Logger.groupEnd();
  
  return { 
    filledCount, 
    results: fillResults,
    totalFields: allElements.length,
    metrics: matchingMetrics
  };
}

/**
 * Simple fallback matcher
 */
function simpleMatch(element, data) {
  const name = (element.name || '').toLowerCase();
  const id = (element.id || '').toLowerCase();
  const placeholder = (element.placeholder || '').toLowerCase();
  
  for (const dataKey of Object.keys(data)) {
    const keyLower = dataKey.toLowerCase().replace(/_/g, '');
    
    if (name.includes(keyLower) || keyLower.includes(name.replace(/[^a-z]/g, '')) ||
        id.includes(keyLower) || keyLower.includes(id.replace(/[^a-z]/g, '')) ||
        placeholder.includes(keyLower)) {
      return { dataKey, confidence: 0.5, matchedOn: ['simple'] };
    }
  }
  
  return { dataKey: null, confidence: 0, matchedOn: [] };
}

/**
 * Undo last auto-fill
 */
function undoLastFill() {
  // TODO: Implement undo functionality
  console.log('[Form Filler] Undo not yet implemented');
}

/**
 * Get audit log
 */
function getAuditLog() {
  return [...auditLog];
}

/**
 * Clear audit log
 */
function clearAuditLog() {
  auditLog.length = 0;
}

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'autofill' && message.data) {
    const result = autofill(message.data, message.options || {});
    sendResponse(result);
  } else if (message.action === 'getAuditLog') {
    sendResponse({ log: getAuditLog() });
  } else if (message.action === 'clearAuditLog') {
    clearAuditLog();
    sendResponse({ success: true });
  } else if (message.action === 'detectFields') {
    const elements = getAllFormElements();
    const fieldInfo = elements.map(({ element }) => ({
      type: element.type || element.tagName.toLowerCase(),
      name: element.name,
      id: element.id,
      placeholder: element.placeholder
    }));
    sendResponse({ fields: fieldInfo, count: fieldInfo.length });
  }
  return true;
});

/**
 * Keyboard shortcut handler
 */
document.addEventListener('keydown', (e) => {
  // Ctrl+Shift+F to trigger auto-fill
  if (e.ctrlKey && e.shiftKey && e.key === 'F') {
    e.preventDefault();
    // Request data from popup/background
    chrome.runtime.sendMessage({ action: 'requestAutofill' }, (response) => {
      if (response && response.data) {
        autofill(response.data);
      }
    });
  }
});

/**
 * Add floating button for quick access
 */
function addFloatingButton() {
  // Check if form exists
  const forms = document.querySelectorAll('form, input, select');
  if (forms.length < 2) return;
  
  // Check if button already exists
  if (document.getElementById('form-filler-fab')) return;
  
  const btn = document.createElement('div');
  btn.id = 'form-filler-fab';
  btn.innerHTML = '🇮🇳';
  btn.title = 'Form Filling Assistant (Ctrl+Shift+F)';
  document.body.appendChild(btn);
  
  btn.addEventListener('click', () => {
    // Show mini menu
    showQuickMenu(btn);
  });
}

/**
 * Show quick menu on FAB click
 */
function showQuickMenu(fabElement) {
  // Remove existing menu
  const existingMenu = document.getElementById('form-filler-menu');
  if (existingMenu) {
    existingMenu.remove();
    return;
  }
  
  const menu = document.createElement('div');
  menu.id = 'form-filler-menu';
  menu.innerHTML = `
    <div class="ffm-item" data-action="open-popup">📂 Open Extension</div>
    <div class="ffm-item" data-action="detect">🔍 Detect Fields</div>
    <div class="ffm-item" data-action="help">❓ Help</div>
  `;
  menu.style.cssText = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 999999;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
  `;
  
  document.body.appendChild(menu);
  
  menu.querySelectorAll('.ffm-item').forEach(item => {
    item.style.cssText = `
      padding: 12px 16px;
      cursor: pointer;
      border-bottom: 1px solid #eee;
      transition: background 0.2s;
    `;
    item.addEventListener('mouseenter', () => item.style.background = '#f5f5f5');
    item.addEventListener('mouseleave', () => item.style.background = 'white');
    
    item.addEventListener('click', () => {
      const action = item.dataset.action;
      menu.remove();
      
      if (action === 'open-popup') {
        alert('Click the extension icon in the toolbar to open the popup.');
      } else if (action === 'detect') {
        const elements = getAllFormElements();
        alert(`Found ${elements.length} fillable form fields on this page.`);
      } else if (action === 'help') {
        alert('Form Filling Assistant\n\nShortcuts:\n• Ctrl+Shift+F: Auto-fill\n\nClick the extension icon to select a profile and fill forms.');
      }
    });
  });
  
  // Close menu when clicking outside
  setTimeout(() => {
    document.addEventListener('click', function closeMenu(e) {
      if (!menu.contains(e.target) && e.target !== fabElement) {
        menu.remove();
        document.removeEventListener('click', closeMenu);
      }
    });
  }, 100);
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addFloatingButton);
} else {
  addFloatingButton();
}

console.log('[Form Filler] Enhanced content script loaded');
