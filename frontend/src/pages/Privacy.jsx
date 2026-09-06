function Privacy() {
  const securityFeatures = [
    {
      icon: "🔐",
      title: "Federated Learning",
      status: "Active",
      description:
        "Hospitals train the AI model locally. Raw patient data never leaves the hospital.",
    },
    {
      icon: "🛡️",
      title: "Homomorphic Encryption",
      status: "Active",
      description:
        "Model updates are protected using encrypted computation during aggregation.",
    },
    {
      icon: "🔒",
      title: "TLS Communication",
      status: "Active",
      description:
        "Secure encrypted communication is used between hospital nodes and the coordinator.",
    },
    {
      icon: "👤",
      title: "Patient Data Protection",
      status: "Protected",
      description:
        "Patient records and MRI scans remain inside their respective hospital environments.",
    },
  ];

  return (
    <div className="page">

      {/* PAGE HEADER */}

      <div className="page-header">

        <div>
          <h1>Privacy & Security</h1>
          <p>
            Monitor privacy-preserving mechanisms protecting federated healthcare AI
          </p>
        </div>

        <div className="security-status">
          <span className="security-dot"></span>
          System Secure
        </div>

      </div>


      {/* SECURITY OVERVIEW */}

      <div className="training-stats">

        <div className="training-card">
          <span>Privacy Status</span>
          <strong>Protected</strong>
          <p>Patient data secured</p>
        </div>

        <div className="training-card">
          <span>Encryption</span>
          <strong>Active</strong>
          <p>Model updates encrypted</p>
        </div>

        <div className="training-card">
          <span>Secure Nodes</span>
          <strong>3 / 3</strong>
          <p>All connections protected</p>
        </div>

        <div className="training-card">
          <span>Data Shared</span>
          <strong>0 GB</strong>
          <p>No raw patient data</p>
        </div>

      </div>


      {/* SECURITY FEATURES */}

      <div className="panel">

        <div className="panel-header">

          <div>
            <h3>Privacy Protection Layers</h3>
            <p>
              Security mechanisms used by the FedMed platform
            </p>
          </div>

          <span className="badge">
            Protected
          </span>

        </div>


        <div className="security-grid">

          {securityFeatures.map((feature) => (
            <div
              className="security-card"
              key={feature.title}
            >

              <div className="security-card-top">

                <div className="security-icon">
                  {feature.icon}
                </div>

                <span className="security-active">
                  ● {feature.status}
                </span>

              </div>

              <h3>
                {feature.title}
              </h3>

              <p>
                {feature.description}
              </p>

            </div>
          ))}

        </div>

      </div>


      {/* DATA FLOW */}

      <div className="panel">

        <div className="panel-header">

          <div>
            <h3>Secure Federated Data Flow</h3>
            <p>
              How patient data remains protected during training
            </p>
          </div>

        </div>


        <div className="security-flow">

          <div className="flow-item">

            <div className="flow-icon">
              🏥
            </div>

            <strong>
              Hospital
            </strong>

            <span>
              Private MRI Data
            </span>

          </div>


          <div className="flow-arrow">
            →
          </div>


          <div className="flow-item">

            <div className="flow-icon">
              🤖
            </div>

            <strong>
              Local Training
            </strong>

            <span>
              Model learns locally
            </span>

          </div>


          <div className="flow-arrow">
            →
          </div>


          <div className="flow-item">

            <div className="flow-icon">
              🔐
            </div>

            <strong>
              Encrypted Update
            </strong>

            <span>
              Only model updates
            </span>

          </div>


          <div className="flow-arrow">
            →
          </div>


          <div className="flow-item">

            <div className="flow-icon">
              🌐
            </div>

            <strong>
              Global Model
            </strong>

            <span>
              Secure aggregation
            </span>

          </div>

        </div>

      </div>


      {/* PRIVACY NOTICE */}

      <div className="privacy-notice">

        <div className="privacy-icon">
          🔐
        </div>

        <div>

          <h3>
            Zero Raw Data Sharing
          </h3>

          <p>
            FedMed follows a privacy-preserving federated learning
            architecture. MRI scans and patient records remain
            inside each participating hospital. The central
            coordinator receives only protected model updates,
            helping reduce the risk of exposing sensitive
            healthcare information.
          </p>

        </div>

      </div>


      {/* SECURITY LOG */}

      <div className="panel">

        <div className="panel-header">

          <div>
            <h3>Security Activity</h3>
            <p>
              Recent privacy and security events
            </p>
          </div>

        </div>


        <div className="security-log">

          <div className="log-item">

            <span className="log-status">
              ✓
            </span>

            <div>
              <strong>
                Hospital 1 secure connection established
              </strong>

              <p>
                TLS connection verified
              </p>
            </div>

            <span className="log-time">
              2 min ago
            </span>

          </div>


          <div className="log-item">

            <span className="log-status">
              ✓
            </span>

            <div>
              <strong>
                Model update encrypted successfully
              </strong>

              <p>
                Homomorphic encryption applied
              </p>
            </div>

            <span className="log-time">
              4 min ago
            </span>

          </div>


          <div className="log-item">

            <span className="log-status">
              ✓
            </span>

            <div>
              <strong>
                Federated aggregation completed
              </strong>

              <p>
                No raw patient data transferred
              </p>
            </div>

            <span className="log-time">
              6 min ago
            </span>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Privacy;