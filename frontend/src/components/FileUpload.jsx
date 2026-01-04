import { useState, useRef } from 'react';

/**
 * File upload component with premium styling
 * Accepts PDF and image files
 * Includes voice input option
 */
export default function FileUpload({ 
  onUpload, 
  isLoading, 
  t = (key) => key,
  onVoiceInput,
  showVoiceButton = true 
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      // Auto-upload when file is selected
      if (onUpload) {
        // Small delay to show file preview first
        setTimeout(() => {
          onUpload(file);
        }, 300);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      // Auto-upload when file is dropped
      if (onUpload) {
        setTimeout(() => {
          onUpload(file);
        }, 300);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleZoneClick = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-header">
        <div className="upload-icon-wrapper">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="12" y1="18" x2="12" y2="12"/>
            <line x1="9" y1="15" x2="12" y2="12"/>
            <line x1="15" y1="15" x2="12" y2="12"/>
          </svg>
        </div>
        <div className="upload-header-text">
          <h2>{t('uploadDocument') || '📄 Upload Document'}</h2>
          <p>{t('uploadHint') || 'Upload Aadhaar, PAN, Voter ID, Passport, or Driving License'}</p>
        </div>
      </div>
      
      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleZoneClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
          onChange={handleFileSelect}
          className="file-input-hidden"
        />
        
        {selectedFile ? (
          <div className="file-preview">
            <div className="file-icon">
              {selectedFile.type.includes('pdf') ? (
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <path d="M10 12h4"/>
                  <path d="M10 16h4"/>
                </svg>
              ) : (
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              )}
            </div>
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">{formatFileSize(selectedFile.size)}</span>
            </div>
            <div className="file-check">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
          </div>
        ) : (
          <div className="drop-zone-content">
            <div className="drop-icon">
              <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <div className="drop-text">
              <span className="drop-main">{t('dropFiles') || 'Drop files here or click to browse'}</span>
              <span className="drop-sub">{t('supportedFormats') || 'PDF, PNG, JPG, JPEG, TIFF, BMP'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Voice Input Alternative */}
      {showVoiceButton && !selectedFile && (
        <div className="voice-alternative">
          <div className="voice-divider">
            <span>{t('or') || 'or'}</span>
          </div>
          <button 
            className="btn-voice"
            onClick={() => {
              if (onVoiceInput) {
                onVoiceInput();
              } else {
                setShowVoiceModal(true);
              }
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
            <span>{t('dontHaveDocument') || "Don't have the document? Speak your details instead"}</span>
          </button>
        </div>
      )}

      <div className="upload-actions">
        <button 
          className={`btn-primary ${isLoading ? 'loading' : ''}`}
          onClick={handleUpload} 
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? (
            <>
              <div className="spinner"></div>
              <span>{t('processing') || 'Processing...'}</span>
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13"/>
                <path d="M22 2L15 22l-4-9-9-4L22 2z"/>
              </svg>
              <span>{t('extractData') || 'Extract Data'}</span>
            </>
          )}
        </button>
        {selectedFile && (
          <button 
            className="btn-secondary"
            onClick={handleClear} 
            disabled={isLoading}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            <span>{t('clear') || 'Clear'}</span>
          </button>
        )}
      </div>

      <style>{`
        .file-upload-container {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 24px;
          padding: 32px;
          border: 1px solid var(--border, #e2e8f0);
          box-shadow: var(--shadow-lg, 0 20px 25px -5px rgb(0 0 0 / 0.1));
          margin-bottom: 24px;
        }

        .file-upload-header {
          display: flex;
          align-items: flex-start;
          gap: 18px;
          margin-bottom: 28px;
        }

        .upload-icon-wrapper {
          width: 56px;
          height: 56px;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
          box-shadow: 0 4px 15px -3px var(--primary, #6366f1);
        }

        .upload-header-text h2 {
          font-size: 24px;
          font-weight: 800;
          margin: 0 0 6px 0;
          color: var(--text-primary, #0f172a);
        }

        .upload-header-text p {
          margin: 0;
          color: var(--text-secondary, #475569);
          font-size: 15px;
        }

        .drop-zone {
          border: 3px dashed var(--border, #e2e8f0);
          border-radius: 20px;
          padding: 48px 32px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          background: var(--bg-tertiary, #f1f5f9);
          margin-bottom: 24px;
          position: relative;
          overflow: hidden;
        }

        .drop-zone::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          opacity: 0;
          transition: opacity 0.3s;
        }

        .drop-zone:hover {
          border-color: var(--primary, #6366f1);
          background: rgba(99, 102, 241, 0.05);
        }

        .drop-zone:hover::before {
          opacity: 0.03;
        }

        .drop-zone.drag-over {
          border-color: var(--primary, #6366f1);
          border-style: solid;
          background: rgba(99, 102, 241, 0.1);
          transform: scale(1.01);
        }

        .drop-zone.has-file {
          border-color: var(--success, #10b981);
          background: rgba(16, 185, 129, 0.05);
          border-style: solid;
        }

        .file-input-hidden {
          position: absolute;
          opacity: 0;
          pointer-events: none;
        }

        .drop-zone-content {
          position: relative;
          z-index: 1;
        }

        .drop-icon {
          color: var(--primary, #6366f1);
          margin-bottom: 20px;
          opacity: 0.8;
        }

        .drop-text {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .drop-main {
          font-size: 17px;
          font-weight: 600;
          color: var(--text-primary, #0f172a);
        }

        .drop-sub {
          font-size: 14px;
          color: var(--text-muted, #94a3b8);
        }

        .file-preview {
          position: relative;
          z-index: 1;
          display: flex;
          align-items: center;
          gap: 20px;
          padding: 16px 24px;
          background: var(--bg-secondary, white);
          border-radius: 16px;
          border: 2px solid var(--success, #10b981);
          max-width: 480px;
          margin: 0 auto;
        }

        .file-icon {
          color: var(--primary, #6366f1);
          opacity: 0.8;
        }

        .file-info {
          flex: 1;
          text-align: left;
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 0;
        }

        .file-name {
          font-weight: 600;
          font-size: 15px;
          color: var(--text-primary, #0f172a);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .file-size {
          font-size: 13px;
          color: var(--text-muted, #94a3b8);
        }

        .file-check {
          color: var(--success, #10b981);
          flex-shrink: 0;
        }

        .upload-actions {
          display: flex;
          gap: 14px;
        }

        .btn-primary {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 16px 28px;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #4f46e5 100%);
          color: white;
          border: none;
          border-radius: 14px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 700;
          transition: all 0.3s;
          box-shadow: 0 4px 15px -3px var(--primary, #6366f1);
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px -5px var(--primary, #6366f1);
        }

        .btn-primary:active:not(:disabled) {
          transform: translateY(0);
        }

        .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-primary.loading {
          background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
        }

        .spinner {
          width: 20px;
          height: 20px;
          border: 3px solid rgba(255, 255, 255, 0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .btn-secondary {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 16px 24px;
          background: var(--bg-tertiary, #f1f5f9);
          color: var(--text-secondary, #475569);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 14px;
          cursor: pointer;
          font-size: 15px;
          font-weight: 600;
          transition: all 0.2s;
        }

        .btn-secondary:hover:not(:disabled) {
          border-color: var(--danger, #ef4444);
          color: var(--danger, #ef4444);
          background: #fef2f2;
        }

        .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Dark mode */
        [data-theme="dark"] .file-upload-container {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }

        [data-theme="dark"] .drop-zone {
          background: var(--bg-tertiary, #334155);
        }

        [data-theme="dark"] .file-preview {
          background: var(--bg-secondary, #1e293b);
        }

        [data-theme="dark"] .btn-secondary {
          background: var(--bg-tertiary, #334155);
        }

        /* Responsive */
        .voice-alternative {
          margin: 24px 0;
        }

        .voice-divider {
          display: flex;
          align-items: center;
          text-align: center;
          margin: 20px 0;
          color: var(--text-muted, #94a3b8);
          font-size: 14px;
          font-weight: 500;
        }

        .voice-divider::before,
        .voice-divider::after {
          content: '';
          flex: 1;
          border-bottom: 1px solid var(--border, #e2e8f0);
        }

        .voice-divider span {
          padding: 0 16px;
        }

        .btn-voice {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          padding: 16px 24px;
          background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
          color: white;
          border: none;
          border-radius: 14px;
          cursor: pointer;
          font-size: 15px;
          font-weight: 600;
          transition: all 0.3s;
          box-shadow: 0 4px 15px -3px #8b5cf6;
        }

        .btn-voice:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px -5px #8b5cf6;
        }

        .btn-voice:active {
          transform: translateY(0);
        }

        @media (max-width: 600px) {
          .file-upload-container {
            padding: 24px 20px;
          }

          .file-upload-header {
            flex-direction: column;
            text-align: center;
          }

          .upload-icon-wrapper {
            margin: 0 auto;
          }

          .upload-actions {
            flex-direction: column;
          }

          .file-preview {
            flex-direction: column;
            text-align: center;
            padding: 20px;
          }

          .file-info {
            text-align: center;
          }

          .btn-voice {
            font-size: 14px;
            padding: 14px 20px;
          }
        }
      `}</style>
    </div>
  );
}
