/**
 * Form Template Selector Component
 * Allows users to select which government form they need to fill
 */
export default function FormTemplateSelector({ onSelect, t }) {
  const formTemplates = [
    {
      id: 'aadhaar_update',
      name: t('formAadhaarUpdate') || 'Aadhaar Update Form',
      description: t('formAadhaarUpdateDesc') || 'Update your Aadhaar card details',
      icon: '🆔',
      requiredDocs: ['Aadhaar Card'],
      optionalDocs: ['PAN Card', 'Voter ID']
    },
    {
      id: 'ration_card',
      name: t('formRationCard') || 'Ration Card Application',
      description: t('formRationCardDesc') || 'Apply for a new ration card',
      icon: '🛒',
      requiredDocs: ['Aadhaar Card', 'Address Proof'],
      optionalDocs: ['Voter ID']
    },
    {
      id: 'birth_certificate',
      name: t('formBirthCertificate') || 'Birth Certificate Request',
      description: t('formBirthCertificateDesc') || 'Request a copy of birth certificate',
      icon: '👶',
      requiredDocs: ['Aadhaar Card', 'Parent ID'],
      optionalDocs: ['School Certificate']
    },
    {
      id: 'driving_license',
      name: t('formDrivingLicense') || 'Driving License Application',
      description: t('formDrivingLicenseDesc') || 'Apply for driving license',
      icon: '🚗',
      requiredDocs: ['Aadhaar Card', 'Address Proof'],
      optionalDocs: ['PAN Card', 'Medical Certificate']
    },
    {
      id: 'passport',
      name: t('formPassport') || 'Passport Application',
      description: t('formPassportDesc') || 'Apply for passport',
      icon: '✈️',
      requiredDocs: ['Aadhaar Card', 'Birth Certificate', 'Address Proof'],
      optionalDocs: ['PAN Card', 'Voter ID']
    },
    {
      id: 'voter_id',
      name: t('formVoterId') || 'Voter ID Enrollment',
      description: t('formVoterIdDesc') || 'Enroll for voter ID card',
      icon: '🗳️',
      requiredDocs: ['Aadhaar Card', 'Address Proof'],
      optionalDocs: ['Birth Certificate']
    }
  ];

  return (
    <div className="form-template-selector">
      <div className="selector-header">
        <h2>{t('selectFormType') || 'Which form do you need?'}</h2>
        <p>{t('selectFormSubtitle') || 'Choose the government form you want to fill'}</p>
      </div>

      <div className="forms-grid">
        {formTemplates.map(form => (
          <div
            key={form.id}
            className="form-card"
            onClick={() => onSelect(form)}
          >
            <div className="form-icon">{form.icon}</div>
            <h3>{form.name}</h3>
            <p className="form-description">{form.description}</p>
            
            <div className="form-requirements">
              <div className="required-docs">
                <span className="req-label">{t('required') || 'Required:'}</span>
                <div className="doc-tags">
                  {form.requiredDocs.map((doc, idx) => (
                    <span key={idx} className="doc-tag required">{doc}</span>
                  ))}
                </div>
              </div>
              {form.optionalDocs.length > 0 && (
                <div className="optional-docs">
                  <span className="req-label">{t('optional') || 'Optional:'}</span>
                  <div className="doc-tags">
                    {form.optionalDocs.map((doc, idx) => (
                      <span key={idx} className="doc-tag optional">{doc}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="form-action">
              <span>{t('select') || 'Select'}</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .form-template-selector {
          max-width: 1200px;
          margin: 0 auto;
          padding: 32px 24px;
          animation: fadeSlideUp 0.5s ease-out;
        }

        .selector-header {
          text-align: center;
          margin-bottom: 40px;
        }

        .selector-header h2 {
          font-size: 28px;
          font-weight: 800;
          margin-bottom: 12px;
          color: var(--text-primary, #0f172a);
          background: linear-gradient(135deg, var(--primary, #6366f1) 0%, #8b5cf6 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .selector-header p {
          font-size: 16px;
          color: var(--text-secondary, #475569);
        }

        .forms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 24px;
        }

        .form-card {
          background: var(--glass-bg, rgba(255, 255, 255, 0.8));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 2px solid var(--border, #e2e8f0);
          border-radius: 20px;
          padding: 28px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;
        }

        .form-card::before {
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

        .form-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.25);
          border-color: var(--primary, #6366f1);
        }

        .form-card:hover::before {
          transform: scaleX(1);
        }

        .form-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .form-card h3 {
          font-size: 20px;
          font-weight: 700;
          margin-bottom: 8px;
          color: var(--text-primary, #0f172a);
        }

        .form-description {
          font-size: 14px;
          color: var(--text-secondary, #475569);
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .form-requirements {
          margin-bottom: 20px;
        }

        .required-docs,
        .optional-docs {
          margin-bottom: 12px;
        }

        .req-label {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--text-muted, #94a3b8);
          display: block;
          margin-bottom: 8px;
        }

        .doc-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .doc-tag {
          font-size: 11px;
          padding: 4px 10px;
          border-radius: 6px;
          font-weight: 500;
        }

        .doc-tag.required {
          background: var(--danger-light, #fee2e2);
          color: var(--danger, #ef4444);
        }

        .doc-tag.optional {
          background: var(--bg-tertiary, #f1f5f9);
          color: var(--text-secondary, #475569);
        }

        .form-action {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          color: var(--primary, #6366f1);
          font-weight: 600;
          font-size: 15px;
          padding-top: 16px;
          border-top: 1px solid var(--border, #e2e8f0);
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
          .forms-grid {
            grid-template-columns: 1fr;
          }

          .selector-header h2 {
            font-size: 24px;
          }
        }

        [data-theme="dark"] .form-card {
          background: var(--glass-bg, rgba(30, 41, 59, 0.8));
        }
      `}</style>
    </div>
  );
}

