import React, { useState } from "react";
import Upload from "./components/Upload";
import Results from "./components/Results";
import History from "./components/History";
import "./index.css";

function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [reportData, setReportData] = useState(null);

  const showResults = (data) => {
    setReportData(data);
    setCurrentPage("results");
  };

  return (
    <div
      style={{ minHeight: "100vh", background: "#f0f4f8", overflowY: "auto" }}
    >
      <header className="header">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "#4f8ef7",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
            }}
          >
            🏥
          </div>
          <span style={{ fontSize: "17px", fontWeight: "600", color: "#fff" }}>
            MediSimplify
          </span>
          <span
            style={{
              background: "#4f8ef7",
              color: "#fff",
              fontSize: "10px",
              padding: "2px 8px",
              borderRadius: "20px",
            }}
            className="hide-mobile"
          >
            AI powered
          </span>
        </div>
        <nav style={{ display: "flex", gap: "8px" }}>
          <button
            className={
              currentPage === "home" || currentPage === "results"
                ? "btn-nav-active"
                : "btn-nav"
            }
            onClick={() => setCurrentPage("home")}
          >
            Upload
          </button>
          <button
            className={currentPage === "history" ? "btn-nav-active" : "btn-nav"}
            onClick={() => setCurrentPage("history")}
          >
            History
          </button>
        </nav>
      </header>

      <main className="main-content">
        {currentPage === "home" && <Upload onResults={showResults} />}
        {currentPage === "results" && (
          <Results data={reportData} onBack={() => setCurrentPage("home")} />
        )}
        {currentPage === "history" && <History onViewReport={showResults} />}
      </main>
    </div>
  );
}

export default App;
