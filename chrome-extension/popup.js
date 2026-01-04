/**
 * Form Filling Assistant - Enhanced Chrome Extension Popup
 */

const API_BASE = 'http://localhost:8000/api/v1';

// DOM Elements
const connectionStatus = document.getElementById('connection-status');
const statusText = document.querySelector('.status-text');
const themeToggle = document.getElementById('theme-toggle');
const securitySection = document.getElementById('security-section');
const mainContent = document.getElementById('main-content');
const passwordInput = document.getElementById('password-input');
const unlockBtn = document.getElementById('unlock-btn');
const unlockError = document.getElementById('unlock-error');
const profileSelect = document.getElementById('profile-select');
const refreshBtn = document.getElementById('refresh-btn');
const profileCard = document.getElementById('profile-card');
const profileName = document.getElementById('profile-name');
const profileDocs = document.getElementById('profile-docs');
const fieldsPreview = document.getElementById('fields-preview');
const lastUpdated = document.getElementById('last-updated');
const pageStats = document.getElementById('page-stats');
const detectedFields = document.getElementById('detected-fields');
const fillableFields = document.getElementById('fillable-fields');
const fillOptions = document.getElementById('fill-options');
const partialFill = document.getElementById('partial-fill');
const autofillBtn = document.getElementById('autofill-btn');
const detectBtn = document.getElementById('detect-btn');
const openWebappBtn = document.getElementById('open-webapp-btn');
const fillResults = document.getElementById('fill-results');
const fillCount = document.getElementById('fill-count');
const resultsDetails = document.getElementById('results-details');

// State
let currentProfile = null;
let autofillData = null;
let isLocked = false;

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// ============================================================================
// CONNECTION & SECURITY
// ============================================================================

async function checkConnection() {
  try {
    const response = await fetch(`${API_BASE.replace('/api/v1', '')}/health`);
    if (response.ok) {
      connectionStatus.classList.add('connected');
      connectionStatus.classList.remove('disconnected');
      statusText.textContent = 'Connected to server';
      return true;
    }
  } catch (e) {
    console.error('Connection error:', e);
  }
  
  connectionStatus.classList.add('disconnected');
  connectionStatus.classList.remove('connected');
  statusText.textContent = 'Server not running';
  return false;
}

async function checkSecurityStatus() {
  try {
    const response = await fetch(`${API_BASE}/security/status`);
    if (response.ok) {
      const status = await response.json();
      
      if (status.password_set && !status.unlocked) {
        // Show lock screen
        isLocked = true;
        securitySection.classList.remove('hidden');
        mainContent.classList.add('hidden');
        return false;
      }
    }
  } catch (e) {
    console.log('Security check skipped:', e.message);
  }
  
  // No password set or already unlocked
  isLocked = false;
  securitySection.classList.add('hidden');
  mainContent.classList.remove('hidden');
  return true;
}

