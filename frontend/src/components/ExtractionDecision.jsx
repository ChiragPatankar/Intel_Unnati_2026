/**
 * Extraction Decision Component
 * Shows "Save or Use Once?" after data extraction
 * Progressive disclosure - decision point AFTER extraction
 */
export default function ExtractionDecision({ 
  extractedData, 
  onSaveToProfile, 
  onUseOnce, 
  onEdit,
  t 
}) {
  const fieldCount = Object.keys(extractedData?.entities || {}).length;
  const successMessage = t('extractionSuccess') || 'Extracted successfully!';

  return (
    <div className="extraction-decision">
      <div className="decision-header">
        <div className="success-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3>✅ {fieldCount > 0 ? `Extracted ${fieldCount} ${fieldCount === 1 ? 'field' : 'fields'} successfully!` : successMessage}</h3>
        <p>{t('whatNext') || 'What would you like to do with this data?'}</p>
      </div>

      <div className="decision-options">
        {/* Option 1: Save to Profile */}
        <div className="decision-card save" onClick={onSaveToProfile}>
          <div className="card-header">
            <div className="card-icon save-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
            </div>
            <h4>{t('saveToProfile') || '💾 Save to Profile'}</h4>
          </div>
          <p>{t('saveToProfileDesc') || 'Store this data for future use. Auto-fill any form with Chrome extension.'}</p>
          <div className="card-benefits">
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('reuseAnywhere') || 'Reuse anywhere, anytime'}</span>
            </div>
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('autoFillForms') || 'Auto-fill forms with extension'}</span>
            </div>
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('secureStorage') || 'Secure, encrypted storage'}</span>
            </div>
          </div>
          <button className="decision-btn save-btn">
            {t('saveNow') || 'Save Now'}
          </button>
        </div>

        {/* Option 2: Use Once */}
        <div className="decision-card use-once" onClick={onUseOnce}>
          <div className="card-header">
            <div className="card-icon use-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <h4>{t('useOnce') || '⚡ Use Once'}</h4>
          </div>
          <p>{t('useOnceDesc') || 'Just need this data now? Download or copy it. No storage needed.'}</p>
          <div className="card-benefits">
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('downloadJSON') || 'Download as JSON'}</span>
            </div>
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('copyClipboard') || 'Copy to clipboard'}</span>
            </div>
            <div className="benefit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>{t('noStorage') || 'No storage required'}</span>
            </div>
          </div>
          <button className="decision-btn use-btn">
            {t('useNow') || 'Use Now'}
          </button>
        </div>
      </div>

      <div className="decision-footer">
        <button className="edit-btn" onClick={onEdit}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          {t('editFields') || 'Edit fields before deciding'}
        </button>
      </div>

      <style>{`
        .extraction-decision {
          max-width: 900px;
          margin: 0 auto;
          padding: 32px 24px;
          animation: fadeSlideUp 0.4s ease-out;
        }

        .decision-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .success-icon {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          margin: 0 auto 20px;
          box-shadow: 0 8px 25px -5px #10b981;
        }

        .decision-header h3 {
          font-size: 24px;
          font-weight: 700;
          margin-bottom: 8px;
          color: var(--text-primary, #0f172a);
        }

        .decision-header p {
          font-size: 16px;
          color: var(--text-secondary, #475569);
        }

        .decision-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 24px;
          margin-bottom: 24px;
        }

        .decision-card {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 20px;
          padding: 28px;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
          overflow: hidden;
        }

        .decision-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          transform: scaleX(0);
          transition: transform 0.3s;
        }

        .decision-card.save::before {
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        }

        .decision-card.use-once::before {
          background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        }

        .decision-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
        }

        .decision-card:hover::before {
          transform: scaleX(1);
        }

        .card-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 16px;
        }

        .card-icon {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .save-icon {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .use-icon {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }

        .card-header h4 {
          font-size: 20px;
          font-weight: 700;
          color: var(--text-primary, #0f172a);
        }

        .decision-card p {
          font-size: 14px;
          color: var(--text-secondary, #475569);
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .card-benefits {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 24px;
        }

        .benefit {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          color: var(--text-secondary, #475569);
        }

        .benefit svg {
          color: var(--success, #10b981);
          flex-shrink: 0;
        }

        .decision-btn {
          width: 100%;
          padding: 14px 24px;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s;
        }

        .save-btn {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }

        .save-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px -5px #10b981;
        }

        .use-btn {
          background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
          color: white;
        }

        .use-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px -5px #6366f1;
        }

        .decision-footer {
          text-align: center;
          padding-top: 24px;
          border-top: 1px solid var(--border, #e2e8f0);
        }

        .edit-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          background: var(--bg-tertiary, #f1f5f9);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 10px;
          color: var(--text-secondary, #475569);
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .edit-btn:hover {
          border-color: var(--primary, #6366f1);
          color: var(--primary, #6366f1);
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
          .decision-options {
            grid-template-columns: 1fr;
          }
        }

        [data-theme="dark"] .decision-card {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }
      `}</style>
    </div>
  );
}

