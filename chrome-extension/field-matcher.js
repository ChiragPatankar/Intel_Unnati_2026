/**
 * Advanced Field Matcher with Fuzzy Matching
 * Uses multiple signals to detect and match form fields
 */

// Levenshtein distance for fuzzy matching
function levenshteinDistance(a, b) {
  const matrix = [];
  
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[b.length][a.length];
}

// Calculate similarity score (0-1)
function similarity(a, b) {
  if (!a || !b) return 0;
  a = a.toLowerCase().trim();
  b = b.toLowerCase().trim();
  if (a === b) return 1;
  
  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) return 1;
  
  const distance = levenshteinDistance(a, b);
  return 1 - distance / maxLen;
}

// Comprehensive field name mappings with variations
const FIELD_DATABASE = {
  // Name fields
  name: {
    aliases: ['name', 'full_name', 'fullname', 'your_name', 'applicant_name', 
              'customer_name', 'user_name', 'username', 'complete_name', 'holder_name',
              'account_holder', 'beneficiary_name', 'subscriber_name', 'member_name'],
    patterns: [/^name$/i, /full.*name/i, /your.*name/i, /applicant/i, /holder.*name/i],
    labels: ['name', 'full name', 'your name', 'applicant name', 'customer name'],
    priority: 10
  },
  first_name: {
    aliases: ['first_name', 'firstname', 'fname', 'given_name', 'givenname', 
              'forename', 'first', 'f_name'],
    patterns: [/first.*name/i, /given.*name/i, /fname/i, /^first$/i, /forename/i],
    labels: ['first name', 'given name', 'forename'],
    priority: 9
  },
  last_name: {
    aliases: ['last_name', 'lastname', 'lname', 'surname', 'family_name', 
              'familyname', 'last', 'l_name'],
    patterns: [/last.*name/i, /sur.*name/i, /family.*name/i, /lname/i, /^last$/i],
    labels: ['last name', 'surname', 'family name'],
    priority: 9
  },
  middle_name: {
    aliases: ['middle_name', 'middlename', 'mname', 'middle'],
    patterns: [/middle.*name/i, /mname/i, /^middle$/i],
    labels: ['middle name', 'middle initial'],
    priority: 8
  },
  father_name: {
    aliases: ['father_name', 'fathername', 'fathers_name', 'father', 
              'guardian_name', 'guardian', 'parent_name', 'father_husband_name',
              'so_of', 'son_of', 'daughter_of', 'do_of', 'wo_of', 'wife_of'],
    patterns: [/father/i, /guardian/i, /parent.*name/i, /s\/o/i, /d\/o/i, /w\/o/i],
    labels: ["father's name", 'father name', 'guardian name', "parent's name", 
             's/o', 'd/o', 'w/o', "father/husband's name"],
    priority: 8
  },
  mother_name: {
    aliases: ['mother_name', 'mothername', 'mothers_name', 'mother'],
    patterns: [/mother/i],
    labels: ["mother's name", 'mother name'],
    priority: 8
  },
  spouse_name: {
    aliases: ['spouse_name', 'spousename', 'husband_name', 'wife_name', 'partner_name'],
    patterns: [/spouse/i, /husband/i, /wife/i, /partner/i],
    labels: ["spouse's name", 'spouse name', "husband's name", "wife's name"],
    priority: 7
  },
  
  // Date fields
  dob: {
    aliases: ['dob', 'date_of_birth', 'dateofbirth', 'birthdate', 'birth_date',
              'birthday', 'bday', 'birth', 'date_birth'],
    patterns: [/date.*birth/i, /birth.*date/i, /^dob$/i, /birthday/i, /bday/i],
    labels: ['date of birth', 'dob', 'birthday', 'birth date', 'd.o.b'],
    priority: 10
  },
  
  // ID fields
  aadhaar: {
    aliases: ['aadhaar', 'aadhaar_number', 'aadhar', 'aadhar_number', 'uid', 
              'uidai', 'aadhaar_no', 'aadhar_no', 'unique_id', 'aadhaarno'],
    patterns: [/aadhaar/i, /aadhar/i, /^uid$/i, /uidai/i, /unique.*id/i],
    labels: ['aadhaar number', 'aadhaar no', 'aadhar number', 'uid', 'uidai number'],
    priority: 10
  },
  pan: {
    aliases: ['pan', 'pan_number', 'pannumber', 'pan_no', 'panno', 
              'permanent_account_number', 'income_tax_pan'],
    patterns: [/^pan$/i, /pan.*number/i, /pan.*no/i, /permanent.*account/i],
    labels: ['pan number', 'pan no', 'pan card number', 'permanent account number'],
    priority: 10
  },
  voter_id: {
    aliases: ['voter_id', 'voterid', 'epic', 'epic_number', 'voter', 
              'voter_number', 'election_id', 'epic_no', 'voter_card'],
    patterns: [/voter/i, /^epic$/i, /election.*id/i],
    labels: ['voter id', 'voter id number', 'epic', 'election id'],
    priority: 9
  },
  passport: {
    aliases: ['passport', 'passport_number', 'passport_no', 'passportno', 
              'passport_num', 'travel_document'],
    patterns: [/passport/i, /travel.*document/i],
    labels: ['passport number', 'passport no', 'passport'],
    priority: 9
  },
  driving_license: {
    aliases: ['driving_license', 'drivinglicense', 'dl', 'dl_number', 
              'license_number', 'licence_number', 'driving_licence', 'dlno'],
    patterns: [/driving.*licen[sc]e/i, /^dl$/i, /licen[sc]e.*number/i],
    labels: ['driving license', 'driving licence', 'dl number', 'license number'],
    priority: 9
  },
  
  // Address fields
  address: {
    aliases: ['address', 'full_address', 'residential_address', 'permanent_address',
              'street_address', 'address1', 'address_line_1', 'addressline1',
              'correspondence_address', 'present_address', 'current_address', 'addr'],
    patterns: [/^address$/i, /full.*address/i, /street.*address/i, /address.*1/i, 
               /residential/i, /permanent.*address/i, /correspondence/i],
    labels: ['address', 'full address', 'street address', 'residential address',
             'permanent address', 'address line 1', 'correspondence address'],
    priority: 10
  },
  address2: {
    aliases: ['address2', 'address_line_2', 'addressline2', 'street2', 'apt', 
              'apartment', 'suite', 'unit', 'building', 'flat_no'],
    patterns: [/address.*2/i, /address.*line.*2/i, /apartment/i, /suite/i, /flat/i],
    labels: ['address line 2', 'apartment', 'suite', 'unit', 'flat no'],
    priority: 7
  },
  city: {
    aliases: ['city', 'town', 'district', 'municipality', 'village', 
              'city_name', 'place', 'locality'],
    patterns: [/^city$/i, /^town$/i, /district/i, /municipality/i],
    labels: ['city', 'town', 'district', 'city/town'],
    priority: 8
  },
  state: {
    aliases: ['state', 'province', 'region', 'state_name', 'state_province'],
    patterns: [/^state$/i, /province/i, /^region$/i],
    labels: ['state', 'province', 'state/province'],
    priority: 8
  },
  pincode: {
    aliases: ['pincode', 'pin', 'postal_code', 'postalcode', 'zip', 
              'zipcode', 'zip_code', 'pin_code', 'postcode', 'area_code'],
    patterns: [/pin.*code/i, /postal.*code/i, /^zip$/i, /^pin$/i, /post.*code/i],
    labels: ['pincode', 'pin code', 'postal code', 'zip code', 'pin'],
    priority: 9
  },
  country: {
    aliases: ['country', 'country_name', 'nation'],
    patterns: [/^country$/i, /nation/i],
    labels: ['country', 'country name'],
    priority: 6
  },
  
  // Contact fields
  email: {
    aliases: ['email', 'email_address', 'emailaddress', 'email_id', 'emailid',
              'e_mail', 'mail', 'user_email', 'contact_email'],
    patterns: [/email/i, /e-?mail/i, /mail.*id/i],
    labels: ['email', 'email address', 'e-mail', 'email id'],
    priority: 10
  },
  phone: {
    aliases: ['phone', 'mobile', 'phone_number', 'mobile_number', 'cell',
              'cellphone', 'telephone', 'contact', 'contact_number', 'tel',
              'phone_no', 'mobile_no', 'contact_no', 'mob', 'ph_no'],
    patterns: [/phone/i, /mobile/i, /cell/i, /telephone/i, /contact.*number/i, /^tel$/i],
    labels: ['phone number', 'mobile number', 'contact number', 'phone', 'mobile', 
             'telephone', 'cell phone'],
    priority: 10
  },
  
  // Other fields
  gender: {
    aliases: ['gender', 'sex', 'male_female'],
    patterns: [/^gender$/i, /^sex$/i],
    labels: ['gender', 'sex', 'male/female'],
    priority: 8
  },
  occupation: {
    aliases: ['occupation', 'profession', 'job', 'job_title', 'work', 
              'employment', 'designation', 'role'],
    patterns: [/occupation/i, /profession/i, /job.*title/i, /designation/i],
    labels: ['occupation', 'profession', 'job title', 'designation'],
    priority: 6
  },
  income: {
    aliases: ['income', 'annual_income', 'salary', 'earnings', 'monthly_income'],
    patterns: [/income/i, /salary/i, /earnings/i],
    labels: ['annual income', 'income', 'salary', 'monthly income'],
    priority: 5
  },
  nationality: {
    aliases: ['nationality', 'citizenship', 'citizen'],
    patterns: [/nationality/i, /citizenship/i],
    labels: ['nationality', 'citizenship'],
    priority: 6
  },
  marital_status: {
    aliases: ['marital_status', 'maritalstatus', 'married', 'marital'],
    patterns: [/marital/i, /married/i],
    labels: ['marital status', 'married/single'],
    priority: 6
  },
  bank_account: {
    aliases: ['bank_account', 'account_number', 'accountnumber', 'bank_acc',
              'acc_no', 'account_no', 'acct_number'],
    patterns: [/bank.*account/i, /account.*number/i, /acc.*no/i],
    labels: ['bank account', 'account number', 'bank account number'],
    priority: 7
  },
  ifsc: {
    aliases: ['ifsc', 'ifsc_code', 'bank_code', 'ifsccode'],
    patterns: [/ifsc/i, /bank.*code/i],
    labels: ['ifsc code', 'ifsc', 'bank ifsc'],
    priority: 7
  }
};

