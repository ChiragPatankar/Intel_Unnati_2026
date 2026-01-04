import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import FormTemplateSelector from './components/FormTemplateSelector';
import FormPreview from './components/FormPreview';
import VoiceInput from './components/VoiceInput';
import { uploadAndMapToForm, getFormTemplate, generateFilledForm } from './api';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary" style={{ padding: '40px', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'Unknown error'}</p>
          <button onClick={() => window.location.reload()} style={{ padding: '10px 20px', marginTop: '20px' }}>
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Available UI languages
const uiLanguages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
];

// Language translations
const translations = {
  en: {
    title: '🇮🇳 Seva Kendra - Form Filling Assistant',
    subtitle: 'Upload documents, auto-fill government forms, download PDF',
    selectFormType: 'Which form do you need?',
    selectFormSubtitle: 'Choose the government form you want to fill',
    formAadhaarUpdate: 'Aadhaar Update Form',
    formAadhaarUpdateDesc: 'Update your Aadhaar card details',
    formRationCard: 'Ration Card Application',
    formRationCardDesc: 'Apply for a new ration card',
    formBirthCertificate: 'Birth Certificate Request',
    formBirthCertificateDesc: 'Request a copy of birth certificate',
    formDrivingLicense: 'Driving License Application',
    formDrivingLicenseDesc: 'Apply for driving license',
    formPassport: 'Passport Application',
    formPassportDesc: 'Apply for passport',
    formVoterId: 'Voter ID Enrollment',
    formVoterIdDesc: 'Enroll for voter ID card',
    required: 'Required',
    optional: 'Optional',
    select: 'Select',
    uploadDocument: '📄 Upload Document',
    uploadHint: 'Upload your ID documents (Aadhaar, PAN, Voter ID, etc.)',
    dropFiles: 'Drop files here or click to browse',
    supportedFormats: 'PDF, PNG, JPG, JPEG, TIFF, BMP',
    processing: 'Processing...',
    extractData: 'Extract Data',
    or: 'or',
    dontHaveDocument: "Don't have the document? Speak your details instead",
    formPreview: 'Form Preview',
    back: 'Back',
    complete: 'Complete',
    enterValue: 'Enter value...',
    selectOption: 'Select...',
    generatePDF: 'Generate PDF',
    editDocuments: 'Edit Documents',
    home: 'Home',
    generatingPDF: 'Generating PDF...',
    pdfGenerated: 'PDF Generated Successfully!',
    previewPDF: 'Preview PDF',
    downloadPDF: '📥 Download PDF',
    printPDF: '🖨️ Print',
    nextStep: 'Next: Submit this form at the counter',
    fillAnotherForm: 'Fill Another Form',
    footer: '🔒 Your data stays on your computer',
    voiceInput: '🎤 Voice Input',
    cancel: 'Cancel',
    useVoiceData: 'Use Voice Data',
  },
  hi: {
    title: '🇮🇳 सेवा केंद्र - फॉर्म भरने का सहायक',
    subtitle: 'दस्तावेज़ अपलोड करें, सरकारी फॉर्म ऑटो-फिल करें, PDF डाउनलोड करें',
    selectFormType: 'आपको कौन सा फॉर्म चाहिए?',
    selectFormSubtitle: 'वह सरकारी फॉर्म चुनें जिसे आप भरना चाहते हैं',
    formAadhaarUpdate: 'आधार अपडेट फॉर्म',
    formAadhaarUpdateDesc: 'अपने आधार कार्ड की जानकारी अपडेट करें',
    formRationCard: 'राशन कार्ड आवेदन',
    formRationCardDesc: 'नया राशन कार्ड के लिए आवेदन करें',
    formBirthCertificate: 'जन्म प्रमाणपत्र अनुरोध',
    formBirthCertificateDesc: 'जन्म प्रमाणपत्र की प्रति अनुरोध करें',
    formDrivingLicense: 'ड्राइविंग लाइसेंस आवेदन',
    formDrivingLicenseDesc: 'ड्राइविंग लाइसेंस के लिए आवेदन करें',
    formPassport: 'पासपोर्ट आवेदन',
    formPassportDesc: 'पासपोर्ट के लिए आवेदन करें',
    formVoterId: 'वोटर आईडी नामांकन',
    formVoterIdDesc: 'वोटर आईडी कार्ड के लिए नामांकन करें',
    required: 'आवश्यक',
    optional: 'वैकल्पिक',
    select: 'चुनें',
    uploadDocument: '📄 दस्तावेज़ अपलोड करें',
    uploadHint: 'अपने आईडी दस्तावेज़ अपलोड करें (आधार, पैन, वोटर आईडी, आदि)',
    dropFiles: 'फ़ाइलें यहाँ छोड़ें या ब्राउज़ करने के लिए क्लिक करें',
    supportedFormats: 'PDF, PNG, JPG, JPEG, TIFF, BMP',
    processing: 'प्रोसेसिंग...',
    extractData: 'डेटा निकालें',
    or: 'या',
    dontHaveDocument: 'दस्तावेज़ नहीं है? अपनी जानकारी बोलें',
    formPreview: 'फॉर्म पूर्वावलोकन',
    back: 'वापस',
    complete: 'पूर्ण',
    enterValue: 'मान दर्ज करें...',
    selectOption: 'चुनें...',
    generatePDF: 'PDF जेनरेट करें',
    editDocuments: 'दस्तावेज़ संपादित करें',
    home: 'होम',
    generatingPDF: 'PDF जेनरेट हो रहा है...',
    pdfGenerated: 'PDF सफलतापूर्वक जेनरेट किया गया!',
    previewPDF: 'PDF पूर्वावलोकन',
    downloadPDF: '📥 PDF डाउनलोड करें',
    printPDF: '🖨️ प्रिंट करें',
    nextStep: 'अगला: काउंटर पर इस फॉर्म को जमा करें',
    fillAnotherForm: 'दूसरा फॉर्म भरें',
    footer: '🔒 आपका डेटा आपके कंप्यूटर पर ही रहता है',
    voiceInput: '🎤 वॉइस इनपुट',
    cancel: 'रद्द करें',
    useVoiceData: 'वॉइस डेटा उपयोग करें',
  },
};

