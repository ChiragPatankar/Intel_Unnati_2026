/**
 * Voice Input Component
 * Uses Web Speech API for speech-to-text with multi-language support
 * Premium UI Design
 */

import { useState, useRef, useEffect } from 'react';

const VoiceInput = ({ onTranscript, onFieldUpdate, uiLanguage = 'en', translations = {} }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState('');
  const [selectedVoiceLang, setSelectedVoiceLang] = useState(getDefaultVoiceLang(uiLanguage));
  const [currentField, setCurrentField] = useState('');
  const recognitionRef = useRef(null);

  // Get default voice language based on UI language
  function getDefaultVoiceLang(uiLang) {
    const langMap = {
      'en': 'en-IN', 'hi': 'hi-IN', 'ta': 'ta-IN', 'te': 'te-IN',
      'mr': 'mr-IN', 'bn': 'bn-IN', 'gu': 'gu-IN', 'kn': 'kn-IN',
    };
    return langMap[uiLang] || 'en-IN';
  }

  // Translation helper
  const t = (key) => translations[key] || key;

  // Supported Indian languages for voice input
  const voiceLanguages = [
    { code: 'en-IN', name: 'English (India)' },
    { code: 'hi-IN', name: 'हिंदी (Hindi)' },
    { code: 'ta-IN', name: 'தமிழ் (Tamil)' },
    { code: 'te-IN', name: 'తెలుగు (Telugu)' },
    { code: 'mr-IN', name: 'मराठी (Marathi)' },
    { code: 'bn-IN', name: 'বাংলা (Bengali)' },
    { code: 'gu-IN', name: 'ગુજરાતી (Gujarati)' },
    { code: 'kn-IN', name: 'ಕನ್ನಡ (Kannada)' },
    { code: 'ml-IN', name: 'മലയാളം (Malayalam)' },
    { code: 'pa-IN', name: 'ਪੰਜਾਬੀ (Punjabi)' },
  ];

  // Update voice language when UI language changes
  useEffect(() => {
    setSelectedVoiceLang(getDefaultVoiceLang(uiLanguage));
  }, [uiLanguage]);

  useEffect(() => {
    // Check for browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError(t('voiceNotSupported'));
      return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    const recognition = recognitionRef.current;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = selectedVoiceLang;

    recognition.onstart = () => {
      setIsListening(true);
      setError('');
      console.log('[Voice] Started listening in', selectedVoiceLang);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptText = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcriptText + ' ';
        } else {
          interim += transcriptText;
        }
      }

      if (final) {
        const newTranscript = transcript + final;
        setTranscript(newTranscript);
        
        // Process the transcript
        processVoiceInput(final.trim());
        
        if (onTranscript) {
          onTranscript(final.trim());
        }
      }
      setInterimTranscript(interim);
    };

    recognition.onerror = (event) => {
      console.error('[Voice] Error:', event.error);
      setError(`Error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      console.log('[Voice] Stopped listening');
    };

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, [selectedVoiceLang]);

  // Process voice input for field detection and filling
  const processVoiceInput = (text) => {
    const lowerText = text.toLowerCase();
    
    // Field detection patterns - more flexible matching
    const patterns = {
      name: [
        /(?:my name is|i am|i'm|name is|मेरा नाम|naam|नाम)\s*(?:is\s*)?(.+?)(?:\s|$|,|\.)/i,
        /(?:name|नाम)\s*(?:is|are)?\s*(.+?)(?:\s|$|,|\.)/i,
      ],
      father_name: [
        /(?:father'?s? name|पिता का नाम|pitaji|father)\s*(?:is|are)?\s*(.+?)(?:\s|$|,|\.)/i,
      ],
      dob: [
        /(?:date of birth|born on|dob|जन्म तिथि|janam|birth date)\s*(?:is|on)?\s*(.+?)(?:\s|$|,|\.)/i,
      ],
      address: [
        /(?:address|पता|i live at|मैं रहता हूं|residence)\s*(?:is|at)?\s*(.+?)(?:\s|$|,|\.)/i,
      ],
      phone: [
        /(?:phone|mobile|number|नंबर|फोन|contact)\s*(?:is|number)?\s*([\d\s\+\-]+?)(?:\s|$|,|\.)/i,
      ],
      email: [
        /(?:email|ईमेल|e-mail)\s*(?:is|address)?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/i,
      ],
      aadhaar: [
        /(?:aadhaar|आधार|uid)\s*(?:number|नंबर)?\s*(?:is)?\s*([\d\s\-]+?)(?:\s|$|,|\.)/i,
      ],
      pan: [
        /(?:pan|पैन)\s*(?:number|नंबर)?\s*(?:is)?\s*([a-z\d\s]+?)(?:\s|$|,|\.)/i,
      ],
    };

    for (const [field, fieldPatterns] of Object.entries(patterns)) {
      for (const pattern of fieldPatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
          const value = match[1].trim();
          console.log(`[Voice] Detected ${field}:`, value);
          
          if (onFieldUpdate) {
            onFieldUpdate(field, value);
          }
          return;
        }
      }
    }

    // If no pattern matched but we have a current field selected, use the text as value
    if (currentField && text.trim()) {
      if (onFieldUpdate) {
        onFieldUpdate(currentField, text.trim());
      }
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.lang = selectedVoiceLang;
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const clearTranscript = () => {
    setTranscript('');
    setInterimTranscript('');
  };

  const getPrompt = () => {
    return t('startSpeaking');
  };

  return (
    <div className="voice-input-container">
      {/* Header with icon and language selector */}
      <div className="voice-header">
        <div className="voice-title">
          <div className="voice-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </div>
          <h3>{t('voiceTitle')}</h3>
        </div>
        <select 
          value={selectedVoiceLang} 
          onChange={(e) => setSelectedVoiceLang(e.target.value)}
          className="voice-lang-select"
        >
          {voiceLanguages.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="voice-error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </div>
      )}

      {/* Main Voice Button */}
      <div className="voice-main-controls">
        <button 
          className={`voice-btn-main ${isListening ? 'listening' : ''}`}
          onClick={toggleListening}
          disabled={!!error}
        >
          <div className="voice-btn-inner">
            {isListening ? (
              <>
                <div className="voice-wave">
                  <span></span><span></span><span></span><span></span><span></span>
                </div>
                <span className="btn-text">{t('stopVoice')}</span>
              </>
            ) : (
              <>
                <svg className="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
                <span className="btn-text">{t('startVoice')}</span>
              </>
            )}
          </div>
          {isListening && <div className="pulse-ring"></div>}
          {isListening && <div className="pulse-ring delay"></div>}
        </button>
        
        {transcript && (
          <button className="voice-btn-clear" onClick={clearTranscript}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            {t('clear')}
          </button>
        )}
      </div>

      {/* Field Selector */}
      <div className="voice-field-selector">
        <label>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          {t('fillField')}
        </label>
        <select 
          value={currentField} 
          onChange={(e) => setCurrentField(e.target.value)}
          className="field-dropdown"
        >
          <option value="">{t('autoDetect')}</option>
          <option value="name">{t('fullName')}</option>
          <option value="father_name">{t('fatherName')}</option>
          <option value="dob">{t('dateOfBirth')}</option>
          <option value="address">{t('address')}</option>
          <option value="phone">{t('phoneNumber')}</option>
          <option value="email">{t('email')}</option>
          <option value="aadhaar">{t('aadhaarNumber')}</option>
          <option value="pan">{t('panNumber')}</option>
        </select>
      </div>

      {/* Listening Indicator */}
      {isListening && (
        <div className="voice-listening-indicator">
          <div className="listening-dot"></div>
          <span>{getPrompt()}</span>
        </div>
      )}

      {/* Transcript Box */}
      <div className="voice-transcript-box">
        <div className="transcript-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          {t('transcript')}
        </div>
        <div className="transcript-content">
          {transcript || <span className="placeholder-text">{t('startSpeaking')}...</span>}
          <span className="interim-text">{interimTranscript}</span>
        </div>
      </div>

      {/* Tips Section */}
      <div className="voice-tips-card">
        <div className="tips-header">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <strong>{t('tips')}</strong>
        </div>
        <ul className="tips-list">
          <li>{t('tipName')}</li>
          <li>{t('tipPhone')}</li>
          <li>{t('tipField')}</li>
        </ul>
      </div>

      <style>{`
        .voice-input-container {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 32px;
          border: 1px solid var(--border, #e2e8f0);
          box-shadow: var(--shadow-lg, 0 20px 25px -5px rgb(0 0 0 / 0.1));
        }

        .voice-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 28px;
          padding-bottom: 20px;
          border-bottom: 2px solid var(--border, #e2e8f0);
        }

        .voice-title {
          display: flex;
          align-items: center;
          gap: 14px;
        }

        .voice-icon {
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 15px -3px var(--primary, #6366f1);
        }

        .voice-header h3 {
          margin: 0;
          font-size: 22px;
          font-weight: 700;
          color: var(--text-primary, #0f172a);
        }

        .voice-lang-select {
          padding: 12px 40px 12px 16px;
          border-radius: 12px;
          border: 2px solid var(--border, #e2e8f0);
          background: var(--bg-secondary, white);
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary, #0f172a);
          cursor: pointer;
          appearance: none;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 12px center;
          background-size: 16px;
          transition: all 0.2s;
        }

        .voice-lang-select:hover {
          border-color: var(--primary, #6366f1);
        }

        .voice-lang-select:focus {
          outline: none;
          border-color: var(--primary, #6366f1);
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
        }

        .voice-error {
          display: flex;
          align-items: center;
          gap: 10px;
          background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
          color: #dc2626;
          padding: 16px 20px;
          border-radius: 12px;
          margin-bottom: 24px;
          font-weight: 600;
          font-size: 14px;
          border-left: 4px solid #dc2626;
        }

        .voice-main-controls {
          display: flex;
          gap: 16px;
          margin-bottom: 24px;
          align-items: stretch;
        }

        .voice-btn-main {
          flex: 1;
          padding: 0;
          border: none;
          border-radius: 20px;
          cursor: pointer;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          position: relative;
          overflow: hidden;
          transition: all 0.3s;
          box-shadow: 0 4px 20px -5px var(--primary, #6366f1);
        }

        .voice-btn-inner {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 32px 24px;
          gap: 12px;
          position: relative;
          z-index: 1;
        }

        .voice-btn-main .mic-icon {
          color: white;
        }

        .voice-btn-main .btn-text {
          color: white;
          font-size: 16px;
          font-weight: 700;
        }

        .voice-btn-main:hover:not(:disabled) {
          transform: translateY(-3px);
          box-shadow: 0 8px 30px -5px var(--primary, #6366f1);
        }

        .voice-btn-main:active:not(:disabled) {
          transform: translateY(-1px);
        }

        .voice-btn-main.listening {
          background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
          box-shadow: 0 4px 20px -5px #ef4444;
        }

        .voice-btn-main:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .pulse-ring {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 100%;
          height: 100%;
          border: 3px solid rgba(255, 255, 255, 0.4);
          border-radius: 20px;
          transform: translate(-50%, -50%);
          animation: pulse-ring 1.5s ease-out infinite;
        }

        .pulse-ring.delay {
          animation-delay: 0.5s;
        }

        @keyframes pulse-ring {
          0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
          }
          100% {
            transform: translate(-50%, -50%) scale(1.3);
            opacity: 0;
          }
        }

        .voice-wave {
          display: flex;
          align-items: center;
          gap: 4px;
          height: 32px;
        }

        .voice-wave span {
          width: 4px;
          height: 100%;
          background: white;
          border-radius: 2px;
          animation: wave 1s ease-in-out infinite;
        }

        .voice-wave span:nth-child(1) { animation-delay: 0s; }
        .voice-wave span:nth-child(2) { animation-delay: 0.1s; }
        .voice-wave span:nth-child(3) { animation-delay: 0.2s; }
        .voice-wave span:nth-child(4) { animation-delay: 0.3s; }
        .voice-wave span:nth-child(5) { animation-delay: 0.4s; }

        @keyframes wave {
          0%, 100% { transform: scaleY(0.3); }
          50% { transform: scaleY(1); }
        }

        .voice-btn-clear {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 20px 24px;
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 16px;
          background: var(--bg-tertiary, #f1f5f9);
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          color: var(--text-secondary, #475569);
          transition: all 0.2s;
        }

        .voice-btn-clear:hover {
          border-color: #ef4444;
          color: #ef4444;
          background: #fef2f2;
        }

        .voice-field-selector {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
          padding: 16px 20px;
          background: var(--bg-tertiary, #f1f5f9);
          border-radius: 14px;
          border: 2px solid var(--border, #e2e8f0);
        }

        .voice-field-selector label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-secondary, #475569);
          white-space: nowrap;
        }

        .field-dropdown {
          flex: 1;
          padding: 12px 16px;
          border-radius: 10px;
          border: 2px solid var(--border, #e2e8f0);
          background: var(--bg-secondary, white);
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary, #0f172a);
          cursor: pointer;
          transition: all 0.2s;
        }

        .field-dropdown:focus {
          outline: none;
          border-color: var(--primary, #6366f1);
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
        }

        .voice-listening-indicator {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 18px 24px;
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-radius: 14px;
          margin-bottom: 24px;
          border-left: 4px solid #f59e0b;
          animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .listening-dot {
          width: 14px;
          height: 14px;
          background: #ef4444;
          border-radius: 50%;
          animation: pulse-dot 1s ease-in-out infinite;
        }

        @keyframes pulse-dot {
          0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
          50% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        }

        .voice-listening-indicator span {
          font-size: 15px;
          font-weight: 600;
          color: #92400e;
        }

        .voice-transcript-box {
          background: var(--bg-secondary, white);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 16px;
          padding: 20px;
          margin-bottom: 24px;
          min-height: 140px;
        }

        .transcript-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--text-muted, #94a3b8);
          margin-bottom: 14px;
        }

        .transcript-content {
          font-size: 16px;
          line-height: 1.8;
          color: var(--text-primary, #0f172a);
          font-weight: 500;
        }

        .placeholder-text {
          color: var(--text-muted, #94a3b8);
          font-style: italic;
        }

        .interim-text {
          color: var(--text-muted, #94a3b8);
          font-style: italic;
          background: linear-gradient(90deg, var(--text-muted, #94a3b8), transparent);
          -webkit-background-clip: text;
          background-clip: text;
        }

        .voice-tips-card {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
          padding: 20px 24px;
          border-radius: 14px;
          border-left: 4px solid var(--primary, #6366f1);
        }

        .tips-header {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          color: var(--primary, #6366f1);
          margin-bottom: 12px;
        }

        .tips-list {
          margin: 0;
          padding-left: 28px;
          color: var(--text-secondary, #475569);
        }

        .tips-list li {
          padding: 6px 0;
          font-size: 14px;
          line-height: 1.5;
        }

        /* Dark mode adjustments */
        [data-theme="dark"] .voice-input-container {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }

        [data-theme="dark"] .voice-lang-select,
        [data-theme="dark"] .field-dropdown {
          background: var(--bg-secondary, #1e293b);
        }

        [data-theme="dark"] .voice-field-selector {
          background: var(--bg-tertiary, #334155);
        }

        [data-theme="dark"] .voice-transcript-box {
          background: var(--bg-secondary, #1e293b);
        }

        [data-theme="dark"] .voice-btn-clear {
          background: var(--bg-tertiary, #334155);
        }
      `}</style>
    </div>
  );
};

export default VoiceInput;
