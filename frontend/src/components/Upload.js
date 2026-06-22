import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

const API_URL = "http://localhost:8000";

const reportTypes = [
  { icon: "🧪", label: "Lab reports", cls: "type-badge-blue" },
  { icon: "🫁", label: "X-rays / MRI", cls: "type-badge-purple" },
  { icon: "📋", label: "Discharge notes", cls: "type-badge-teal" },
  { icon: "💊", label: "Prescriptions", cls: "type-badge-amber" },
];

const steps = [
  { num: "1", label: "Upload your report", color: "#4f8ef7" },
  { num: "2", label: "Claude AI reads it", color: "#7F77DD" },
  { num: "3", label: "Plain English summary", color: "#1D9E75" },
  { num: "4", label: "See your risk level", color: "#D85A30" },
  { num: "5", label: "Follow action plan", color: "#D4537E" },
];

function Upload({ onResults }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onResults(response.data);
    } catch (err) {
      setError("Failed to analyze. Please check your API key and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid-2col">
      {/* Left Sidebar */}
      <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
        {/* Blue Upload Card */}
        <div className="card-blue">
          <p
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "rgba(255,255,255,0.8)",
              margin: "0 0 10px",
            }}
          >
            Upload your report
          </p>
          <div
            {...getRootProps()}
            className="dropzone-blue"
            style={{
              background: isDragActive
                ? "rgba(255,255,255,0.25)"
                : "rgba(255,255,255,0.1)",
            }}
          >
            <input {...getInputProps()} />
            <div style={{ fontSize: "32px", marginBottom: "6px" }}>📂</div>
            <p style={{ fontSize: "12px", color: "#fff", margin: 0 }}>
              {isDragActive
                ? "Drop it here!"
                : "Drag & drop or click\nPDF · JPG · PNG"}
            </p>
          </div>

          {file && (
            <div
              style={{
                background: "rgba(255,255,255,0.2)",
                borderRadius: "8px",
                padding: "8px 12px",
                marginBottom: "10px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <span>📄</span>
              <span
                style={{
                  fontSize: "12px",
                  color: "#fff",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {file.name}
              </span>
            </div>
          )}

          {error && (
            <div
              style={{
                background: "rgba(255,255,255,0.15)",
                borderRadius: "8px",
                padding: "8px 12px",
                marginBottom: "10px",
              }}
            >
              <p style={{ fontSize: "12px", color: "#fff", margin: 0 }}>
                ⚠️ {error}
              </p>
            </div>
          )}

          <button
            className="btn-white"
            onClick={handleUpload}
            disabled={!file || loading}
            style={{
              opacity: !file || loading ? 0.6 : 1,
              cursor: !file || loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "🔄 Analyzing..." : "✨ Analyze Report"}
          </button>
        </div>

        {/* Report Types */}
        <div className="card">
          <p
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "#666",
              margin: "0 0 10px",
            }}
          >
            Supported types
          </p>
          {reportTypes.map((t) => (
            <div key={t.label} className={`type-item ${t.cls}`}>
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </div>
          ))}
        </div>

        {/* How it works */}
        <div className="card-dark">
          <p
            style={{
              fontSize: "12px",
              fontWeight: "600",
              color: "rgba(255,255,255,0.6)",
              margin: "0 0 12px",
            }}
          >
            How it works
          </p>
          {steps.map((s) => (
            <div
              key={s.num}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "10px",
              }}
            >
              <div className="step-circle" style={{ background: s.color }}>
                {s.num}
              </div>
              <span style={{ fontSize: "12px", color: "#fff" }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right Welcome Area */}
      <div
        className="card"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "420px",
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: "72px", marginBottom: "1rem" }}>🏥</div>
        <h2
          style={{
            fontSize: "22px",
            fontWeight: "700",
            color: "#1a1a2e",
            margin: "0 0 12px",
          }}
        >
          Understand your medical reports
        </h2>
        <p
          style={{
            fontSize: "14px",
            color: "#888",
            maxWidth: "360px",
            lineHeight: 1.7,
            margin: "0 0 2rem",
          }}
        >
          Upload any medical document and get a plain English explanation with
          color-coded risk assessment.
        </p>
        <div
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          <span className="badge badge-high">🔴 High risk</span>
          <span className="badge badge-medium">🟡 Medium risk</span>
          <span className="badge badge-low">🟢 Low risk</span>
        </div>
      </div>
    </div>
  );
}

export default Upload;
