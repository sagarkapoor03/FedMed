import { useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import "./App.css";

import Hospitals from "./pages/Hospitals";
import Training from "./pages/Training";
import MRIAnalysis from "./pages/MRIAnalysis";
import Privacy from "./pages/Privacy";
import Settings from "./pages/Settings";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  const trainingData = [
    { round: 1, loss: 0.85, dice: 62 },
    { round: 2, loss: 0.72, dice: 68 },
    { round: 3, loss: 0.61, dice: 73 },
    { round: 4, loss: 0.52, dice: 77 },
    { round: 5, loss: 0.45, dice: 80 },
    { round: 6, loss: 0.39, dice: 82 },
    { round: 7, loss: 0.34, dice: 84 },
    { round: 8, loss: 0.29, dice: 86 },
    { round: 9, loss: 0.25, dice: 88 },
    { round: 10, loss: 0.21, dice: 89.4 },
  ];

  const navigation = (page) => {
    setCurrentPage(page);
  };

  const Sidebar = () => (
    <aside className="sidebar">

      <div className="logo">
        <span>🏥</span>
        <h2>FedMed</h2>
      </div>

      <nav>

        <a
          className={
            currentPage === "dashboard" ? "active" : ""
          }
          onClick={() => navigation("dashboard")}
        >
          Dashboard
        </a>

        <a
          className={
            currentPage === "hospitals" ? "active" : ""
          }
          onClick={() => navigation("hospitals")}
        >
          Hospitals
        </a>

        <a
          className={
            currentPage === "training" ? "active" : ""
          }
          onClick={() => navigation("training")}
        >
          Training
        </a>

        <a
          className={
            currentPage === "mri" ? "active" : ""
          }
          onClick={() => navigation("mri")}
        >
          MRI Analysis
        </a>

        <a
          className={
            currentPage === "privacy" ? "active" : ""
          }
          onClick={() => navigation("privacy")}
        >
          Privacy & Security
        </a>

      </nav>

      <div className="sidebar-bottom">

        <a
          className={
            currentPage === "settings" ? "active" : ""
          }
          onClick={() => navigation("settings")}
        >
          ⚙️ Settings
        </a>

      </div>

    </aside>
  );

  /* =========================
     HOSPITALS
  ========================= */

  if (currentPage === "hospitals") {
    return (
      <div className="app">
        <Sidebar />

        <main className="main-content">
          <Hospitals />
        </main>
      </div>
    );
  }

  /* =========================
     TRAINING
  ========================= */

  if (currentPage === "training") {
    return (
      <div className="app">
        <Sidebar />

        <main className="main-content">
          <Training />
        </main>
      </div>
    );
  }

  /* =========================
     MRI ANALYSIS
  ========================= */

  if (currentPage === "mri") {
    return (
      <div className="app">
        <Sidebar />

        <main className="main-content">
          <MRIAnalysis />
        </main>
      </div>
    );
  }

  /* =========================
     PRIVACY
  ========================= */

  if (currentPage === "privacy") {
    return (
      <div className="app">
        <Sidebar />

        <main className="main-content">
          <Privacy />
        </main>
      </div>
    );
  }

  /* =========================
     SETTINGS
  ========================= */

  if (currentPage === "settings") {
    return (
      <div className="app">
        <Sidebar />

        <main className="main-content">
          <Settings />
        </main>
      </div>
    );
  }

  /* =========================
     DASHBOARD
  ========================= */

  return (
    <div className="app">

      <Sidebar />

      <main className="main-content">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <h1>
              Federated Learning Dashboard
            </h1>

            <p>
              Privacy-preserving healthcare AI
            </p>
          </div>

          <div className="server-status">
            <span></span>
            Server Online
          </div>

        </header>


        {/* STATS */}

        <section className="stats">

          <div className="card">
            <p>Training Round</p>
            <h2>10</h2>
            <small>
              +2 from last round
            </small>
          </div>

          <div className="card">
            <p>Global Dice Score</p>
            <h2>89.4%</h2>
            <small>
              ↑ 4.8% improvement
            </small>
          </div>

          <div className="card">
            <p>Training Loss</p>
            <h2>0.21</h2>
            <small>
              ↓ 12.5% reduction
            </small>
          </div>

          <div className="card">
            <p>Active Hospitals</p>
            <h2>3 / 3</h2>
            <small>
              All nodes connected
            </small>
          </div>

        </section>


        {/* CHART + HOSPITALS */}

        <section className="content-grid">

          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>
                  Training Progress
                </h3>

                <p>
                  Global model performance
                </p>
              </div>

              <span className="badge">
                Live
              </span>

            </div>


            <div className="chart">

              <ResponsiveContainer
                width="100%"
                height={260}
              >

                <LineChart
                  data={trainingData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="round"
                    label={{
                      value: "Training Round",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />

                  <YAxis />

                  <Tooltip />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="dice"
                    name="Dice Score"
                    stroke="#2563eb"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />

                  <Line
                    type="monotone"
                    dataKey="loss"
                    name="Training Loss"
                    stroke="#ef4444"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </div>


          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>
                  Hospital Nodes
                </h3>

                <p>
                  Federated clients
                </p>
              </div>

            </div>


            <div className="hospital">

              <div className="hospital-icon">
                🏥
              </div>

              <div>
                <strong>
                  Hospital 1
                </strong>

                <p>
                  Training locally
                </p>
              </div>

              <span className="online">
                ●
              </span>

            </div>


            <div className="hospital">

              <div className="hospital-icon">
                🏥
              </div>

              <div>
                <strong>
                  Hospital 2
                </strong>

                <p>
                  Training locally
                </p>
              </div>

              <span className="online">
                ●
              </span>

            </div>


            <div className="hospital">

              <div className="hospital-icon">
                🏥
              </div>

              <div>
                <strong>
                  Hospital 3
                </strong>

                <p>
                  Training locally
                </p>
              </div>

              <span className="online">
                ●
              </span>

            </div>

          </div>

        </section>


        {/* MRI SEGMENTATION */}

        <section className="panel segmentation">

          <div className="panel-header">

            <div>

              <h3>
                🧠 MRI Tumor Segmentation
              </h3>

              <p>
                Latest model prediction
              </p>

            </div>

            <button
              onClick={() =>
                navigation("mri")
              }
            >
              View Analysis
            </button>

          </div>


          <div className="mri-section">

            <div className="mri-box">

              <div>
                🧠
              </div>

              <p>
                MRI Scan
              </p>

            </div>


            <div className="arrow">
              →
            </div>


            <div className="mri-box">

              <div>
                🎯
              </div>

              <p>
                Tumor Mask
              </p>

            </div>


            <div className="result">

              <span>
                Segmentation Accuracy
              </span>

              <strong>
                92.6%
              </strong>

            </div>

          </div>

        </section>


        {/* FOOTER */}

        <footer>

          <span>
            FedMed • Federated Healthcare AI
          </span>

          <span>
            🔐 Privacy Protected
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;