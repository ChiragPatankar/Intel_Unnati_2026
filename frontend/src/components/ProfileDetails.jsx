import { useState, useEffect, useRef } from 'react';
import { getProfile, uploadDocumentToProfile, updateProfile } from '../api';
import SmartSuggestions from './SmartSuggestions';

/**
 * Profile Details Component
 * Shows profile fields and allows document upload
 */
export default function ProfileDetails({ profileId, onUpdate }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editedFields, setEditedFields] = useState({});
  const [status, setStatus] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (profileId) {
      loadProfile();
    }
  }, [profileId]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await getProfile(profileId);
      setProfile(data);
      setEditedFields(data.fields || {});
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setStatus({ type: 'loading', message: `Processing ${file.name}...` });
      
      const result = await uploadDocumentToProfile(profileId, file);
      
      setProfile(result.profile);
      setEditedFields(result.profile.fields || {});
      setStatus({ 
        type: 'success', 
        message: `✅ Extracted ${Object.keys(result.extracted_fields).length} fields from ${result.document_type}` 
      });
      
      if (onUpdate) onUpdate(result.profile);
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSaveEdits = async () => {
    try {
      const updated = await updateProfile(profileId, editedFields);
      setProfile(updated);
      setEditing(false);
      setStatus({ type: 'success', message: '✅ Profile saved!' });
      if (onUpdate) onUpdate(updated);
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    }
  };

  const handleFieldChange = (key, value) => {
    setEditedFields(prev => ({ ...prev, [key]: value }));
  };

  const handleAddField = () => {
    const fieldName = prompt('Enter field name:');
    if (fieldName && fieldName.trim()) {
      setEditedFields(prev => ({ 
        ...prev, 
        [fieldName.trim().toLowerCase().replace(/\s+/g, '_')]: '' 
      }));
    }
  };

  if (loading) {
    return <div className="profile-details loading">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="profile-details error">Profile not found</div>;
  }

  return (
    <div className="profile-details">
      <div className="profile-details-header">
        <h2>{profile.name}</h2>
        <div className="header-actions">
          {editing ? (
            <>
              <button onClick={handleSaveEdits}>💾 Save</button>
              <button onClick={() => { setEditing(false); setEditedFields(profile.fields || {}); }}>
                Cancel
              </button>
            </>
          ) : (
            <button onClick={() => setEditing(true)}>✏️ Edit</button>
          )}
        </div>
      </div>

      {/* Status */}
      {status && (
        <div className={`status ${status.type}`}>
          {status.message}
        </div>
      )}

      {/* Upload Document */}
      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
          onChange={handleFileUpload}
          disabled={uploading}
          style={{ display: 'none' }}
        />
        <button 
          className="upload-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? '⏳ Processing...' : '📄 Upload Document'}
        </button>
        <span className="upload-hint">
          Add Aadhaar, PAN, or Voter ID to extract data
        </span>
      </div>

      {/* Smart Suggestions */}
      {profile && (
        <SmartSuggestions 
          profile={profile}
          onAddDocument={(docType) => {
            // Trigger file upload for suggested document
            fileInputRef.current?.click();
          }}
          t={(key) => key}
        />
      )}

      {/* Fields */}
      <div className="fields-section">
        <div className="fields-header">
          <h3>Stored Information</h3>
          {editing && (
            <button className="add-field-btn" onClick={handleAddField}>
              + Add Field
            </button>
          )}
        </div>

        {Object.keys(editedFields).length === 0 ? (
          <div className="empty-fields">
            <p>No data yet. Upload a document to get started!</p>
          </div>
        ) : (
          <div className="fields-grid">
            {Object.entries(editedFields).map(([key, value]) => (
              <div key={key} className="field-row">
                <label>{key.replace(/_/g, ' ')}</label>
                {editing ? (
                  <input
                    type="text"
                    value={value || ''}
                    onChange={(e) => handleFieldChange(key, e.target.value)}
                  />
                ) : (
                  <span className="field-value">{maskSensitive(key, value) || '-'}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Documents List */}
      {profile.documents && profile.documents.length > 0 && (
        <div className="documents-section">
          <h3>📚 Uploaded Documents</h3>
          <ul className="documents-list">
            {profile.documents.map((doc, idx) => (
              <li key={idx}>
                <span className="doc-type">{doc.type}</span>
                <span className="doc-date">
                  {new Date(doc.added_at).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Chrome Extension Notice */}
      <div className="extension-notice">
        <h4>🔌 Use with Chrome Extension</h4>
        <p>
          Install the Form Filling Assistant extension to auto-fill forms 
          on any website using this profile's data.
        </p>
      </div>
    </div>
  );
}

/**
 * Mask sensitive data for display
 */
function maskSensitive(field, value) {
  if (!value) return value;
  
  if (field.includes('aadhaar') && value.length >= 12) {
    return 'XXXX XXXX ' + value.slice(-4);
  }
  if (field.includes('pan') && value.length >= 10) {
    return value.slice(0, 3) + 'XXXXX' + value.slice(-2);
  }
  return value;
}

