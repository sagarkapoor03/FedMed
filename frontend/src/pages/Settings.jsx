import { useState } from "react";

function Settings() {
  const [notifications, setNotifications] = useState(true);
  const [autoTraining, setAutoTraining] = useState(true);
  const [encryption, setEncryption] = useState(true);

  return (
    <div className="page">

      {/* PAGE HEADER */}

      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Manage FedMed platform preferences</p>
        </div>

        <div className="settings-status">
          <span className="settings-dot"></span>
          Configuration Active
        </div>
      </div>


      {/* SYSTEM OVERVIEW */}

      <div className="training-stats">

        <div className="training-card">
          <span>System Status</span>
          <strong>Online</strong>
          <p>All services operational</p>
        </div>

        <div className="training-card">
          <span>Model Version</span>
          <strong>v1.0</strong>
          <p>FedMed Global Model</p>
        </div>

        <div className="training-card">
          <span>Connected Nodes</span>
          <strong>3 / 3</strong>
          <p>Hospital clients</p>
        </div>

        <div className="training-card">
          <span>Security</span>
          <strong>Protected</strong>
          <p>Encryption enabled</p>
        </div>

      </div>


      {/* GENERAL SETTINGS */}

      <div className="panel settings-panel">

        <div className="panel-header">
          <div>
            <h3>General Settings</h3>
            <p>Configure the federated learning environment</p>
          </div>
        </div>


        <div className="settings-list">

          <div className="setting-item">

            <div className="setting-left">

              <div className="setting-icon">
                🔔
              </div>

              <div>
                <strong>Notifications</strong>
                <p>
                  Receive alerts about training and hospital nodes
                </p>
              </div>

            </div>

            <button
              className={`toggle ${
                notifications ? "toggle-on" : ""
              }`}
              onClick={() =>
                setNotifications(!notifications)
              }
            >
              <span></span>
            </button>

          </div>


          <div className="setting-item">

            <div className="setting-left">

              <div className="setting-icon">
                🤖
              </div>

              <div>
                <strong>Automatic Training</strong>
                <p>
                  Automatically start the next federated round
                </p>
              </div>

            </div>

            <button
              className={`toggle ${
                autoTraining ? "toggle-on" : ""
              }`}
              onClick={() =>
                setAutoTraining(!autoTraining)
              }
            >
              <span></span>
            </button>

          </div>


          <div className="setting-item">

            <div className="setting-left">

              <div className="setting-icon">
                🔐
              </div>

              <div>
                <strong>Model Encryption</strong>
                <p>
                  Encrypt model updates before aggregation
                </p>
              </div>

            </div>

            <button
              className={`toggle ${
                encryption ? "toggle-on" : ""
              }`}
              onClick={() =>
                setEncryption(!encryption)
              }
            >
              <span></span>
            </button>

          </div>

        </div>

      </div>


      {/* TRAINING CONFIGURATION */}

      <div className="panel">

        <div className="panel-header">
          <div>
            <h3>Training Configuration</h3>
            <p>Configure global federated learning parameters</p>
          </div>
        </div>


        <div className="settings-form">

          <div className="form-group">
            <label>Federated Rounds</label>

            <input
              type="number"
              defaultValue="20"
              min="1"
            />

            <small>
              Number of global training rounds
            </small>
          </div>


          <div className="form-group">
            <label>Local Epochs</label>

            <input
              type="number"
              defaultValue="10"
              min="1"
            />

            <small>
              Local training epochs per hospital
            </small>
          </div>


          <div className="form-group">
            <label>Aggregation Strategy</label>

            <select defaultValue="FedAvg">
              <option>FedAvg</option>
              <option>FedProx</option>
              <option>FedAdam</option>
            </select>

            <small>
              Algorithm used to aggregate model updates
            </small>
          </div>


          <div className="form-group">
            <label>Learning Rate</label>

            <input
              type="number"
              defaultValue="0.001"
              step="0.0001"
            />

            <small>
              Global model learning rate
            </small>
          </div>

        </div>


        <div className="settings-actions">

          <button className="cancel-button">
            Cancel
          </button>

          <button className="save-button">
            Save Configuration
          </button>

        </div>

      </div>


      {/* SECURITY CONFIGURATION */}

      <div className="panel">

        <div className="panel-header">
          <div>
            <h3>Security Configuration</h3>
            <p>
              Privacy and communication security settings
            </p>
          </div>

          <span className="badge">
            Secure
          </span>
        </div>


        <div className="security-settings">

          <div>
            <span>Communication Protocol</span>
            <strong>gRPC + TLS</strong>
          </div>

          <div>
            <span>Encryption Method</span>
            <strong>Homomorphic Encryption</strong>
          </div>

          <div>
            <span>Privacy Mechanism</span>
            <strong>Differential Privacy</strong>
          </div>

          <div>
            <span>Authentication</span>
            <strong>Secure Node Authentication</strong>
          </div>

        </div>

      </div>


      {/* SYSTEM INFORMATION */}

      <div className="privacy-notice">

        <div className="privacy-icon">
          ⚙️
        </div>

        <div>

          <h3>FedMed System Configuration</h3>

          <p>
            These settings control the frontend representation
            of the FedMed federated healthcare AI platform.
            Backend training, encryption and hospital
            communication services will be connected in the
            next development phase.
          </p>

        </div>

      </div>

    </div>
  );
}

export default Settings;