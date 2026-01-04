/**
 * Form Preview Component
 * Shows the filled form for review and editing before PDF generation
 */
export default function FormPreview({ 
  formTemplate, 
  formData, 
  onFieldChange, 
  onGeneratePDF,
  onBack,
  t 
}) {
  const handleFieldChange = (fieldName, value) => {
    if (onFieldChange) {
      onFieldChange(fieldName, value);
    }
  };

  const handleGenerate = () => {
    if (onGeneratePDF) {
      onGeneratePDF();
    }
  };

  const completionRate = formTemplate && formData ? 
    (Object.values(formData).filter(v => {
      if (!v) return false;
      // Handle string values
      if (typeof v === 'string') return v.trim().length > 0;
      // Handle other types (numbers, booleans, etc.)
      return true;
    }).length / Object.keys(formTemplate.fields || {}).length * 100).toFixed(0) : 0;

  return (
    <div className="form-preview-container">
      <div className="preview-header">
        <button className="back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          {t('back') || 'Back'}
        </button>
        <div className="header-content">
          <h2>{formTemplate?.name || t('formPreview') || 'Form Preview'}</h2>
          <div className="completion-badge">
            <span>{completionRate}% {t('complete') || 'Complete'}</span>
          </div>
        </div>
      </div>

      <div className="preview-content">
        <div className="form-preview-card">
          <div className="form-fields">
            {formTemplate && Object.entries(formTemplate.fields || {}).map(([fieldName, fieldConfig]) => {
              // Ensure value is always a string
              const rawValue = formData?.[fieldName];
              const value = rawValue != null ? String(rawValue) : "";
              const isRequired = fieldConfig.required;
              
              return (
                <div key={fieldName} className={`form-field ${!value && isRequired ? 'missing' : ''}`}>
                  <label>
                    {fieldConfig.label}
                    {isRequired && <span className="required-star">*</span>}
                  </label>
                  {fieldConfig.type === 'textarea' ? (
                    <textarea
                      value={value}
                      onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                      placeholder={t('enterValue') || 'Enter value...'}
                      rows={3}
                      className="field-input"
                    />
                  ) : fieldConfig.type === 'select' ? (
                    <select
                      value={value}
                      onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                      className="field-input"
                    >
                      <option value="">{t('selectOption') || 'Select...'}</option>
                      {(fieldConfig.options || (fieldName === 'gender' ? ['Male', 'Female', 'Other'] : [])).map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={fieldConfig.type === 'date' ? 'date' : fieldConfig.type === 'email' ? 'email' : fieldConfig.type === 'tel' ? 'tel' : 'text'}
                      value={value}
                      onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                      placeholder={t('enterValue') || 'Enter value...'}
                      className="field-input"
                    />
                  )}
                  {!value && isRequired && (
                    <span className="field-error">{t('required') || 'This field is required'}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="preview-actions">
          <button className="btn-secondary" onClick={onBack}>
            {t('editDocuments') || 'Edit Documents'}
          </button>
          <button 
            className="btn-primary generate-btn"
            onClick={handleGenerate}
            disabled={completionRate < 100}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            {t('generatePDF') || 'Generate PDF'}
          </button>
        </div>
      </div>

      <style>{`
        .form-preview-container {
          max-width: 900px;
          margin: 0 auto;
          padding: 24px;
          animation: fadeSlideUp 0.4s ease-out;
        }

        .preview-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 28px;
        }

        .back-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 16px;
          background: var(--bg-tertiary, #f1f5f9);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 10px;
          color: var(--text-secondary, #475569);
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .back-btn:hover {
          border-color: var(--primary, #6366f1);
          color: var(--primary, #6366f1);
        }

        .header-content {
          flex: 1;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-content h2 {
          font-size: 24px;
          font-weight: 700;
          color: var(--text-primary, #0f172a);
        }

        .completion-badge {
          padding: 8px 16px;
          background: linear-gradient(135deg, var(--success, #10b981) 0%, #059669 100%);
          color: white;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 700;
        }

        .form-preview-card {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          border: 1px solid var(--border, #e2e8f0);
          border-radius: 20px;
          padding: 32px;
          margin-bottom: 24px;
        }

        .form-fields {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .form-field {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-field.missing {
          border-left: 3px solid var(--danger, #ef4444);
          padding-left: 12px;
        }

        .form-field label {
          font-size: 13px;
          font-weight: 700;
          color: var(--text-secondary, #475569);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .required-star {
          color: var(--danger, #ef4444);
          margin-left: 4px;
        }

        .field-input {
          padding: 14px 16px;
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 10px;
          font-size: 15px;
          font-weight: 500;
          background: var(--bg-secondary, white);
          color: var(--text-primary, #0f172a);
          transition: all 0.2s;
          font-family: inherit;
        }

        .field-input:focus {
          outline: none;
          border-color: var(--primary, #6366f1);
          box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
        }

        .field-input textarea {
          resize: vertical;
          min-height: 80px;
        }

        .field-error {
          font-size: 12px;
          color: var(--danger, #ef4444);
          font-weight: 500;
        }

        .preview-actions {
          display: flex;
          gap: 16px;
          justify-content: flex-end;
        }

        .btn-secondary {
          padding: 14px 28px;
          background: var(--bg-tertiary, #f1f5f9);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 12px;
          color: var(--text-secondary, #475569);
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary:hover {
          border-color: var(--primary, #6366f1);
          color: var(--primary, #6366f1);
        }

        .generate-btn {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 14px 28px;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #4f46e5 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 15px -3px var(--primary, #6366f1);
        }

        .generate-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px -5px var(--primary, #6366f1);
        }

        .generate-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @keyframes fadeSlideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .preview-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .header-content {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .preview-actions {
            flex-direction: column;
          }
        }

        [data-theme="dark"] .form-preview-card {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }
      `}</style>
    </div>
  );
}

