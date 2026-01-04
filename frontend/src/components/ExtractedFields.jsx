/**
 * Editable form displaying extracted fields with confidence scores
 */
export default function ExtractedFields({ data, onFieldChange }) {
  if (!data || !data.entities) {
    return null;
  }

  const { entities, document_type, detected_language, notes, overall_confidence, timing } = data;

  // Get confidence level class
  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.85) return 'confidence-high';
    if (confidence >= 0.60) return 'confidence-medium';
    return 'confidence-low';
  };

  // Format field name for display
  const formatFieldName = (name) => {
    return name.replace(/_/g, ' ');
  };

  // Get confidence percentage
  const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(0)}%`;
  };

  return (
    <div className="results-section">
      <h2>📋 Extracted Data</h2>
      
      {/* Document type badge */}
      <div className="doc-type">
        📑 Document Type: <strong>{document_type?.toUpperCase() || 'UNKNOWN'}</strong>
        {detected_language && ` | Language: ${detected_language.toUpperCase()}`}
      </div>

      {/* Overall confidence */}
      <div style={{ marginBottom: '15px' }}>
        Overall Confidence: 
        <span 
          className={`confidence-badge ${getConfidenceClass(overall_confidence)}`}
          style={{ marginLeft: '8px' }}
        >
          {formatConfidence(overall_confidence)}
        </span>
      </div>

      {/* Editable fields */}
      {Object.entries(entities).map(([fieldName, fieldData]) => (
        <div key={fieldName} className="field-group">
          <div className="field-header">
            <label className="field-label">{formatFieldName(fieldName)}</label>
            <span className={`confidence-badge ${getConfidenceClass(fieldData.confidence)}`}>
              {formatConfidence(fieldData.confidence)} | {fieldData.match_type?.replace('_', ' ')}
            </span>
          </div>
          <input
            type="text"
            className="field-input"
            value={fieldData.value}
            onChange={(e) => onFieldChange(fieldName, e.target.value)}
            style={{
              borderColor: fieldData.confidence < 0.6 ? '#ffcdd2' : undefined,
            }}
          />
          {fieldData.confidence < 0.6 && (
            <small style={{ color: '#c62828' }}>⚠️ Low confidence - please verify</small>
          )}
        </div>
      ))}

      {/* Notes */}
      {notes && notes.length > 0 && (
        <div className="notes-section">
          <strong>📝 Notes:</strong>
          <ul>
            {notes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Timing information */}
      {timing && (
        <div className="timing-section">
          <strong>⏱️ Processing Time:</strong>
          <div className="timing-row">
            <span>Upload:</span>
            <span>{timing.upload_time_ms}ms</span>
          </div>
          <div className="timing-row">
            <span>OCR:</span>
            <span>{timing.ocr_time_ms}ms</span>
          </div>
          <div className="timing-row">
            <span>Extraction:</span>
            <span>{timing.extraction_time_ms}ms</span>
          </div>
          <div className="timing-row" style={{ fontWeight: 'bold', borderTop: '1px solid #ddd', paddingTop: '5px' }}>
            <span>Total:</span>
            <span>{timing.total_time_ms}ms</span>
          </div>
        </div>
      )}
    </div>
  );
}

