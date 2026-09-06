function MRIAnalysis() {
  const scans = [
    {
      id: "MRI-001",
      hospital: "Hospital 1",
      patient: "Patient A",
      status: "Analyzed",
      accuracy: "92.6%",
      tumor: "Detected",
    },
    {
      id: "MRI-002",
      hospital: "Hospital 2",
      patient: "Patient B",
      status: "Analyzed",
      accuracy: "94.1%",
      tumor: "Detected",
    },
    {
      id: "MRI-003",
      hospital: "Hospital 3",
      patient: "Patient C",
      status: "Processing",
      accuracy: "--",
      tumor: "Processing",
    },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>MRI Analysis</h1>
          <p>AI-powered brain tumor segmentation analysis</p>
        </div>

        <div className="training-status">
          <span className="training-dot"></span>
          Model Ready
        </div>
      </div>

      {/* Analysis Overview */}

      <div className="training-stats">
        <div className="training-card">
          <span>Total MRI Scans</span>
          <strong>325</strong>
          <p>Across all hospitals</p>
        </div>

        <div className="training-card">
          <span>Scans Analyzed</span>
          <strong>284</strong>
          <p>87.4% completed</p>
        </div>

        <div className="training-card">
          <span>Tumors Detected</span>
          <strong>76</strong>
          <p>AI predictions</p>
        </div>

        <div className="training-card">
          <span>Model Accuracy</span>
          <strong>92.6%</strong>
          <p>Current global model</p>
        </div>
      </div>

      {/* MRI Visualization */}

      <div className="panel mri-analysis-panel">
        <div className="panel-header">
          <div>
            <h3>Latest MRI Analysis</h3>
            <p>Brain tumor segmentation using global federated model</p>
          </div>

          <span className="badge">AI Analysis</span>
        </div>

        <div className="analysis-view">

          <div className="scan-container">
            <div className="scan-image">
              <div className="brain-placeholder">
                🧠
              </div>
            </div>

            <div className="scan-label">
              <strong>Original MRI Scan</strong>
              <span>MRI-001 • Hospital 1</span>
            </div>
          </div>

          <div className="analysis-arrow">
            →
          </div>

          <div className="scan-container">
            <div className="scan-image segmentation-image">
              <div className="segmentation-placeholder">
                🎯
              </div>
            </div>

            <div className="scan-label">
              <strong>Predicted Tumor Mask</strong>
              <span>AI Segmentation Output</span>
            </div>
          </div>

        </div>

        {/* Result */}

        <div className="analysis-result">

          <div className="result-item">
            <span>Segmentation Accuracy</span>
            <strong>92.6%</strong>
          </div>

          <div className="result-item">
            <span>Dice Score</span>
            <strong>89.4%</strong>
          </div>

          <div className="result-item">
            <span>Tumor Status</span>
            <strong className="tumor-detected">
              ● Detected
            </strong>
          </div>

          <div className="result-item">
            <span>Model Version</span>
            <strong>FedMed-v1.0</strong>
          </div>

        </div>
      </div>

      {/* Recent Scans */}

      <div className="panel recent-scans">

        <div className="panel-header">
          <div>
            <h3>Recent MRI Scans</h3>
            <p>Latest analysis results from federated hospitals</p>
          </div>
        </div>

        <div className="table-wrapper">

          <table>

            <thead>
              <tr>
                <th>Scan ID</th>
                <th>Hospital</th>
                <th>Patient</th>
                <th>Status</th>
                <th>Accuracy</th>
                <th>Tumor</th>
              </tr>
            </thead>

            <tbody>

              {scans.map((scan) => (
                <tr key={scan.id}>

                  <td>
                    <strong>{scan.id}</strong>
                  </td>

                  <td>{scan.hospital}</td>

                  <td>{scan.patient}</td>

                  <td>
                    <span
                      className={
                        scan.status === "Analyzed"
                          ? "round-completed"
                          : "round-running"
                      }
                    >
                      ● {scan.status}
                    </span>
                  </td>

                  <td>
                    <strong>{scan.accuracy}</strong>
                  </td>

                  <td>
                    {scan.tumor === "Detected" ? (
                      <span className="tumor-detected">
                        ● Detected
                      </span>
                    ) : (
                      <span className="processing-text">
                        ● Processing
                      </span>
                    )}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>

      </div>

      {/* Privacy Notice */}

      <div className="privacy-notice">
        <div className="privacy-icon">🔐</div>

        <div>
          <h3>Privacy-Preserving Analysis</h3>

          <p>
            MRI data remains securely stored at each hospital.
            Only model updates are exchanged through the
            federated learning system. Raw patient data is
            never shared with the central server.
          </p>
        </div>
      </div>

    </div>
  );
}

export default MRIAnalysis;