/**
 * Get all text signals from a form field
 */
function getFieldSignals(element) {
  const signals = {
    name: (element.name || '').toLowerCase(),
    id: (element.id || '').toLowerCase(),
    placeholder: (element.placeholder || '').toLowerCase(),
    ariaLabel: (element.getAttribute('aria-label') || '').toLowerCase(),
    autocomplete: (element.getAttribute('autocomplete') || '').toLowerCase(),
    dataField: (element.getAttribute('data-field') || '').toLowerCase(),
    className: (element.className || '').toLowerCase(),
    label: '',
    parentText: '',
    siblingText: ''
  };
  
  // Get associated label
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) {
      signals.label = label.textContent.toLowerCase().trim();
    }
  }
  
  // Check parent label
  const parentLabel = element.closest('label');
  if (parentLabel) {
    signals.label = parentLabel.textContent.toLowerCase().trim();
  }
  
  // Get parent div text (often contains label-like text)
  const parent = element.parentElement;
  if (parent) {
    const parentClone = parent.cloneNode(true);
    // Remove input elements to get only text
    parentClone.querySelectorAll('input, select, textarea').forEach(el => el.remove());
    signals.parentText = parentClone.textContent.toLowerCase().trim().slice(0, 100);
  }
  
  // Get previous sibling text
  let sibling = element.previousElementSibling;
  if (sibling) {
    signals.siblingText = sibling.textContent.toLowerCase().trim().slice(0, 50);
  }
  
  return signals;
}

