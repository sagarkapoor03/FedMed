function Hospitals() {
  const hospitals = [
    {
      name: "Hospital 1",
      node: "HOSP-001",
      status: "Online",
      training: "Training locally",
      dataset: "120 MRI scans",
      lastSync: "2 min ago",
    },
    {
      name: "Hospital 2",
      node: "HOSP-002",
      status: "Online",
      training: "Training locally",
      dataset: "95 MRI scans",
      lastSync: "3 min ago",
    },
    {
      name: "Hospital 3",
      node: "HOSP-003",
      status: "Offline",
      training: "Training paused",
      dataset: "110 MRI scans",
      lastSync: "18 min ago",
    },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Hospital Nodes</h1>
          <p>Manage and monitor federated hospital clients</p>
        </div>

        <div className="node-summary">
          <span className="summary-dot"></span>
          2 / 3 Nodes Online
        </div>
      </div>

      <div className="hospital-grid">
        {hospitals.map((hospital) => (
          <div className="hospital-card" key={hospital.node}>

            <div className="hospital-card-header">
              <div className="large-hospital-icon">🏥</div>

              <span
                className={
                  hospital.status === "Online"
                    ? "status online-status"
                    : "status offline-status"
                }
              >
                ● {hospital.status}
              </span>
            </div>

            <h2>{hospital.name}</h2>

            <p className="node-id">{hospital.node}</p>

            <div className="hospital-info">
              <div>
                <span>Training Status</span>
                <strong>{hospital.training}</strong>
              </div>

              <div>
                <span>Local Dataset</span>
                <strong>{hospital.dataset}</strong>
              </div>

              <div>
                <span>Last Sync</span>
                <strong>{hospital.lastSync}</strong>
              </div>
            </div>

            <div className="privacy-status">
              🔐 <span>Private data protected</span>
            </div>

            <button className="view-node">
              View Node
            </button>

          </div>
        ))}
      </div>
    </div>
  );
}

export default Hospitals;