// Theme hook
function useTheme() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return [theme, toggleTheme];
}

// Language hook
function useLanguage() {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'en';
  });

  useEffect(() => {
    document.documentElement.setAttribute('lang', language);
    localStorage.setItem('language', language);
  }, [language]);

  const changeLanguage = (newLang) => {
    setLanguage(newLang);
  };

  const t = (key) => translations[language]?.[key] || translations.en[key] || key;

  return [language, changeLanguage, t];
}

/**
 * Main application component
 * Simplified form-first flow: Select Form → Upload → Extract → Review → Generate PDF
 */
function App() {
  const [theme, toggleTheme] = useTheme();
  const [language, changeLanguage, t] = useLanguage();
  
  // Flow state
  const [step, setStep] = useState(1); // 1: Select Form, 2: Upload, 3: Review, 4: PDF Preview, 5: Success
  const [selectedForm, setSelectedForm] = useState(null);
  const [formTemplate, setFormTemplate] = useState(null);
  const [formData, setFormData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [voiceFields, setVoiceFields] = useState({});
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);
  const [pdfFilename, setPdfFilename] = useState(null);

  // Handle form selection
  const handleFormSelect = async (form) => {
    setSelectedForm(form);
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch form template details
      const template = await getFormTemplate(form.id);
      setFormTemplate(template);
      setStep(2); // Move to upload step
    } catch (err) {
      setError(err.message);
      setStatus({ type: 'error', message: `❌ ${err.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle document upload
  const handleUpload = async (file) => {
    if (!selectedForm) {
      setStatus({ type: 'error', message: '❌ Please select a form first' });
      return;
    }
    
    if (!file) {
      setStatus({ type: 'error', message: '❌ No file selected' });
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setStatus({ type: 'loading', message: `Processing ${file.name}...` });

    try {
      // Upload and map to form
      const result = await uploadAndMapToForm(selectedForm.id, file);
      
      console.log('Upload result:', result);
      
      // Validate response structure
      if (!result) {
        throw new Error('No response from server');
      }
      
      // Convert mapped fields to form data
      const mappedFields = result.mapped_fields || {};
      const data = {};
      
      if (typeof mappedFields === 'object' && mappedFields !== null) {
        for (const [fieldName, fieldInfo] of Object.entries(mappedFields)) {
          let value = "";
          if (fieldInfo && typeof fieldInfo === 'object') {
            value = fieldInfo.value;
          } else {
            value = fieldInfo;
          }
          // Ensure value is a string
          data[fieldName] = value != null ? String(value) : "";
        }
      }
      
      // Merge with any voice input data (ensure voice fields are also strings)
      const mergedData = { ...data };
      for (const [key, value] of Object.entries(voiceFields)) {
        mergedData[key] = value != null ? String(value) : "";
      }
      setFormData(mergedData);
      
      // Ensure formTemplate is set before moving to step 3
      if (!formTemplate) {
        // Try to fetch template again if missing
        try {
          const template = await getFormTemplate(selectedForm.id);
          setFormTemplate(template);
        } catch (templateErr) {
          console.error('Failed to fetch template:', templateErr);
          throw new Error('Failed to load form template');
        }
      }
      
      setStatus({
        type: 'success',
        message: `✅ Extracted and mapped ${Object.keys(mergedData).length} fields!`,
      });
      setStep(3); // Move to review step
    } catch (err) {
      console.error('Upload error:', err);
      const errorMessage = err?.message || err?.detail || 'Upload failed. Please try again.';
      setError(errorMessage);
      setStatus({ type: 'error', message: `❌ ${errorMessage}` });
      // Don't change step on error - stay on upload step
    } finally {
      setIsLoading(false);
    }
  };

  // Handle voice input
  const handleVoiceInput = () => {
    setShowVoiceModal(true);
  };

  // Map voice field names to form field names
  const mapVoiceFieldToFormField = (voiceFieldName) => {
    // Map voice input field names to actual form template field names
    const fieldMapping = {
      'name': 'applicant_name',  // Voice says "name" but form uses "applicant_name"
      'full_name': 'applicant_name',
      'father_name': 'father_name',
      'dob': 'date_of_birth',
      'date_of_birth': 'date_of_birth',
      'address': 'address',
      'phone': 'mobile_number',
      'mobile': 'mobile_number',
      'mobile_number': 'mobile_number',
      'email': 'email',
      'aadhaar': 'aadhaar_number',
      'aadhaar_number': 'aadhaar_number',
      'pan': 'pan_number',
      'pan_number': 'pan_number',
    };
    
    // If we have a form template, try to find the matching field
    if (formTemplate && formTemplate.fields) {
      // First check direct mapping
      if (fieldMapping[voiceFieldName]) {
        const mappedField = fieldMapping[voiceFieldName];
        if (formTemplate.fields[mappedField]) {
          return mappedField;
        }
      }
      
      // Try to find by checking field mappings in template
      for (const [formFieldName, fieldConfig] of Object.entries(formTemplate.fields)) {
        const mappings = fieldConfig.mapping || [];
        if (mappings.includes(voiceFieldName) || formFieldName === voiceFieldName) {
          return formFieldName;
        }
      }
    }
    
    // Fallback to direct mapping or original field name
    return fieldMapping[voiceFieldName] || voiceFieldName;
  };

  // Handle voice field updates
  const handleVoiceFieldUpdate = (fieldName, value) => {
    // Map voice field name to actual form field name
    const formFieldName = mapVoiceFieldToFormField(fieldName);
    console.log(`[Voice] Mapping "${fieldName}" -> "${formFieldName}" with value:`, value);
    
    setVoiceFields(prev => ({
      ...prev,
      [formFieldName]: value
    }));
  };

  // Handle voice transcript (for manual mapping)
  const handleVoiceTranscript = (text) => {
    // Store transcript for later processing
    console.log('Voice transcript:', text);
  };

  // Use voice data to fill form
  const handleUseVoiceData = () => {
    if (Object.keys(voiceFields).length > 0) {
      setFormData(prev => ({ ...prev, ...voiceFields }));
      setShowVoiceModal(false);
      setStep(3); // Move to review step
    }
  };

  // Handle field change in preview
  const handleFieldChange = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Handle PDF generation
  const handleGeneratePDF = async () => {
    if (!selectedForm || !formTemplate) return;
    
    setIsLoading(true);
    setError(null);
    setStatus({ type: 'loading', message: t('generatingPDF') });

    try {
      const result = await generateFilledForm(selectedForm.id, {
        form_data: formData,
        extracted_entities: {} // Can include original extracted data if needed
      });
      
      // Store PDF blob URL for preview (don't auto-download)
      if (result.blobUrl) {
        setPdfBlobUrl(result.blobUrl);
        setPdfFilename(result.filename);
        setStep(4); // Move to PDF preview step
      } else {
        // Fallback: if no blob URL, show success
        setStatus({
          type: 'success',
          message: `✅ ${t('pdfGenerated')}`,
        });
        setStep(5); // Success step
      }
    } catch (err) {
      setError(err.message);
      setStatus({ type: 'error', message: `❌ ${err.message}` });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle PDF download
  const handleDownloadPDF = () => {
    if (!pdfBlobUrl || !pdfFilename) return;
    
    const a = document.createElement('a');
    a.href = pdfBlobUrl;
    a.download = pdfFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Move to success step after download
    setStep(5);
  };

  // Reset to start
  const handleReset = () => {
    setStep(1);
    setSelectedForm(null);
    setFormTemplate(null);
    setFormData({});
    setError(null);
    setStatus(null);
    // Clean up PDF blob URL
    if (pdfBlobUrl) {
      window.URL.revokeObjectURL(pdfBlobUrl);
      setPdfBlobUrl(null);
      setPdfFilename(null);
    }
  };

  return (
    <ErrorBoundary>
      <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-top">
          <h1>{t('title')}</h1>
          <div className="header-controls">
            <select 
              className="lang-select"
              value={language}
              onChange={(e) => changeLanguage(e.target.value)}
              title="Select language / भाषा चुनें"
            >
              {uiLanguages.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.nativeName}
                </option>
              ))}
            </select>
            <button className="theme-toggle" onClick={toggleTheme} title="Toggle dark mode">
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
        <p>{t('subtitle')}</p>
        
        {/* Progress indicator */}
        {step > 1 && (
          <div className="progress-steps">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>1. {t('selectFormType')}</div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>2. {t('uploadDocument')}</div>
            <div className={`step ${step >= 3 ? 'active' : ''}`}>3. {t('formPreview')}</div>
            <div className={`step ${step >= 4 ? 'active' : ''}`}>4. {t('previewPDF') || 'Preview PDF'}</div>
            <div className={`step ${step >= 5 ? 'active' : ''}`}>5. {t('downloadPDF') || 'Download'}</div>
          </div>
        )}
      </header>

      <main className="app-main">
        {/* STEP 1: Select Form Template */}
        {step === 1 && (
          <FormTemplateSelector 
            onSelect={handleFormSelect}
            t={t}
          />
        )}

        {/* STEP 2: Upload Documents */}
        {step === 2 && (
          <div className="upload-layout">
            <div className="selected-form-badge">
              <span>{selectedForm?.icon}</span>
              <span>{selectedForm?.name}</span>
              <button onClick={() => setStep(1)}>Change</button>
            </div>
            
            <FileUpload 
              onUpload={handleUpload} 
              isLoading={isLoading} 
              t={t}
              showVoiceButton={true}
              onVoiceInput={handleVoiceInput}
            />
            
            {status && (
              <div className={`status ${status.type}`}>
                {status.message}
              </div>
            )}

            {/* Voice Input Modal */}
            {showVoiceModal && (
              <div className="voice-modal-overlay" onClick={() => setShowVoiceModal(false)}>
                <div className="voice-modal" onClick={(e) => e.stopPropagation()}>
                  <div className="voice-modal-header">
                    <h3>{t('voiceInput') || '🎤 Voice Input'}</h3>
                    <button 
                      className="close-btn"
                      onClick={() => setShowVoiceModal(false)}
                    >
                      ✕
                    </button>
                  </div>
                  <VoiceInput
                    onTranscript={handleVoiceTranscript}
                    onFieldUpdate={handleVoiceFieldUpdate}
                    uiLanguage={language}
                    translations={translations[language] || translations.en}
                  />
                  <div className="voice-modal-actions">
                    <button 
                      className="btn-secondary"
                      onClick={() => setShowVoiceModal(false)}
                    >
                      {t('cancel') || 'Cancel'}
                    </button>
                    <button 
                      className="btn-primary"
                      onClick={handleUseVoiceData}
                      disabled={Object.keys(voiceFields).length === 0}
                    >
                      {t('useVoiceData') || 'Use Voice Data'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 3: Review & Edit Form */}
        {step === 3 && (
          <>
            {formTemplate ? (
              <>
                <FormPreview
                  formTemplate={formTemplate}
                  formData={formData}
                  onFieldChange={handleFieldChange}
                  onGeneratePDF={handleGeneratePDF}
                  onBack={() => setStep(2)}
                  t={t}
                />
                {status && (
                  <div className={`status ${status.type}`}>
                    {status.message}
                  </div>
                )}
              </>
            ) : (
              <div className="error-state">
                <p>❌ Form template not loaded. Please try again.</p>
                <button className="btn-primary" onClick={() => setStep(1)}>
                  {t('back') || 'Back to Form Selection'}
                </button>
              </div>
            )}
          </>
        )}

        {/* STEP 4: PDF Preview */}
        {step === 4 && pdfBlobUrl && (
          <div className="pdf-preview-screen">
            <div className="pdf-preview-header">
              <h2>{t('pdfGenerated') || 'PDF Generated Successfully!'}</h2>
              <p>{t('previewPDF') || 'Preview your filled form below'}</p>
            </div>
            <div className="pdf-preview-container">
              <iframe
                src={pdfBlobUrl}
                title="PDF Preview"
                className="pdf-preview-iframe"
              />
            </div>
            <div className="pdf-preview-actions">
              <button className="btn-secondary" onClick={() => setStep(3)}>
                {t('back') || 'Back to Edit'}
              </button>
              <button className="btn-primary" onClick={handleDownloadPDF}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                {t('downloadPDF') || 'Download PDF'}
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: Success */}
        {step === 5 && (
          <div className="success-screen">
            <div className="success-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h2>{t('pdfGenerated')}</h2>
            <p>{t('nextStep')}</p>
            <div className="success-actions">
              <button className="btn-primary" onClick={handleReset}>
                {t('fillAnotherForm') || 'Fill Another Form'}
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          {t('footer') || '🔒 Your data stays on your computer'}
        </p>
      </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;
