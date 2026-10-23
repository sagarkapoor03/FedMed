/**
 * Live status card for one hospital node.
 *
 * Everything shown here comes from the aggregator's runtime state, which
 * the hospital node updates while it trains.
 */

const STATUS_TONE = {
  online: "online",
  training: "training",
  aggregating: "training",
  connecting: "pending",
  offline: "offline",
  failed: "offline",
};

const STATUS_LABEL = {
  online: "Online",
  training: "Training",
  aggregating: "Encrypting",
  connecting: "Connecting",
  offline: "Offline",
  failed: "Failed",
};

function formatAgo(timestamp) {
  if (!timestamp) return "Never";
  const seconds = Math.max(0, Math.floor(Date.now() / 1000 - timestamp));
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.floor(minutes / 60)}h ago`;
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value >= 10 || unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function NodeCard({ node, progress = 0 }) {
  const tone = STATUS_TONE[node.status] ?? "pending";
  const label = STATUS_LABEL[node.status] ?? node.status;

  return (
    <div className="hospital-card node-card">
      <div className="hospital-card-header">
        <div className="large-hospital-icon">🏥</div>
        <span className={`status status-${tone}`}>
          ● {label}
        </span>
      </div>

      <h2>{node.hospital_id?.replace("hospital-", "Hospital ")}</h2>
      <p className="node-id">{node.node_id}</p>

      <div className="hospital-info">
        <div>
          <span>Training Status</span>
          <strong>{node.message ?? "Idle"}</strong>
        </div>
        <div>
          <span>Local Dataset</span>
          <strong>{node.samples ?? 0} MRI scans</strong>
        </div>
        <div>
          <span>Last Sync</span>
          <strong>{formatAgo(node.last_sync)}</strong>
        </div>
        <div>
          <span>Rounds Joined</span>
          <strong>{node.rounds_participated ?? 0}</strong>
        </div>
        <div>
          <span>Local Dice</span>
          <strong>
            {node.local_dice !== null && node.local_dice !== undefined
              ? `${Number(node.local_dice).toFixed(2)}%`
              : "—"}
          </strong>
        </div>
        <div>
          <span>Encrypted Upload</span>
          <strong>{formatBytes(node.payload_bytes)}</strong>
        </div>
      </div>

      <div className="node-progress">
        <div className="node-progress-label">
          <span>Round participation</span>
          <strong>{Math.round(progress)}%</strong>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <div className="privacy-status">
        🔐 <span>Private data protected</span>
      </div>
    </div>
  );
}

export default NodeCard;