async function unlockVault() {
  const password = passwordInput.value;
  if (!password) return;
  
  try {
    const response = await fetch(`${API_BASE}/security/unlock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ master_password: password })
    });
    
    if (response.ok) {
      isLocked = false;
      securitySection.classList.add('hidden');
      mainContent.classList.remove('hidden');
      unlockError.classList.add('hidden');
      loadProfiles();
    } else {
      unlockError.textContent = 'Invalid password';
      unlockError.classList.remove('hidden');
    }
  } catch (e) {
    unlockError.textContent = 'Connection error';
    unlockError.classList.remove('hidden');
  }
}

// ============================================================================
// PROFILES
// ============================================================================

async function loadProfiles() {
  try {
    const response = await fetch(`${API_BASE}/profile/list`);
    if (!response.ok) throw new Error('Failed to load profiles');
    
    const profiles = await response.json();
    
    profileSelect.innerHTML = '<option value="">-- Select a profile --</option>';
    
    profiles.forEach(profile => {
      const option = document.createElement('option');
      option.value = profile.id;
      option.textContent = `${profile.name} (${profile.field_count} fields)`;
      profileSelect.appendChild(option);
    });
    
    // Restore last selected profile
    const lastProfileId = localStorage.getItem('lastProfileId');
    if (lastProfileId) {
      profileSelect.value = lastProfileId;
      if (profileSelect.value) {
        loadProfileData(lastProfileId);
      }
    }
    
  } catch (e) {
    console.error('Error loading profiles:', e);
    profileSelect.innerHTML = '<option value="">No profiles found</option>';
  }
}

async function loadProfileData(profileId) {
  try {
    // Get full profile
    const profileResponse = await fetch(`${API_BASE}/profile/${profileId}`);
    if (!profileResponse.ok) throw new Error('Failed to load profile');
    const profile = await profileResponse.json();
    
    // Get autofill data
    const autofillResponse = await fetch(`${API_BASE}/profile/${profileId}/autofill`);
    if (!autofillResponse.ok) throw new Error('Failed to load autofill data');
    const autofill = await autofillResponse.json();
    
    currentProfile = profile;
    autofillData = autofill.fields;
    
    // Update UI
    profileCard.classList.remove('hidden');
    fillOptions.classList.remove('hidden');
    autofillBtn.disabled = false;
    
    profileName.textContent = profile.name;
    profileDocs.textContent = `${profile.documents?.length || 0} docs`;
    lastUpdated.textContent = `Updated: ${formatDate(profile.updated_at)}`;
    
    displayFieldsPreview(profile.fields);
    localStorage.setItem('lastProfileId', profileId);
    
    // Detect fields on current page
    detectPageFields();
    
  } catch (e) {
    console.error('Error loading profile:', e);
    profileCard.classList.add('hidden');
    autofillBtn.disabled = true;
  }
}

function displayFieldsPreview(fields) {
  fieldsPreview.innerHTML = '';
  
  const importantFields = ['full_name', 'dob', 'aadhaar_number', 'pan_number', 
                          'passport_number', 'driving_license', 'address', 'gender'];
  
  let shownCount = 0;
  
  for (const field of importantFields) {
    if (fields[field]) {
      const item = document.createElement('div');
      item.className = 'field-item';
      item.innerHTML = `
        <span class="field-name">${field.replace(/_/g, ' ')}</span>
        <span class="field-value">${maskSensitiveData(field, fields[field])}</span>
      `;
      fieldsPreview.appendChild(item);
      shownCount++;
    }
  }
  
  const totalFields = Object.keys(fields).length;
  if (totalFields > shownCount) {
    const more = document.createElement('div');
    more.className = 'field-item';
    more.innerHTML = `<span class="field-name" style="color: var(--accent)">+ ${totalFields - shownCount} more fields</span>`;
    fieldsPreview.appendChild(more);
  }
}

function maskSensitiveData(field, value) {
  if (!value) return value;
  
  if (field.includes('aadhaar') && value.length >= 12) {
    return 'XXXX XXXX ' + value.replace(/\s/g, '').slice(-4);
  }
  if (field.includes('pan') && value.length >= 10) {
    return value.slice(0, 3) + 'XXXXX' + value.slice(-2);
  }
  if (field.includes('bank_account') && value.length >= 9) {
    return 'XXXXX' + value.slice(-4);
  }
  return value;
}

function formatDate(dateStr) {
  if (!dateStr) return '--';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', { 
    day: 'numeric', 
    month: 'short', 
    year: 'numeric' 
  });
}

// ============================================================================
// PAGE DETECTION
// ============================================================================

async function detectPageFields() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Check if we can inject into this tab
    if (!tab || !tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) {
      console.log('Cannot detect fields on this type of page');
      pageStats.classList.add('hidden');
      return;
    }
    
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'detectFields' });
    
    if (response) {
      pageStats.classList.remove('hidden');
      detectedFields.textContent = response.count;
      
      // Estimate fillable based on data keys
      const fillable = autofillData ? 
        Math.min(response.count, Object.keys(autofillData).length) : 0;
      fillableFields.textContent = fillable;
    }
  } catch (e) {
    console.log('Could not detect fields:', e.message);
    // Show hint to reload the page
    if (e.message && e.message.includes('Receiving end does not exist')) {
      console.log('Content script not loaded. Refresh the page.');
    }
    pageStats.classList.add('hidden');
  }
}

// ============================================================================
// AUTO-FILL
// ============================================================================

async function triggerAutofill() {
  if (!autofillData) return;
  
  autofillBtn.textContent = '⏳ Filling...';
  autofillBtn.disabled = true;
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const options = {
      partialFillMode: partialFill.checked,
      partialFillThreshold: 0.7
    };
    
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'autofill',
      data: autofillData,
      options
    });
    
    if (response) {
      showFillResults(response);
      
      autofillBtn.textContent = '✅ Done!';
      setTimeout(() => {
        autofillBtn.textContent = '✨ Auto-Fill This Page';
        autofillBtn.disabled = false;
      }, 2000);
    }
    
  } catch (e) {
    console.error('Autofill error:', e);
    // Show more descriptive error
    let errorMsg = '❌ Error';
    if (e.message && e.message.includes('Receiving end does not exist')) {
      errorMsg = '❌ Reload page first';
    } else if (e.message && e.message.includes('Cannot access')) {
      errorMsg = '❌ Cannot fill this page';
    }
    autofillBtn.textContent = errorMsg;
    setTimeout(() => {
      autofillBtn.textContent = '✨ Auto-Fill This Page';
      autofillBtn.disabled = false;
    }, 3000);
  }
}

function showFillResults(response) {
  fillResults.classList.remove('hidden');
  fillCount.textContent = response.filledCount;
  
  resultsDetails.innerHTML = '';
  
  if (response.results) {
    response.results.slice(0, 5).forEach(result => {
      const item = document.createElement('div');
      item.className = 'result-item';
      item.innerHTML = `
        <span>${result.field.replace(/_/g, ' ')}</span>
        <span class="result-confidence">${Math.round(result.confidence * 100)}%</span>
      `;
      resultsDetails.appendChild(item);
    });
    
    if (response.results.length > 5) {
      const more = document.createElement('div');
      more.className = 'result-item';
      more.textContent = `+ ${response.results.length - 5} more`;
      resultsDetails.appendChild(more);
    }
  }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

themeToggle.addEventListener('click', toggleTheme);

unlockBtn.addEventListener('click', unlockVault);
passwordInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') unlockVault();
});

profileSelect.addEventListener('change', (e) => {
  const profileId = e.target.value;
  if (profileId) {
    loadProfileData(profileId);
  } else {
    profileCard.classList.add('hidden');
    fillOptions.classList.add('hidden');
    pageStats.classList.add('hidden');
    autofillBtn.disabled = true;
    currentProfile = null;
    autofillData = null;
  }
});

refreshBtn.addEventListener('click', loadProfiles);

detectBtn.addEventListener('click', detectPageFields);

autofillBtn.addEventListener('click', triggerAutofill);

openWebappBtn.addEventListener('click', () => {
  chrome.tabs.create({ url: 'http://localhost:5173' });
});

// ============================================================================
// INITIALIZE
// ============================================================================

async function init() {
  initTheme();
  
  const connected = await checkConnection();
  if (!connected) return;
  
  const unlocked = await checkSecurityStatus();
  if (unlocked) {
    await loadProfiles();
  }
}

init();
