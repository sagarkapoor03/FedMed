/**
 * Shows the live WebSocket connection state to the aggregator.
 */
const LABELS = {
  online: "Live",
  connecting: "Connecting",
  offline: "Offline",
  error: "Connection Error",
};

function ConnectionBadge({ connection, running }) {
  const state = connection === "online" ? "online" : connection;
  const text = running ? "Training" : LABELS[state] ?? state;

  return (
    <div className={`server-status server-status-${state}`}>
      <span className="status-dot" />
      {text}
    </div>
  );
}

export default ConnectionBadge;