/**
 * Calculate match score for a field against a data key
 */
function calculateMatchScore(signals, fieldConfig) {
  let score = 0;
  let matchedOn = [];
  
  const allSignalTexts = [
    signals.name,
    signals.id,
    signals.placeholder,
    signals.ariaLabel,
    signals.autocomplete,
    signals.dataField,
    signals.label,
    signals.parentText,
    signals.siblingText
  ].filter(Boolean);
  
  // Check exact alias matches
  for (const alias of fieldConfig.aliases) {
    if (signals.name === alias) { score += 100; matchedOn.push('name-exact'); }
    if (signals.id === alias) { score += 90; matchedOn.push('id-exact'); }
    if (signals.autocomplete === alias) { score += 95; matchedOn.push('autocomplete-exact'); }
    
    // Check for alias in other signals
    if (signals.placeholder.includes(alias)) { score += 60; matchedOn.push('placeholder'); }
    if (signals.label.includes(alias)) { score += 70; matchedOn.push('label'); }
    if (signals.ariaLabel.includes(alias)) { score += 65; matchedOn.push('aria-label'); }
  }
  
  // Check pattern matches
  for (const pattern of fieldConfig.patterns) {
    for (const text of allSignalTexts) {
      if (pattern.test(text)) {
        score += 50;
        matchedOn.push('pattern');
      }
    }
  }
  
  // Check label text matches
  for (const labelText of fieldConfig.labels) {
    const sim = similarity(signals.label, labelText);
    if (sim > 0.8) { score += sim * 80; matchedOn.push('label-fuzzy'); }
    
    const simParent = similarity(signals.parentText, labelText);
    if (simParent > 0.7) { score += simParent * 40; matchedOn.push('parent-fuzzy'); }
    
    const simSibling = similarity(signals.siblingText, labelText);
    if (simSibling > 0.8) { score += simSibling * 50; matchedOn.push('sibling-fuzzy'); }
  }
  
  // Fuzzy matching on name/id
  for (const alias of fieldConfig.aliases) {
    const nameSim = similarity(signals.name, alias);
    const idSim = similarity(signals.id, alias);
    
    if (nameSim > 0.7) { score += nameSim * 60; matchedOn.push('name-fuzzy'); }
    if (idSim > 0.7) { score += idSim * 55; matchedOn.push('id-fuzzy'); }
  }
  
  // Apply priority weight
  score *= (fieldConfig.priority / 10);
  
  return { score, matchedOn };
}

