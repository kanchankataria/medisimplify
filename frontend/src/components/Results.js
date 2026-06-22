import React from "react";

const riskColors = {
  High: { bg: "#fff5f5", border: "#fecaca", text: "#dc2626", badge: "#dc2626" },
  Medium: {
    bg: "#fffbeb",
    border: "#fde68a",
    text: "#d97706",
    badge: "#d97706",
  },
  Low: { bg: "#f0fdf4", border: "#bbf7d0", text: "#16a34a", badge: "#16a34a" },
  Unknown: { bg: "#f8f9fa", border: "#dee2e6", text: "#666", badge: "#666" },
};

const valueColors = {
  High: { bg: "#fff5f5", text: "#dc2626" },
  Medium: { bg: "#fffbeb", text: "#d97706" },
  Low: { bg: "#f0fdf4", text: "#16a34a" },
  Normal: { bg: "#f0fdf4", text: "#16a34a" },
};

function Results({ data, onBack }) {
  if (!data) return null;

  const risk = data.risk_level || "Unknown";
  const colors = riskColors[risk] || riskColors["Unknown"];
  const abnormalValues = data.abnormal_values || [];
  const actionSteps = data.action_plan
    ? data.action_plan.split("\n").filter((s) => s.trim())
    : [];

  return (
    <div className="grid-2col">
      {/* Left Sidebar */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {/* Risk Summary Card */}
        <div
          style={{
            background: colors.bg,
            border: `1px solid ${colors.border}`,
            borderRadius: "12px",
            padding: "1.25rem",
            textAlign: "center",
          }}
        >
          <p
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "#666",
              margin: "0 0 12px",
            }}
          >
            Risk level
          </p>
          <div style={{ fontSize: "48px", marginBottom: "8px" }}>
            {risk === "High" ? "🔴" : risk === "Medium" ? "🟡" : "🟢"}
          </div>
          <p
            style={{
              fontSize: "20px",
              fontWeight: "700",
              color: colors.badge,
              margin: "0 0 4px",
            }}
          >
            {risk} Risk
          </p>
          <p style={{ fontSize: "12px", color: "#888", margin: 0 }}>
            {risk === "High"
              ? "See doctor within 7 days"
              : risk === "Medium"
                ? "Schedule a follow-up"
                : "Continue regular checkups"}
          </p>
        </div>

        {/* Abnormal Values */}
        {abnormalValues.length > 0 && (
          <div
            style={{
              background: "#fff",
              border: "1px solid #e9ecef",
              borderRadius: "12px",
              padding: "1.25rem",
            }}
          >
            <p
              style={{
                fontSize: "13px",
                fontWeight: "600",
                color: "#666",
                margin: "0 0 12px",
              }}
            >
              Flagged values
            </p>
            {abnormalValues.map((val, i) => {
              const vc = valueColors[val.risk_level] || valueColors["Normal"];
              return (
                <div
                  key={i}
                  style={{
                    background: vc.bg,
                    borderRadius: "8px",
                    padding: "10px 12px",
                    marginBottom: "8px",
                  }}
                >
                  <p
                    style={{
                      fontSize: "12px",
                      fontWeight: "600",
                      color: vc.text,
                      margin: "0 0 2px",
                    }}
                  >
                    {val.name}
                  </p>
                  <p
                    style={{
                      fontSize: "13px",
                      fontWeight: "700",
                      color: vc.text,
                      margin: "0 0 2px",
                    }}
                  >
                    {val.value}
                  </p>
                  <p
                    style={{
                      fontSize: "11px",
                      color: vc.text,
                      margin: 0,
                      opacity: 0.8,
                    }}
                  >
                    Normal: {val.normal_range}
                  </p>
                </div>
              );
            })}
          </div>
        )}

        {/* Analyze Another */}
        <div
          style={{
            background: "#fff",
            border: "1px solid #e9ecef",
            borderRadius: "12px",
            padding: "1.25rem",
          }}
        >
          <button
            onClick={onBack}
            style={{
              width: "100%",
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #dee2e6",
              background: "#fff",
              color: "#333",
              cursor: "pointer",
              fontSize: "13px",
              fontWeight: "500",
            }}
          >
            ← Analyze another report
          </button>
        </div>
      </div>

      {/* Right Main Area */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {/* Plain English Summary */}
        <div
          style={{
            background: "#fff",
            border: "1px solid #e9ecef",
            borderRadius: "12px",
            padding: "1.25rem",
          }}
        >
          <p
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "#666",
              margin: "0 0 12px",
            }}
          >
            Plain English summary
          </p>
          <div
            style={{
              background: "#f8f9fa",
              borderRadius: "8px",
              padding: "1rem",
            }}
          >
            <p
              style={{
                fontSize: "14px",
                lineHeight: 1.8,
                color: "#333",
                margin: 0,
              }}
            >
              {data.simplified_text}
            </p>
          </div>
        </div>

        {/* Abnormal Values Detail */}
        {abnormalValues.length > 0 && (
          <div
            style={{
              background: "#fff",
              border: "1px solid #e9ecef",
              borderRadius: "12px",
              padding: "1.25rem",
            }}
          >
            <p
              style={{
                fontSize: "13px",
                fontWeight: "600",
                color: "#666",
                margin: "0 0 12px",
              }}
            >
              What these values mean
            </p>
            <div
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              {abnormalValues.map((val, i) => {
                const vc = valueColors[val.risk_level] || valueColors["Normal"];
                return (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      gap: "12px",
                      padding: "12px",
                      background: vc.bg,
                      borderRadius: "8px",
                    }}
                  >
                    <div style={{ minWidth: "80px" }}>
                      <p
                        style={{
                          fontSize: "12px",
                          fontWeight: "700",
                          color: vc.text,
                          margin: 0,
                        }}
                      >
                        {val.name}
                      </p>
                      <p
                        style={{
                          fontSize: "13px",
                          fontWeight: "700",
                          color: vc.text,
                          margin: "2px 0",
                        }}
                      >
                        {val.value}
                      </p>
                    </div>
                    <div
                      style={{
                        borderLeft: `2px solid ${vc.text}`,
                        paddingLeft: "12px",
                        opacity: 0.8,
                      }}
                    >
                      <p
                        style={{
                          fontSize: "12px",
                          color: vc.text,
                          margin: 0,
                          lineHeight: 1.6,
                        }}
                      >
                        {val.explanation}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Plan */}
        <div
          style={{
            background: "#fff",
            border: "1px solid #e9ecef",
            borderRadius: "12px",
            padding: "1.25rem",
          }}
        >
          <p
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "#666",
              margin: "0 0 12px",
            }}
          >
            Action plan
          </p>
          <div style={{ borderLeft: "3px solid #0066cc", paddingLeft: "16px" }}>
            {actionSteps.length > 0 ? (
              actionSteps.map((step, i) => (
                <p
                  key={i}
                  style={{
                    fontSize: "13px",
                    color: "#333",
                    margin: "0 0 8px",
                    lineHeight: 1.6,
                  }}
                >
                  {step}
                </p>
              ))
            ) : (
              <p
                style={{
                  fontSize: "13px",
                  color: "#333",
                  margin: 0,
                  lineHeight: 1.6,
                }}
              >
                {data.action_plan}
              </p>
            )}
          </div>
        </div>

        {/* Disclaimer */}
        <div
          style={{
            background: "#fffbeb",
            border: "1px solid #fde68a",
            borderRadius: "12px",
            padding: "1rem",
          }}
        >
          <p
            style={{
              fontSize: "11px",
              color: "#92400e",
              margin: 0,
              lineHeight: 1.6,
            }}
          >
            ⚠️{" "}
            {data.disclaimer ||
              "This is an AI-assisted summary for educational purposes only. Always consult your doctor."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default Results;
