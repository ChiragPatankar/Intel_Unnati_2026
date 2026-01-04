/**
 * API service for backend communication
 * With comprehensive logging for debugging
 */

const API_BASE = '/api/v1';

// API Logger
const apiLogger = {
  logRequest(method, url, body = null) {
    console.group(`%c🌐 API ${method}`, 'color: #667eea; font-weight: bold');
    console.log('URL:', url);
    if (body) console.log('Body:', body);
    console.time('Request Duration');
  },
  
  logResponse(response, data) {
    console.timeEnd('Request Duration');
    console.log('Status:', response.status, response.statusText);
    console.log('Response:', data);
    console.groupEnd();
  },
  
  logError(error) {
    console.timeEnd('Request Duration');
    console.error('Error:', error);
    console.groupEnd();
  }
};

/**
 * Upload document and extract entities with enhanced confidence scoring
 */
export async function extractEntities(file) {
  const formData = new FormData();
  formData.append('file', file);

  apiLogger.logRequest('POST', `${API_BASE}/document/extract-entities-enhanced`, { file: file.name });
  
  const response = await fetch(`${API_BASE}/document/extract-entities-enhanced`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Upload failed');
  }

  const data = await response.json();
  apiLogger.logResponse(response, data);
  
  // Log OCR quality metrics
  if (data.timing) {
    console.log('%c📊 OCR Metrics', 'color: #ff9800; font-weight: bold', {
      ocrTime: `${data.timing.ocr_time_ms}ms`,
      extractionTime: `${data.timing.extraction_time_ms}ms`,
      totalTime: `${data.timing.total_time_ms}ms`,
      entitiesFound: Object.keys(data.entities || {}).length,
      overallConfidence: `${(data.overall_confidence * 100).toFixed(1)}%`,
      needsReview: data.needs_review
    });
  }
  
  return data;
}

/**
 * Get available form templates (NEW - for government forms)
 */
export async function getFormTemplates() {
  apiLogger.logRequest('GET', `${API_BASE}/forms/templates`);
  
  const response = await fetch(`${API_BASE}/forms/templates`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch templates' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Failed to fetch templates');
  }
  
  const data = await response.json();
  apiLogger.logResponse(response, data);
  return data;
}

/**
 * Get details of a specific form template
 */
export async function getFormTemplate(formId) {
  apiLogger.logRequest('GET', `${API_BASE}/forms/templates/${formId}`);
  
  const response = await fetch(`${API_BASE}/forms/templates/${formId}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Template not found' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Template not found');
  }
  
  const data = await response.json();
  apiLogger.logResponse(response, data);
  return data;
}

/**
 * Upload document and map to form fields (all-in-one)
 */
export async function uploadAndMapToForm(formId, file) {
  const formData = new FormData();
  formData.append('file', file);

  apiLogger.logRequest('POST', `${API_BASE}/forms/upload-and-map/${formId}`, { file: file.name });
  
  const response = await fetch(`${API_BASE}/forms/upload-and-map/${formId}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload and mapping failed' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Upload and mapping failed');
  }

  const data = await response.json();
  apiLogger.logResponse(response, data);
  return data;
}

/**
 * Map extracted data to form fields
 */
export async function mapDataToForm(formId, extractedData) {
  apiLogger.logRequest('POST', `${API_BASE}/forms/map-data/${formId}`, extractedData);
  
  const response = await fetch(`${API_BASE}/forms/map-data/${formId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(extractedData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Mapping failed' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Mapping failed');
  }

  const data = await response.json();
  apiLogger.logResponse(response, data);
  return data;
}

/**
 * Generate filled PDF form
 */
export async function generateFilledForm(formId, formData) {
  apiLogger.logRequest('POST', `${API_BASE}/forms/generate/${formId}`, formData);
  
  const response = await fetch(`${API_BASE}/forms/generate/${formId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'PDF generation failed' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'PDF generation failed');
  }

  // Return blob for preview (don't auto-download)
  const blob = await response.blob();
  apiLogger.logResponse(response, { blob_size: blob.size });
  
  // Create blob URL for preview
  const url = window.URL.createObjectURL(blob);
  const filename = `${formId}_filled_form.pdf`;
  
  // Return blob URL and filename instead of auto-downloading
  return { 
    success: true, 
    filename: filename,
    blobUrl: url,
    blob: blob // Keep blob reference for cleanup
  };
}

// =============================================================================
// PROFILE API
// =============================================================================

/**
 * List all profiles
 */
export async function listProfiles() {
  const response = await fetch(`${API_BASE}/profile/list`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch profiles');
  }

  return response.json();
}

/**
 * Get a profile by ID
 */
export async function getProfile(profileId) {
  const response = await fetch(`${API_BASE}/profile/${profileId}`);
  
  if (!response.ok) {
    throw new Error('Profile not found');
  }

  return response.json();
}

/**
 * Create a new profile
 */
export async function createProfile(name, fields = null) {
  const body = { name, fields };
  apiLogger.logRequest('POST', `${API_BASE}/profile/create`, body);
  
  const response = await fetch(`${API_BASE}/profile/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create profile' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Failed to create profile');
  }

  const data = await response.json();
  apiLogger.logResponse(response, data);
  return data;
}

/**
 * Update profile fields
 */
export async function updateProfile(profileId, fields) {
  const response = await fetch(`${API_BASE}/profile/${profileId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fields }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update profile' }));
    throw new Error(error.detail || 'Failed to update profile');
  }

  return response.json();
}

/**
 * Delete a profile
 */
export async function deleteProfile(profileId) {
  const response = await fetch(`${API_BASE}/profile/${profileId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete profile');
  }

  return response.json();
}

/**
 * Upload document to a profile
 */
export async function uploadDocumentToProfile(profileId, file) {
  const formData = new FormData();
  formData.append('file', file);

  apiLogger.logRequest('POST', `${API_BASE}/profile/${profileId}/upload-document`, { file: file.name });
  
  const response = await fetch(`${API_BASE}/profile/${profileId}/upload-document`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    apiLogger.logError(error);
    throw new Error(error.detail || 'Upload failed');
  }

  const data = await response.json();
  apiLogger.logResponse(response, data);
  
  // Log extraction quality
  console.log('%c📄 Document Extraction', 'color: #28a745; font-weight: bold', {
    documentType: data.document_type,
    fieldsExtracted: Object.keys(data.extracted_fields || {}).length,
    fields: data.extracted_fields
  });
  
  return data;
}

/**
 * Get autofill data for a profile
 */
export async function getAutofillData(profileId) {
  const response = await fetch(`${API_BASE}/profile/${profileId}/autofill`);
  
  if (!response.ok) {
    throw new Error('Failed to get autofill data');
  }

  return response.json();
}
