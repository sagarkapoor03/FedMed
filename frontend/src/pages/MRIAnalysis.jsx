import { useCallback, useEffect, useState } from "react";

import MRIViewer from "../components/MRIViewer";
import StatCard from "../components/StatCard";

/**
 * MRI segmentation explorer.
 *
 * Runs the trained global model over a held-out validation volume and
 * renders the tumour mask the backend returns.
 */
function MRIAnalysis({ fed }) {
  const { actions, latest } = fed;

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [model, setModel] = useState("federated");
  const [sample, setSample] = useState("");

  const runAnalysis = useCallback(
    async (which = model, index = null) => {
      setLoading(true);
      setError(null);
      try {
        const result = await actions.analyze(which, index);
        setAnalysis(result);
      } catch (err) {
        setError(err.message);
        setAnalysis(null);
      } finally {
        setLoading(false);
      }
    },
    [actions, model],
  );

  useEffect(() => {
    // Kick off the first inference once the page mounts. The state
    // updates happen in the promise callback, not synchronously.
    let cancelled = false;

    actions
      .analyze("federated", null)
      .then((result) => {
        if (!cancelled) setAnalysis(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [actions]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const index = sample === "" ? null : Number(sample);
    runAnalysis(model, index);
  };

  const dataset = analysis?.dataset;
  const modelDice = analysis?.available ? analysis.volume_dice : null;
  const totalScans = dataset?.num_val ?? 0;
  const trainScans = dataset?.num_train ?? 0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>MRI Analysis</h1>
          <p>AI-powered brain tumor segmentation analysis</p>
        </div>

        <div className="training-status">
          <span className="training-dot" />
          {analysis?.available ? "Model Ready" : "Awaiting Model"}
        </div>
      </div>

      <div className="training-stats">
        <StatCard
          label="Training Volumes"
          value={trainScans}
          caption="Pooled across all hospitals"
        />
        <StatCard
          label="Held-out Volumes"
          value={totalScans}
          caption="Used for validation"
        />
        <StatCard
          label="Tumour Voxels Found"
          value={analysis?.tumor_voxels ?? "—"}
          caption={
            analysis?.tumor_fraction
              ? `${analysis.tumor_fraction}% of the volume`
              : "Run an analysis"
          }
        />
        <StatCard
          label="Volume Dice Score"
          value={modelDice !== null ? `${modelDice}%` : "—"}
          caption={
            latest
              ? `Global model, round ${latest.round}`
              : "No federated round yet"
          }
          tone="success"
        />
      </div>

      <div className="panel mri-analysis-panel">
        <div className="panel-header">
          <div>
            <h3>Latest MRI Analysis</h3>
            <p>Brain tumor segmentation using the global federated model</p>
          </div>
          <span className="badge">AI Analysis</span>
        </div>

        <form className="analysis-controls" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="model">Model</label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option value="federated">Federated global model</option>
              <option value="baseline">Centralized baseline</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="sample">Sample index</label>
            <input
              id="sample"
              type="number"
              min="0"
              placeholder="auto"
              value={sample}
              onChange={(e) => setSample(e.target.value)}
            />
          </div>

          <button type="submit" className="save-button" disabled={loading}>
            {loading ? "Analyzing…" : "Run Analysis"}
          </button>
        </form>

        <MRIViewer analysis={analysis} loading={loading} error={error} />

        {analysis?.available ? (
          <div className="analysis-result">
            <div className="result-item">
              <span>Segmentation Accuracy</span>
              <strong>{analysis.volume_dice}%</strong>
            </div>
            <div className="result-item">
              <span>Slice Dice Score</span>
              <strong>{analysis.slice_dice}%</strong>
            </div>
            <div className="result-item">
              <span>Tumour Status</span>
              <strong className="tumor-detected">
                ● {analysis.tumor_voxels > 0 ? "Detected" : "None"}
              </strong>
            </div>
            <div className="result-item">
              <span>Model</span>
              <strong>
                {analysis.model === "baseline" ? "FedMed-Base" : "FedMed-v1.0"}
              </strong>
            </div>
          </div>
        ) : null}

        {analysis?.per_class_dice ? (
          <div className="panel class-dice-panel">
            <div className="panel-header">
              <div>
                <h3>Per-class Dice</h3>
                <p>Volume-level scores for each tumour sub-region</p>
              </div>
            </div>
            <div className="class-dice-grid">
              {Object.entries(analysis.per_class_dice).map(([cls, value]) => (
                <div className="class-dice-item" key={cls}>
                  <span>{analysis.class_names?.[cls] ?? `Class ${cls}`}</span>
                  <strong>{Number(value).toFixed(2)}%</strong>
                  <div className="mini-progress">
                    <div
                      className="mini-progress-fill"
                      style={{ width: `${Math.min(100, value)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className="panel recent-scans">
        <div className="panel-header">
          <div>
            <h3>Dataset Distribution</h3>
            <p>Non-IID partition across the participating hospitals</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Hospital</th>
                <th>Node ID</th>
                <th>Training Volumes</th>
                <th>Scanner Bias</th>
              </tr>
            </thead>
            <tbody>
              {(dataset?.hospitals ?? []).map((h) => (
                <tr key={h.hospital_id}>
                  <td>
                    <strong>{h.hospital_id.replace("hospital-", "Hospital ")}</strong>
                  </td>
                  <td>{h.node_id}</td>
                  <td>{h.train}</td>
                  <td>{Number(h.scanner_bias).toFixed(2)}</td>
                </tr>
              ))}
              {!dataset?.hospitals?.length ? (
                <tr>
                  <td colSpan="4" className="muted">
                    Dataset manifest not available.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      <div className="privacy-notice">
        <div className="privacy-icon">🔐</div>
        <div>
          <h3>Privacy-Preserving Analysis</h3>
          <p>
            MRI data remains securely stored at each hospital. Only model
            updates are exchanged through the federated learning system. Raw
            patient data is never shared with the central server.
          </p>
        </div>
      </div>
    </div>
  );
}

export default MRIAnalysis;
