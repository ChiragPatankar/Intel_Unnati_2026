/**
 * Landing Page Component
 * Unified entry point - asks "What do you want to do?"
 */
export default function LandingPage({ onAction, t, profiles = [] }) {
  return (
    <div className="landing-page">
      <div className="landing-hero">
        <h2>{t('whatDoYouWant') || 'What do you want to do today?'}</h2>
        <p className="landing-subtitle">{t('landingSubtitle') || 'Choose how you want to use Smart Form Filler'}</p>
      </div>

      <div className="landing-options">
        {/* Option 1: Fill a form right now */}
        <div className="landing-card primary" onClick={() => onAction('upload')}>
          <div className="card-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <div className="card-content">
            <h3>{t('fillFormNow') || '🎯 Fill a form right now'}</h3>
            <p>{t('fillFormNowDesc') || 'Quick: Upload document → Extract → Auto-fill'}</p>
            <div className="card-action">
              <span>{t('start') || 'Start'}</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Option 2: Save documents for future */}
        <div className="landing-card" onClick={() => onAction('profiles')}>
          <div className="card-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <div className="card-content">
            <h3>{t('saveDocuments') || '💾 Save my documents for future use'}</h3>
            <p>{t('saveDocumentsDesc') || 'Create profile → Use anywhere, anytime'}</p>
            <div className="card-action">
              <span>{t('setupProfile') || 'Setup Profile'}</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        </div>

        {/* Option 3: Manage existing profiles */}
        {profiles.length > 0 && (
          <div className="landing-card" onClick={() => onAction('profiles')}>
            <div className="card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div className="card-content">
              <h3>{t('myProfiles') || `👥 My saved profiles (${profiles.length})`}</h3>
              <p>{t('manageProfilesDesc') || 'View and manage your saved profiles'}</p>
              <div className="card-action">
                <span>{t('manage') || 'Manage'}</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .landing-page {
          max-width: 1000px;
          margin: 0 auto;
          padding: 40px 24px;
          animation: fadeSlideUp 0.5s ease-out;
        }

        .landing-hero {
          text-align: center;
          margin-bottom: 48px;
        }

        .landing-hero h2 {
          font-size: 32px;
          font-weight: 800;
          margin-bottom: 12px;
          color: var(--text-primary, #0f172a);
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .landing-subtitle {
          font-size: 16px;
          color: var(--text-secondary, #475569);
          font-weight: 500;
        }

        .landing-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 24px;
        }

        .landing-card {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 24px;
          padding: 32px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;
        }

        .landing-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          transform: scaleX(0);
          transition: transform 0.3s;
        }

        .landing-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.2);
          border-color: var(--primary, #6366f1);
        }

        .landing-card:hover::before {
          transform: scaleX(1);
        }

        .landing-card.primary {
          border-color: var(--primary, #6366f1);
          background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        }

        .landing-card.primary::before {
          transform: scaleX(1);
        }

        .card-icon {
          width: 72px;
          height: 72px;
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          border-radius: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          margin-bottom: 20px;
          box-shadow: 0 8px 20px -5px var(--primary, #6366f1);
        }

        .landing-card.primary .card-icon {
          background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
          box-shadow: 0 8px 20px -5px #ef4444;
        }

        .card-content h3 {
          font-size: 20px;
          font-weight: 700;
          margin-bottom: 8px;
          color: var(--text-primary, #0f172a);
        }

        .card-content p {
          font-size: 14px;
          color: var(--text-secondary, #475569);
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .card-action {
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--primary, #6366f1);
          font-weight: 600;
          font-size: 15px;
        }

        .landing-card.primary .card-action {
          color: #ef4444;
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
          .landing-options {
            grid-template-columns: 1fr;
          }

          .landing-hero h2 {
            font-size: 24px;
          }
        }

        [data-theme="dark"] .landing-card {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }
      `}</style>
    </div>
  );
}

