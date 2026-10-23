import { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import { api } from "../lib/api";

/**
 * Platform settings.
 *
 * The form mirrors the backend's effective configuration and persists
 * overrides that apply to the next federated run.
 */
function Settings({ fed }) {
  const { status, nodes, connection } = fed;

  const [config, setConfig] = useState(null);
  const [notifications, setNotifications] = useState(true);
  const [autoTraining, setAutoTraining] = useState(false);
  const [form, setForm] = useState({
    num_rounds: 10,
    local_epochs: 2,
    batch_size: 8,
    learning_rate: 0.001,
    dp_noise_multiplier: 1.1,
    dp_clip_norm: 1.0,
    dp_delta: 0.00001,
  });
  const [notice, setNotice] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const data = await api.settings();
        if (cancelled) return;
        setConfig(data);
        setForm((prev) => ({
          ...prev,
          num_rounds: data.federated.num_rounds,
          local_epochs: data.federated.local_epochs,
          batch_size: data.federated.batch_size,
          learning_rate: data.federated.learning_rate,
          dp_noise_multiplier: data.privacy.noise_multiplier,
          dp_clip_norm: data.privacy.clip_norm,
          dp_delta: data.privacy.delta,
        }));
      } catch (err) {
        if (!cancelled) setNotice(err.message);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleChange = (field) => (event) => {
    const raw = event.target.value;
    const value = event.target.type === "number" ? Number(raw) : raw;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setNotice(null);
    try {
      await fed.actions.updateSettings(form);
      setNotice("Configuration saved — it applies to the next run.");
    } catch (err) {
      setNotice(err.message);
    } finally {
      setSaving(false);
    }
  };

  const model = config?.model;
  const privacy = config?.privacy;
  const transport = config?.transport;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Manage FedMed platform preferences</p>
        </div>

        <div className="settings-status">
          <span className="settings-dot" />
          Configuration Active
        </div>
      </div>

      <div className="training-stats">
        <StatCard
          label="System Status"
          value={connection === "online" ? "Online" : "Offline"}
          caption={
            status?.is_running ? "Federated run in progress" : "All services idle"
          }
          tone={connection === "online" ? "success" : "danger"}
        />
        <StatCard
          label="Model"
          value={model?.architecture?.split(" ").pop() ?? "3D U-Net"}
          caption={`${(model?.parameters ?? 0).toLocaleString()} parameters`}
          tone="info"
        />
        <StatCard
          label="Connected Nodes"
          value={`${nodes.filter((n) => n.status === "online").length} / ${
            nodes.length || 3
          }`}
          caption="Hospital clients"
        />
        <StatCard
          label="Security"
          value="Protected"
          caption={
            privacy?.enabled ? `${privacy.scheme} · ${privacy.mechanism}` : "Disabled"
          }
          tone="success"
        />
      </div>

      <div className="panel settings-panel">
        <div className="panel-header">
          <div>
            <h3>General Settings</h3>
            <p>Configure the federated learning environment</p>
          </div>
        </div>

        <div className="settings-list">
          {[
            {
              icon: "🔔",
              title: "Notifications",
              note: "Receive alerts about training and hospital nodes",
              value: notifications,
              onChange: () => setNotifications(!notifications),
            },
            {
              icon: "🤖",
              title: "Automatic Training",
              note: "Automatically start the next federated round",
              value: autoTraining,
              onChange: () => setAutoTraining(!autoTraining),
            },
          ].map((item) => (
            <div className="setting-item" key={item.title}>
              <div className="setting-left">
                <div className="setting-icon">{item.icon}</div>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.note}</p>
                </div>
              </div>
              <button
                type="button"
                className={`toggle ${item.value ? "toggle-on" : ""}`}
                onClick={item.onChange}
                aria-pressed={item.value}
              >
                <span />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Training Configuration</h3>
            <p>Configure global federated learning parameters</p>
          </div>
        </div>

        <div className="settings-form">
          <div className="form-group">
            <label htmlFor="set-rounds">Federated Rounds</label>
            <input
              id="set-rounds"
              type="number"
              min="1"
              max="100"
              value={form.num_rounds}
              onChange={handleChange("num_rounds")}
            />
            <small>Number of global training rounds</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-epochs">Local Epochs</label>
            <input
              id="set-epochs"
              type="number"
              min="1"
              max="50"
              value={form.local_epochs}
              onChange={handleChange("local_epochs")}
            />
            <small>Local training epochs per hospital</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-batch">Batch Size</label>
            <input
              id="set-batch"
              type="number"
              min="1"
              max="64"
              value={form.batch_size}
              onChange={handleChange("batch_size")}
            />
            <small>Patients sampled per DP-SGD step</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-lr">Learning Rate</label>
            <input
              id="set-lr"
              type="number"
              step="0.0001"
              value={form.learning_rate}
              onChange={handleChange("learning_rate")}
            />
            <small>Local optimizer learning rate</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-sigma">DP Noise Multiplier (σ)</label>
            <input
              id="set-sigma"
              type="number"
              step="0.1"
              value={form.dp_noise_multiplier}
              onChange={handleChange("dp_noise_multiplier")}
            />
            <small>Noise std = σ × clip norm</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-clip">DP Clip Norm (C)</label>
            <input
              id="set-clip"
              type="number"
              step="0.1"
              value={form.dp_clip_norm}
              onChange={handleChange("dp_clip_norm")}
            />
            <small>Per-patient gradient L2 bound</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-delta">DP Delta (δ)</label>
            <input
              id="set-delta"
              type="number"
              step="0.000001"
              value={form.dp_delta}
              onChange={handleChange("dp_delta")}
            />
            <small>Target failure probability</small>
          </div>

          <div className="form-group">
            <label htmlFor="set-strategy">Aggregation Strategy</label>
            <select id="set-strategy" value="FedAvg" disabled>
              <option>FedAvg (homomorphic CKKS)</option>
            </select>
            <small>Updates are summed on ciphertext before decryption</small>
          </div>
        </div>

        <div className="settings-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={() => setNotice("Changes discarded")}
          >
            Cancel
          </button>
          <button
            type="button"
            className="save-button"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving…" : "Save Configuration"}
          </button>
        </div>

        {notice ? <p className="launch-notice">{notice}</p> : null}
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Security Configuration</h3>
            <p>Privacy and communication security settings</p>
          </div>
          <span className="badge">Secure</span>
        </div>

        <div className="security-settings">
          <div>
            <span>Communication Protocol</span>
            <strong>{transport?.protocol ?? "gRPC + TLS"}</strong>
          </div>
          <div>
            <span>Encryption Method</span>
            <strong>
              {privacy?.scheme ? `Homomorphic (${privacy.scheme})` : "Homomorphic Encryption"}
            </strong>
          </div>
          <div>
            <span>Privacy Mechanism</span>
            <strong>{privacy?.mechanism ?? "Differential Privacy"}</strong>
          </div>
          <div>
            <span>Polynomial Modulus</span>
            <strong>{privacy?.poly_modulus ?? "—"} bits</strong>
          </div>
          <div>
            <span>Projected ε</span>
            <strong>
              {privacy?.projected_epsilon !== undefined
                ? Number(privacy.projected_epsilon).toFixed(3)
                : "—"}
            </strong>
          </div>
          <div>
            <span>Authentication</span>
            <strong>Mutual TLS</strong>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Model Architecture</h3>
            <p>The 3D U-Net shared by every hospital node</p>
          </div>
        </div>

        <div className="security-settings">
          <div>
            <span>Architecture</span>
            <strong>{model?.architecture ?? "3D U-Net"}</strong>
          </div>
          <div>
            <span>Channels</span>
            <strong>{model?.channels?.join(" → ") ?? "—"}</strong>
          </div>
          <div>
            <span>Residual Blocks</span>
            <strong>{model?.num_res_units ?? "—"}</strong>
          </div>
          <div>
            <span>Patch Size</span>
            <strong>{model?.patch_size?.join("³") ?? "—"}</strong>
          </div>
          <div>
            <span>Classes</span>
            <strong>{model?.num_classes ?? "—"}</strong>
          </div>
          <div>
            <span>Parameters</span>
            <strong>{(model?.parameters ?? 0).toLocaleString()}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
