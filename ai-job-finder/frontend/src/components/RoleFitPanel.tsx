import { useState } from "react";
import type { RoleFit } from "../types";

interface Props {
  roleFits: RoleFit[];
  analyzing: boolean;
  searching: boolean;
  onAnalyze: () => void;
  onSearch: (selectedRoles: string[], location: string, remoteOnly: boolean) => void;
}

export default function RoleFitPanel({ roleFits, analyzing, searching, onAnalyze, onSearch }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [location, setLocation] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);

  function toggle(role: string) {
    const next = new Set(selected);
    if (next.has(role)) next.delete(role);
    else next.add(role);
    setSelected(next);
  }

  return (
    <section className="card">
      <h2>2 · Best-fit roles</h2>
      <p className="subtitle">
        Deterministic fit scores from your skills — select roles to focus the search (top 3 used by default).
      </p>

      {roleFits.length === 0 ? (
        <button onClick={onAnalyze} disabled={analyzing}>
          {analyzing ? "Analyzing…" : "Analyze my resume"}
        </button>
      ) : (
        <>
          <div className="role-grid">
            {roleFits.map((fit) => (
              <div
                key={fit.id}
                className={`role-card${selected.has(fit.role_name) ? " selected" : ""}`}
                onClick={() => toggle(fit.role_name)}
              >
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <strong>{fit.role_name}</strong>
                  <span className={`score ${fit.score >= 60 ? "score-high" : fit.score >= 40 ? "score-med" : "score-low"}`}>
                    {fit.score}
                  </span>
                </div>
                <div className="explanation">{fit.explanation}</div>
              </div>
            ))}
          </div>

          <div className="row" style={{ marginTop: 16 }}>
            <input
              type="text"
              placeholder="Location (e.g. Bengaluru) — optional"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              style={{ minWidth: 260 }}
            />
            <label style={{ fontSize: 13 }}>
              <input type="checkbox" checked={remoteOnly} onChange={(e) => setRemoteOnly(e.target.checked)} /> Remote only
            </label>
            <button onClick={() => onSearch([...selected], location, remoteOnly)} disabled={searching}>
              {searching ? "Searching all sources…" : "Search jobs"}
            </button>
          </div>
        </>
      )}
    </section>
  );
}
