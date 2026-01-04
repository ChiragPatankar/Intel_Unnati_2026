/**
 * Smart Suggestions Component
 * Shows contextual suggestions based on current profile state
 * e.g., "Add PAN? Often used with Aadhaar"
 */
export default function SmartSuggestions({ profile, onAddDocument, t }) {
  if (!profile) return null;

  const existingDocs = profile.documents || [];
  const existingDocTypes = existingDocs.map(doc => doc.document_type?.toLowerCase() || '');

  // Smart suggestion rules
  const suggestions = [];

  // If has Aadhaar but no PAN
  if (existingDocTypes.includes('aadhaar') && !existingDocTypes.includes('pan')) {
    suggestions.push({
      type: 'pan',
      message: t('suggestPan') || 'Add PAN card? Often used together with Aadhaar',
      icon: '💳',
      priority: 'high'
    });
  }

  // If has PAN but no Aadhaar
  if (existingDocTypes.includes('pan') && !existingDocTypes.includes('aadhaar')) {
    suggestions.push({
      type: 'aadhaar',
      message: t('suggestAadhaar') || 'Add Aadhaar card? Commonly paired with PAN',
      icon: '🆔',
      priority: 'high'
    });
  }

  // If has Aadhaar/PAN but no Voter ID
  if ((existingDocTypes.includes('aadhaar') || existingDocTypes.includes('pan')) && 
      !existingDocTypes.includes('voter_id')) {
    suggestions.push({
      type: 'voter_id',
      message: t('suggestVoterId') || 'Add Voter ID? Useful for government forms',
      icon: '🗳️',
      priority: 'medium'
    });
  }

  // If has basic docs but no Passport
  if (existingDocTypes.length >= 2 && !existingDocTypes.includes('passport')) {
    suggestions.push({
      type: 'passport',
      message: t('suggestPassport') || 'Add Passport? Required for international travel',
      icon: '✈️',
      priority: 'medium'
    });
  }

  // If has basic docs but no Driving License
  if (existingDocTypes.length >= 2 && !existingDocTypes.includes('driving_license')) {
    suggestions.push({
      type: 'driving_license',
      message: t('suggestDrivingLicense') || 'Add Driving License? Useful for vehicle-related forms',
      icon: '🚗',
      priority: 'low'
    });
  }

  if (suggestions.length === 0) return null;

  // Sort by priority
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  suggestions.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  return (
    <div className="smart-suggestions">
      <div className="suggestions-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span>{t('smartSuggestions') || '💡 Smart Suggestions'}</span>
      </div>

      <div className="suggestions-list">
        {suggestions.slice(0, 3).map((suggestion, index) => (
          <div 
            key={index}
            className={`suggestion-item priority-${suggestion.priority}`}
            onClick={() => onAddDocument && onAddDocument(suggestion.type)}
          >
            <div className="suggestion-icon">{suggestion.icon}</div>
            <div className="suggestion-content">
              <p>{suggestion.message}</p>
              {onAddDocument && (
                <button className="suggestion-action">
                  {t('addNow') || 'Add Now'} →
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .smart-suggestions {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
          border: 1px solid var(--border, #e2e8f0);
          border-left: 4px solid var(--primary, #6366f1);
          border-radius: 12px;
          padding: 20px;
          margin: 24px 0;
        }

        .suggestions-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 700;
          color: var(--primary, #6366f1);
          margin-bottom: 16px;
        }

        .suggestions-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .suggestion-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          background: var(--bg-secondary, white);
          border-radius: 10px;
          border: 1px solid var(--border, #e2e8f0);
          cursor: pointer;
          transition: all 0.2s;
        }

        .suggestion-item:hover {
          border-color: var(--primary, #6366f1);
          transform: translateX(4px);
        }

        .suggestion-item.priority-high {
          border-left: 3px solid var(--success, #10b981);
        }

        .suggestion-item.priority-medium {
          border-left: 3px solid var(--warning, #f59e0b);
        }

        .suggestion-item.priority-low {
          border-left: 3px solid var(--gray-400, #9ca3af);
        }

        .suggestion-icon {
          font-size: 24px;
          flex-shrink: 0;
        }

        .suggestion-content {
          flex: 1;
        }

        .suggestion-content p {
          font-size: 14px;
          color: var(--text-primary, #0f172a);
          margin: 0 0 6px 0;
          line-height: 1.5;
        }

        .suggestion-action {
          background: none;
          border: none;
          color: var(--primary, #6366f1);
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          padding: 0;
          transition: all 0.2s;
        }

        .suggestion-action:hover {
          color: var(--primary-dark, #4f46e5);
        }

        @media (max-width: 600px) {
          .smart-suggestions {
            padding: 16px;
          }

          .suggestion-item {
            flex-direction: column;
            text-align: center;
          }
        }

        [data-theme="dark"] .suggestion-item {
          background: var(--bg-secondary, #1e293b);
        }
      `}</style>
    </div>
  );
}

