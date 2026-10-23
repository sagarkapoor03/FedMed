/**
 * A single headline metric with an optional delta / caption.
 */
function StatCard({ label, value, caption, tone = "default", icon }) {
  return (
    <div className={`card stat-card stat-card-${tone}`}>
      <div className="stat-card-top">
        <p>{label}</p>
        {icon ? <span className="stat-card-icon">{icon}</span> : null}
      </div>
      <h2>{value}</h2>
      {caption ? <small>{caption}</small> : null}
    </div>
  );
}

export default StatCard;
