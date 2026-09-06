function Training() {
  const trainingRounds = [
    {
      round: 1,
      loss: "0.85",
      dice: "62%",
      status: "Completed",
    },
    {
      round: 2,
      loss: "0.72",
      dice: "68%",
      status: "Completed",
    },
    {
      round: 3,
      loss: "0.61",
      dice: "73%",
      status: "Completed",
    },
    {
      round: 4,
      loss: "0.52",
      dice: "77%",
      status: "Completed",
    },
    {
      round: 5,
      loss: "0.45",
      dice: "80%",
      status: "Completed",
    },
    {
      round: 6,
      loss: "0.39",
      dice: "82%",
      status: "Completed",
    },
    {
      round: 7,
      loss: "0.34",
      dice: "84%",
      status: "Completed",
    },
    {
      round: 8,
      loss: "0.29",
      dice: "86%",
      status: "Completed",
    },
    {
      round: 9,
      loss: "0.25",
      dice: "88%",
      status: "Completed",
    },
    {
      round: 10,
      loss: "0.21",
      dice: "89.4%",
      status: "Running",
    },
  ];

  return (
    <div className="page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Training</h1>
          <p>Monitor federated model training progress</p>
        </div>

        <div className="training-status">
          <span className="training-dot"></span>
          Training Active
        </div>
      </div>

      {/* Training Summary */}
      <div className="training-stats">

        <div className="training-card">
          <span>Current Round</span>
          <strong>10 / 20</strong>
          <p>50% completed</p>
        </div>

        <div className="training-card">
          <span>Global Dice Score</span>
          <strong>89.4%</strong>
          <p>↑ Improving</p>
        </div>

        <div className="training-card">
          <span>Current Loss</span>
          <strong>0.21</strong>
          <p>↓ Decreasing</p>
        </div>

        <div className="training-card">
          <span>Participants</span>
          <strong>3 / 3</strong>
          <p>All hospitals active</p>
        </div>

      </div>

      {/* Current Training */}
      <div className="panel training-progress-panel">

        <div className="panel-header">
          <div>
            <h3>Federated Training Progress</h3>
            <p>Current global model training status</p>
          </div>

          <span className="badge">Round 10</span>
        </div>

        <div className="progress-container">

          <div className="progress-info">
            <span>Overall Progress</span>
            <strong>50%</strong>
          </div>

          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>

        </div>

        <div className="training-process">

          <div className="process-step completed">
            <div className="process-icon">✓</div>
            <strong>Model Broadcast</strong>
            <span>Global model sent</span>
          </div>

          <div className="process-line"></div>

          <div className="process-step completed">
            <div className="process-icon">✓</div>
            <strong>Local Training</strong>
            <span>Hospitals training</span>
          </div>

          <div className="process-line"></div>

          <div className="process-step active-step">
            <div className="process-icon">↻</div>
            <strong>Aggregation</strong>
            <span>FedAvg in progress</span>
          </div>

          <div className="process-line"></div>

          <div className="process-step">
            <div className="process-icon">4</div>
            <strong>Global Update</strong>
            <span>Waiting</span>
          </div>

        </div>

      </div>

      {/* Hospital Training Status */}
      <div className="panel">

        <div className="panel-header">
          <div>
            <h3>Hospital Training Status</h3>
            <p>Local training progress for each node</p>
          </div>
        </div>

        <div className="training-hospitals">

          <div className="training-hospital">
            <div className="training-hospital-left">
              <div className="hospital-icon">🏥</div>

              <div>
                <strong>Hospital 1</strong>
                <p>Local Epoch: 8 / 10</p>
              </div>
            </div>

            <div className="hospital-progress">
              <div className="mini-progress">
                <div className="mini-progress-fill"></div>
              </div>
              <span>80%</span>
            </div>

            <span className="online">●</span>
          </div>

          <div className="training-hospital">
            <div className="training-hospital-left">
              <div className="hospital-icon">🏥</div>

              <div>
                <strong>Hospital 2</strong>
                <p>Local Epoch: 7 / 10</p>
              </div>
            </div>

            <div className="hospital-progress">
              <div className="mini-progress">
                <div className="mini-progress-fill"></div>
              </div>
              <span>70%</span>
            </div>

            <span className="online">●</span>
          </div>

          <div className="training-hospital">
            <div className="training-hospital-left">
              <div className="hospital-icon">🏥</div>

              <div>
                <strong>Hospital 3</strong>
                <p>Local Epoch: 9 / 10</p>
              </div>
            </div>

            <div className="hospital-progress">
              <div className="mini-progress">
                <div className="mini-progress-fill"></div>
              </div>
              <span>90%</span>
            </div>

            <span className="online">●</span>
          </div>

        </div>

      </div>

      {/* Training History */}
      <div className="panel training-history">

        <div className="panel-header">
          <div>
            <h3>Training History</h3>
            <p>Federated learning round statistics</p>
          </div>
        </div>

        <div className="table-wrapper">

          <table>
            <thead>
              <tr>
                <th>Round</th>
                <th>Training Loss</th>
                <th>Dice Score</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {trainingRounds.map((item) => (
                <tr key={item.round}>
                  <td>
                    <strong>Round {item.round}</strong>
                  </td>

                  <td>{item.loss}</td>

                  <td>
                    <strong>{item.dice}</strong>
                  </td>

                  <td>
                    <span
                      className={
                        item.status === "Running"
                          ? "round-running"
                          : "round-completed"
                      }
                    >
                      ● {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

        </div>

      </div>
    </div>
  );
}

export default Training;