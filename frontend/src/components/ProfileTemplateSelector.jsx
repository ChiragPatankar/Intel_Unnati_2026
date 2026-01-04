/**
 * Profile Template Selector
 * Shows use case templates: Personal, Work, Family, etc.
 */
export default function ProfileTemplateSelector({ onSelect, t }) {
  const templates = [
    {
      id: 'personal',
      name: t('templatePersonal') || '🏠 Personal',
      description: t('templatePersonalDesc') || 'For personal documents and ID cards',
      icon: '🏠',
      suggestedDocs: ['Aadhaar', 'PAN', 'Voter ID', 'Passport']
    },
    {
      id: 'work',
      name: t('templateWork') || '💼 Work',
      description: t('templateWorkDesc') || 'For professional and employment documents',
      icon: '💼',
      suggestedDocs: ['PAN', 'Passport', 'Driving License']
    },
    {
      id: 'family',
      name: t('templateFamily') || '👨‍👩‍👧 Family',
      description: t('templateFamilyDesc') || 'For family members\' documents',
      icon: '👨‍👩‍👧',
      suggestedDocs: ['Aadhaar', 'Voter ID']
    },
    {
      id: 'custom',
      name: t('templateCustom') || '✨ Custom',
      description: t('templateCustomDesc') || 'Create your own profile',
      icon: '✨',
      suggestedDocs: []
    }
  ];

  return (
    <div className="profile-templates">
      <div className="templates-header">
        <h3>{t('chooseTemplate') || 'Choose a profile template'}</h3>
        <p>{t('templateSubtitle') || 'Select a template to get started, or create a custom profile'}</p>
      </div>

      <div className="templates-grid">
        {templates.map(template => (
          <div
            key={template.id}
            className="template-card"
            onClick={() => onSelect(template)}
          >
            <div className="template-icon">{template.icon}</div>
            <h4>{template.name}</h4>
            <p>{template.description}</p>
            {template.suggestedDocs.length > 0 && (
              <div className="template-suggestions">
                <span className="suggestions-label">{t('suggestedDocs') || 'Suggested:'}</span>
                <div className="suggestions-tags">
                  {template.suggestedDocs.map(doc => (
                    <span key={doc} className="doc-tag">{doc}</span>
                  ))}
                </div>
              </div>
            )}
            <div className="template-action">
              <span>{t('select') || 'Select'}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .profile-templates {
          padding: 24px;
        }

        .templates-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .templates-header h3 {
          font-size: 22px;
          font-weight: 700;
          margin-bottom: 8px;
          color: var(--text-primary, #0f172a);
        }

        .templates-header p {
          font-size: 14px;
          color: var(--text-secondary, #475569);
        }

        .templates-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 20px;
        }

        .template-card {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 16px;
          padding: 24px;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
          overflow: hidden;
        }

        .template-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          transform: scaleX(0);
          transition: transform 0.3s;
        }

        .template-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 30px -10px rgba(99, 102, 241, 0.2);
          border-color: var(--primary, #6366f1);
        }

        .template-card:hover::before {
          transform: scaleX(1);
        }

        .template-icon {
          font-size: 40px;
          margin-bottom: 12px;
        }

        .template-card h4 {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 8px;
          color: var(--text-primary, #0f172a);
        }

        .template-card p {
          font-size: 13px;
          color: var(--text-secondary, #475569);
          margin-bottom: 16px;
          line-height: 1.5;
        }

        .template-suggestions {
          margin-bottom: 16px;
        }

        .suggestions-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--text-muted, #94a3b8);
          display: block;
          margin-bottom: 8px;
        }

        .suggestions-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .doc-tag {
          font-size: 11px;
          padding: 4px 10px;
          background: var(--bg-tertiary, #f1f5f9);
          border-radius: 6px;
          color: var(--text-secondary, #475569);
          font-weight: 500;
        }

        .template-action {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--primary, #6366f1);
          font-weight: 600;
          font-size: 14px;
          margin-top: auto;
        }

        @media (max-width: 768px) {
          .templates-grid {
            grid-template-columns: 1fr;
          }
        }

        [data-theme="dark"] .template-card {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }
      `}</style>
    </div>
  );
}