/**
 * Find best matching data key for a field
 */
function findBestMatch(element, data) {
  const signals = getFieldSignals(element);
  let bestMatch = null;
  let bestScore = 0;
  let bestMatchedOn = [];
  
  // Debug logging
  const DEBUG = true;
  if (DEBUG && signals.name) {
    console.log(`%c[FieldMatcher] Analyzing: ${signals.name || signals.id || 'unnamed'}`, 
      'color: #888', { signals });
  }
  
  for (const [dataKey, value] of Object.entries(data)) {
    if (!value) continue;
    
    // Find field config that matches this data key
    for (const [fieldType, fieldConfig] of Object.entries(FIELD_DATABASE)) {
      if (fieldConfig.aliases.includes(dataKey.toLowerCase()) || fieldType === dataKey.toLowerCase()) {
        const { score, matchedOn } = calculateMatchScore(signals, fieldConfig);
        
        if (score > bestScore && score > 30) { // Minimum threshold
          bestScore = score;
          bestMatch = dataKey;
          bestMatchedOn = matchedOn;
        }
      }
    }
  }
  
  // Also try direct matching with data keys
  for (const [dataKey, value] of Object.entries(data)) {
    if (!value) continue;
    
    const dataKeyLower = dataKey.toLowerCase().replace(/_/g, '');
    const signalTexts = [signals.name, signals.id, signals.placeholder, signals.label];
    
    for (const text of signalTexts) {
      const textClean = text.replace(/[^a-z]/g, '');
      const sim = similarity(textClean, dataKeyLower);
      if (sim > 0.75 && sim * 100 > bestScore) {
        bestScore = sim * 100;
        bestMatch = dataKey;
        bestMatchedOn = ['direct-fuzzy'];
      }
    }
  }
  
  // Log match result
  if (bestMatch && bestScore > 30) {
    console.log(`%c[FieldMatcher] Match found: ${signals.name || signals.id} → ${bestMatch} (score: ${bestScore.toFixed(1)}, via: ${bestMatchedOn.join(', ')})`,
      'color: #28a745');
  }
  
  return { 
    dataKey: bestMatch, 
    score: bestScore,
    confidence: Math.min(bestScore / 100, 1),
    matchedOn: bestMatchedOn 
  };
}

/**
 * Validate value format before filling
 */
function validateValue(dataKey, value) {
  const validators = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^[\d\s\-\+\(\)]{10,15}$/,
    mobile: /^[\d\s\-\+\(\)]{10,15}$/,
    pincode: /^\d{6}$/,
    pan: /^[A-Z]{5}\d{4}[A-Z]$/i,
    aadhaar: /^\d{12}$/,
    aadhaar_number: /^\d{12}$/,
    dob: /^\d{2}[\/\-]\d{2}[\/\-]\d{4}$|^\d{4}[\/\-]\d{2}[\/\-]\d{2}$/,
    ifsc: /^[A-Z]{4}0[A-Z0-9]{6}$/i
  };
  
  const keyLower = dataKey.toLowerCase();
  for (const [type, regex] of Object.entries(validators)) {
    if (keyLower.includes(type)) {
      // Clean value for validation
      const cleanValue = value.toString().replace(/\s/g, '');
      return regex.test(cleanValue);
    }
  }
  
  return true; // No validation rule, assume valid
}

// Export for use in content script
if (typeof window !== 'undefined') {
  window.FieldMatcher = {
    findBestMatch,
    validateValue,
    getFieldSignals,
    similarity,
    FIELD_DATABASE
  };
}

