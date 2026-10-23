/**
 * MRI segmentation viewer.
 *
 * Renders the raw MRI slice next to the model's tumour-mask overlay. Both
 * images are PNGs produced by the backend (base64 encoded).
 */

function toDataUri(base64) {
  return base64 ? `data:image/png;base64,${base64}` : null;
}

function MRIViewer({ analysis, loading, error }) {
  if (loading) {
    return (
      <div className="analysis-view analysis-placeholder">
        <p>Running inference on the global model…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-view analysis-placeholder analysis-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!analysis?.available) {
    return (
      <div className="analysis-view analysis-placeholder">
        <p>{analysis?.reason ?? "No trained model available yet."}</p>
        <span>Train the baseline or the federated model first.</span>
      </div>
    );
  }

  const mri = toDataUri(analysis.mri_png);
  const mask = toDataUri(analysis.mask_png);

  return (
    <div className="analysis-view">
      <div className="scan-container">
        {mri ? (
          <img className="scan-image" src={mri} alt="MRI slice" />
        ) : (
          <div className="scan-image brain-placeholder">🧠</div>
        )}
        <div className="scan-label">
          <strong>Original MRI Scan</strong>
          <span>
            Sample #{analysis.sample_index} · slice {analysis.slice_index}
          </span>
        </div>
      </div>

      <div className="analysis-arrow">→</div>

      <div className="scan-container">
        {mask ? (
          <img className="scan-image segmentation-image" src={mask} alt="Tumor mask" />
        ) : (
          <div className="scan-image segmentation-image segmentation-placeholder">
            🎯
          </div>
        )}
        <div className="scan-label">
          <strong>Predicted Tumor Mask</strong>
          <span>AI segmentation output</span>
        </div>
      </div>
    </div>
  );
}

export default MRIViewer;
