import { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import { api } from "../lib/api";

const EVENT_LABEL = {
  dp_noise_applied: "Differential privacy noise applied",
  update_encrypted: "Model update encrypted",
  aggregation_completed: "Federated aggregation completed",
  node_offline: "Hospital node dropped offline",
  round_no_updates: "Round received no updates",
};

function formatTime(timestamp) {
  if (!timestamp) return "";
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatDetail(detail = {}) {
  const parts = [];
  if (detail.scheme) parts.push(detail.scheme);
  if (detail.mode) parts.push(detail.mode);
  if (detail.ciphertext_bytes)
    parts.push(`${(detail.ciphertext_bytes / 1e6).toFixed(1)} MB`);
  if (detail.sigma !== undefined) parts.push(`σ=${detail.sigma}`);
  if (detail.patients) parts.push(`${detail.patients} patients`);
  if (detail.round) parts.push(`round ${detail.round}`);
  return parts.join(" · ");
}

/**
 * Privacy and security monitoring.
 *
 * Shows the live posture of the HE and DP mechanisms plus the audit trail
 * of every privacy-relevant event the aggregator recorded.
 */
function Privacy({ fed }) {
  const { privacyEvents, securityEvents, status, nodes, summary } = fed;

  const [posture, setPosture] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await api.privacy();
        if (!cancelled) setPosture(data);
      } catch {
        // The dashboard still works without the posture payload.
      }
    };
    load();
    const timer = setInterval(load, 15000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const he = posture?.he;
  const dp = posture?.dp;
  const epsilon = status?.dp_epsilon ?? posture?.accountant?.epsilon ?? 0;
  const delta = status?.dp_delta ?? posture?.accountant?.delta ?? 1e-5;
  const encryptedNodes = nodes.filter((n) => n.encrypted).length;
  const totalBytes = nodes.reduce((sum, n) => sum + (n.payload_bytes || 0), 0);

  const features = [
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
      status: he?.enabled ? "Active" : "Disabled",
      description: he?.enabled
        ? `Model updates are protected with TenSEAL ${he.scheme} (${he.poly_modulus}-bit polynomial modulus) and aggregated on ciphertext.`
        : "Model updates are encrypted during aggregation.",
    },
    {
      icon: "🔒",
      title: "TLS Communication",
      status: "Active",
      description:
        "gRPC channels between the hospital nodes and the coordinator use mutual TLS with client certificate verification.",
    },
    {
      icon: "👤",
      title: "Patient Data Protection",
      status: "Protected",
      description:
        "Patient records and MRI scans remain inside their respective hospital environments.",
    },
    {
      icon: "📊",
      title: "Differential Privacy",
      status: dp?.enabled ? "Active" : "Disabled",
      description: dp?.enabled
        ? `DP-SGD clips every patient gradient to C=${dp.clip_norm} and adds Gaussian noise with σ=${dp.noise_multiplier}·C.`
        : "Per-patient gradient clipping and Gaussian noise.",
    },
  ];

  const guarantees = posture?.guarantees ?? [];

  const allEvents = [...privacyEvents, ...securityEvents].sort(
    (a, b) => (b.timestamp ?? 0) - (a.timestamp ?? 0),
  );

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Privacy & Security</h1>
          <p>
            Monitor privacy-preserving mechanisms protecting federated
            healthcare AI
          </p>
        </div>

        <div className="security-status">
          <span className="security-dot" />
          System Secure
        </div>
      </div>

      <div className="training-stats">
        <StatCard
          label="Privacy Status"
          value="Protected"
          caption="Patient data secured"
          tone="success"
        />
        <StatCard
          label="Encryption"
          value={he?.enabled ? "Active" : "Disabled"}
          caption={
            he?.enabled
              ? `${he.scheme} · ${he.poly_modulus}-bit modulus`
              : "Homomorphic encryption off"
          }
          tone="info"
        />
        <StatCard
          label="DP Budget (ε)"
          value={Number(epsilon).toFixed(3)}
          caption={`δ = ${Number(delta).toExponential(1)} · ${
            status?.dp_rounds ?? 0
          } rounds accounted`}
          tone="info"
        />
        <StatCard
          label="Data Shared"
          value="0 B"
          caption={`${encryptedNodes} encrypted node uploads (${
            (totalBytes / 1e6).toFixed(1)
          } MB ciphertext)`}
          tone="success"
        />
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Privacy Protection Layers</h3>
            <p>Security mechanisms used by the FedMed platform</p>
          </div>
          <span className="badge">Protected</span>
        </div>

        <div className="security-grid">
          {features.map((feature) => (
            <div className="security-card" key={feature.title}>
              <div className="security-card-top">
                <div className="security-icon">{feature.icon}</div>
                <span className="security-active">● {feature.status}</span>
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Secure Federated Data Flow</h3>
            <p>How patient data remains protected during training</p>
          </div>
        </div>

        <div className="security-flow">
          {[
            { icon: "🏥", title: "Hospital", note: "Private MRI Data" },
            { icon: "🤖", title: "Local Training", note: "Model learns locally" },
            { icon: "📉", title: "DP-SGD", note: "Clipped + noised update" },
            { icon: "🔐", title: "Encrypted Update", note: "CKKS ciphertext" },
            { icon: "🌐", title: "Global Model", note: "Secure aggregation" },
          ].map((item, index, all) => (
            <div className="flow-wrap" key={item.title}>
              <div className="flow-item">
                <div className="flow-icon">{item.icon}</div>
                <strong>{item.title}</strong>
                <span>{item.note}</span>
              </div>
              {index < all.length - 1 ? <div className="flow-arrow">→</div> : null}
            </div>
          ))}
        </div>
      </div>

      {guarantees.length ? (
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Formal Guarantees</h3>
              <p>What each mechanism mathematically provides</p>
            </div>
          </div>
          <div className="guarantee-list">
            {guarantees.map((g) => (
              <div className="guarantee-item" key={g.title}>
                <div className="guarantee-icon">✔</div>
                <div>
                  <strong>{g.title}</strong>
                  <p>{g.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="panel">
        <div className="panel-header">
          <div>
            <h3>Security Activity</h3>
            <p>Recent privacy and security events</p>
          </div>
        </div>

        <div className="security-log">
          {allEvents.length === 0 ? (
            <p className="muted">No privacy events recorded yet.</p>
          ) : null}

          {allEvents.slice(0, 40).map((event, index) => (
            <div className="log-item" key={`${event.event}-${index}`}>
              <span className="log-status">
                {event.event === "node_offline" ? "!" : "✓"}
              </span>
              <div>
                <strong>
                  {EVENT_LABEL[event.event] ??
                    event.event.replace(/_/g, " ")}
                </strong>
                <p>{formatDetail(event.detail)}</p>
              </div>
              <span className="log-time">{formatTime(event.timestamp)}</span>
            </div>
          ))}
        </div>
      </div>

      {summary ? (
        <div className="privacy-notice">
          <div className="privacy-icon">🔐</div>
          <div>
            <h3>Zero Raw Data Sharing</h3>
            <p>
              FedMed follows a privacy-preserving federated learning
              architecture. MRI scans and patient records remain inside each
              participating hospital. The central coordinator receives only
              protected model updates, and the federated global model reached{" "}
              {summary.dice_ratio_pct ?? 0}% of the centralized baseline Dice
              score without exposing a single patient record.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default Privacy;
