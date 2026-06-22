import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000";

const riskColors = {
  High: { bg: "#fff5f5", text: "#dc2626", border: "#fecaca" },
  Medium: { bg: "#fffbeb", text: "#d97706", border: "#fde68a" },
  Low: { bg: "#f0fdf4", text: "#16a34a", border: "#bbf7d0" },
  Unknown: { bg: "#f8f9fa", text: "#666", border: "#dee2e6" },
};

function History({ onViewReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/history`);
      setReports(response.data.reports || []);
    } catch (err) {
      setError("Could not load history. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (reportId) => {
    try {
      await axios.delete(`${API_URL}/report/${reportId}`);
      setReports(reports.filter((r) => r.id !== reportId));
    } catch (err) {
      alert("Failed to delete report.");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getFileIcon = (fileType) => {
    if (fileType === "image") return "🩻";
    if (fileType === "scanned_pdf") return "📸";
    return "📄";
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "4rem", color: "#888" }}>
        <p style={{ fontSize: "32px" }}>⏳</p>
        <p>Loading your reports...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          background: "#fff5f5",
          border: "1px solid #fecaca",
          borderRadius: "12px",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <p style={{ fontSize: "32px" }}>⚠️</p>
        <p style={{ color: "#dc2626", fontSize: "14px" }}>{error}</p>
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div
        style={{
          background: "#fff",
          border: "1px solid #e9ecef",
          borderRadius: "12px",
          padding: "4rem",
          textAlign: "center",
        }}
      >
        <p style={{ fontSize: "48px" }}>📭</p>
        <h3 style={{ color: "#333", margin: "0 0 8px" }}>No reports yet</h3>
        <p style={{ color: "#888", fontSize: "14px" }}>
          Upload your first medical report to get started.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <h2
          style={{
            fontSize: "18px",
            fontWeight: "600",
            margin: 0,
            color: "#1a1a2e",
          }}
        >
          Report History
        </h2>
        <span style={{ fontSize: "13px", color: "#888" }}>
          {reports.length} reports
        </span>
      </div>

      {/* Stats Row */}
      <div className="grid-3col">
        {[
          {
            label: "High risk",
            count: reports.filter((r) => r.risk_level === "High").length,
            color: "#dc2626",
            bg: "#fff5f5",
          },
          {
            label: "Medium risk",
            count: reports.filter((r) => r.risk_level === "Medium").length,
            color: "#d97706",
            bg: "#fffbeb",
          },
          {
            label: "Low risk",
            count: reports.filter((r) => r.risk_level === "Low").length,
            color: "#16a34a",
            bg: "#f0fdf4",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            style={{
              background: stat.bg,
              borderRadius: "12px",
              padding: "1rem",
              textAlign: "center",
            }}
          >
            <p
              style={{
                fontSize: "24px",
                fontWeight: "700",
                color: stat.color,
                margin: "0 0 4px",
              }}
            >
              {stat.count}
            </p>
            <p style={{ fontSize: "12px", color: "#666", margin: 0 }}>
              {stat.label}
            </p>
          </div>
        ))}
      </div>

      {/* Reports List */}
      <div
        style={{
          background: "#fff",
          border: "1px solid #e9ecef",
          borderRadius: "12px",
          overflow: "hidden",
        }}
      >
        {reports.map((report, index) => {
          const colors = riskColors[report.risk_level] || riskColors["Unknown"];
          return (
            <div
              key={report.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "16px",
                padding: "16px 20px",
                borderBottom:
                  index < reports.length - 1 ? "1px solid #f0f0f0" : "none",
                transition: "background 0.15s",
              }}
            >
              {/* File Icon */}
              <div
                style={{
                  fontSize: "28px",
                  minWidth: "40px",
                  textAlign: "center",
                }}
              >
                {getFileIcon(report.file_type)}
              </div>

              {/* Report Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <p
                  style={{
                    fontSize: "14px",
                    fontWeight: "500",
                    margin: "0 0 4px",
                    color: "#1a1a2e",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {report.filename}
                </p>
                <p
                  style={{ fontSize: "12px", color: "#888", margin: "0 0 4px" }}
                >
                  {formatDate(report.created_at)}
                </p>
                <p
                  style={{
                    fontSize: "12px",
                    color: "#555",
                    margin: 0,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {report.simplified_text?.substring(0, 80)}...
                </p>
              </div>

              {/* Risk Badge */}
              <div style={{ minWidth: "80px", textAlign: "center" }}>
                <span
                  style={{
                    background: colors.bg,
                    color: colors.text,
                    border: `1px solid ${colors.border}`,
                    fontSize: "11px",
                    fontWeight: "600",
                    padding: "4px 10px",
                    borderRadius: "20px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {report.risk_level === "High"
                    ? "🔴"
                    : report.risk_level === "Medium"
                      ? "🟡"
                      : "🟢"}{" "}
                  {report.risk_level}
                </span>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", gap: "8px", minWidth: "120px" }}>
                <button
                  onClick={() => onViewReport(report)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: "6px",
                    border: "1px solid #0066cc",
                    background: "#fff",
                    color: "#0066cc",
                    cursor: "pointer",
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  View
                </button>
                <button
                  onClick={() => handleDelete(report.id)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: "6px",
                    border: "1px solid #fecaca",
                    background: "#fff5f5",
                    color: "#dc2626",
                    cursor: "pointer",
                    fontSize: "12px",
                  }}
                >
                  🗑
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default History;
