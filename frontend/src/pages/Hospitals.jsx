import NodeCard from "../components/NodeCard";

/**
 * Hospital node monitoring.
 *
 * Each card is driven by the aggregator's live view of the node: status,
 * sample count, last sync, local accuracy and the size of the encrypted
 * payload the node uploaded.
 */
function Hospitals({ fed }) {
  const { nodes, rounds, totalNodes, onlineNodes } = fed;
  const totalRounds = rounds.length || 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Hospital Nodes</h1>
          <p>Manage and monitor federated hospital clients</p>
        </div>

        <div className="node-summary">
          <span className="summary-dot" />
          {onlineNodes} / {totalNodes} Nodes Online
        </div>
      </div>

      <div className="hospital-grid">
        {nodes.length === 0 ? (
          <p className="muted">Waiting for the aggregator to report node status…</p>
        ) : null}

        {nodes.map((node) => (
          <NodeCard
            key={node.hospital_id}
            node={node}
            progress={Math.min(
              100,
              ((node.rounds_participated ?? 0) / totalRounds) * 100,
            )}
          />
        ))}
      </div>
    </div>
  );
}

export default Hospitals;
