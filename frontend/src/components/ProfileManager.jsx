import { useState, useEffect } from 'react';
import { 
  listProfiles, 
  getProfile, 
  createProfile, 
  deleteProfile,
  uploadDocumentToProfile,
  updateProfile
} from '../api';
import ProfileTemplateSelector from './ProfileTemplateSelector';

/**
 * Profile Manager Component
 * Allows users to create, view, and manage profiles for auto-fill
 * Now with template support
 */
export default function ProfileManager({ onProfileSelect, selectedProfile, t }) {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [error, setError] = useState(null);

  // Load profiles on mount
  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setLoading(true);
      const data = await listProfiles();
      setProfiles(data);
      setError(null);
    } catch (err) {
      setError(t('failedToLoad'));
      setProfiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setNewProfileName(template.name.replace(/[🏠💼👨‍👩‍👧✨]/g, '').trim() || '');
    setShowTemplates(false);
    setShowCreateForm(true);
  };

  const handleCreateProfile = async (e) => {
    e.preventDefault();
    if (!newProfileName.trim()) return;

    try {
      const profile = await createProfile(newProfileName.trim());
      setProfiles([profile, ...profiles]);
      setNewProfileName('');
      setShowCreateForm(false);
      setSelectedTemplate(null);
      onProfileSelect(profile);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteProfile = async (profileId, e) => {
    e.stopPropagation();
    if (!confirm(t('deleteConfirm'))) return;

    try {
      await deleteProfile(profileId);
      setProfiles(profiles.filter(p => p.id !== profileId));
      if (selectedProfile?.id === profileId) {
        onProfileSelect(null);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="profile-manager">
      <div className="profile-header">
        <h2>{t('myProfiles')}</h2>
        <button 
          className="add-btn"
          onClick={() => {
            if (!showTemplates && !showCreateForm) {
              setShowTemplates(true);
            } else {
              setShowTemplates(false);
              setShowCreateForm(false);
              setSelectedTemplate(null);
            }
          }}
        >
          {showTemplates || showCreateForm ? '✕' : t('newProfile')}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {/* Template Selector */}
      {showTemplates && (
        <ProfileTemplateSelector 
          onSelect={handleTemplateSelect}
          t={t}
        />
      )}

      {/* Create Profile Form */}
      {showCreateForm && (
        <form onSubmit={handleCreateProfile} className="create-form">
          {selectedTemplate && (
            <div className="template-badge">
              <span>{selectedTemplate.icon}</span>
              <span>{selectedTemplate.name}</span>
            </div>
          )}
          <input
            type="text"
            placeholder={t('profilePlaceholder')}
            value={newProfileName}
            onChange={(e) => setNewProfileName(e.target.value)}
            autoFocus
          />
          <button type="submit" disabled={!newProfileName.trim()}>
            {t('create')}
          </button>
        </form>
      )}

      {/* Profile List */}
      <div className="profile-list">
        {loading ? (
          <div className="loading">{t('loadingProfiles')}</div>
        ) : profiles.length === 0 ? (
          <div className="empty-state">
            <p>{t('noProfiles')}</p>
          </div>
        ) : (
          profiles.map(profile => (
            <div
              key={profile.id}
              className={`profile-item ${selectedProfile?.id === profile.id ? 'selected' : ''}`}
              onClick={() => onProfileSelect(profile)}
            >
              <div className="profile-info">
                <span className="profile-name">{profile.name}</span>
                <span className="profile-meta">
                  {profile.field_count} {t('fields')} • {profile.document_count} {t('docs')}
                </span>
              </div>
              <button 
                className="delete-btn"
                onClick={(e) => handleDeleteProfile(profile.id, e)}
                title={t('deleteConfirm')}
              >
                🗑️
              </button>
            </div>
          ))
        )}
      </div>

      <button className="refresh-btn" onClick={loadProfiles}>
        {t('refresh')}
      </button>
    </div>
  );
}
