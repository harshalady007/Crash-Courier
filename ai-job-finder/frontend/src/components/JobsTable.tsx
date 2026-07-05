import { useState } from "react";
import { generateRecommendation } from "../api";
import type { JobMatch, Recommendation } from "../types";

interface Props {
  matches: JobMatch[];
}

function scoreClass(score: number): string {
  if (score >= 75) return "score-high";
  if (score >= 55) return "score-med";
  return "score-low";
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "1 day ago";
  if (days < 30) return `${days} days ago`;
  return new Date(iso).toLocaleDateString();
}

export default function JobsTable({ matches }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);
  const [recs, setRecs] = useState<Record<number, Recommendation>>({});
  const [recBusy, setRecBusy] = useState<number | null>(null);
  const [recError, setRecError] = useState("");

  async function loadRecommendation(match: JobMatch) {
    if (recs[match.id] || match.recommendation) return;
    setRecBusy(match.id);
    setRecError("");
    try {
      const rec = await generateRecommendation(match.id);
      setRecs((prev) => ({ ...prev, [match.id]: rec }));
    } catch (e) {
      setRecError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setRecBusy(null);
    }
  }

  if (matches.length === 0) {
    return <p className="info">No jobs match the current filters. Lower the minimum score or run a new search.</p>;
  }

  return (
    <table className="jobs">
      <thead>
        <tr>
          <th>Score</th>
          <th>Job</th>
          <th>Location</th>
          <th>Experience</th>
          <th>Skills</th>
          <th>Posted</th>
          <th>Apply</th>
        </tr>
      </thead>
      <tbody>
        {matches.map((m) => {
          const rec = recs[m.id] ?? m.recommendation;
          return [
            <tr key={m.id} className="job-row" onClick={() => setExpanded(expanded === m.id ? null : m.id)}>
              <td>
                <span className={`score-badge ${scoreClass(m.score)}`}>{m.score}</span>
                <div className="source-tag">{m.shortlist_chance} chance</div>
              </td>
              <td>
                <strong>{m.job.title}</strong>
                <div className="source-tag">
                  {m.job.company} · via {m.job.source}
                </div>
              </td>
              <td>
                {m.job.remote ? <span className="chip match">Remote</span> : m.job.location || "—"}
              </td>
              <td>{m.job.experience_required ?? (m.job.fresher_friendly ? "Fresher friendly" : "—")}</td>
              <td style={{ maxWidth: 260 }}>
                {m.matched_skills.slice(0, 4).map((s) => (
                  <span key={s} className="chip match">{s}</span>
                ))}
                {m.missing_skills.slice(0, 2).map((s) => (
                  <span key={s} className="chip miss">{s}</span>
                ))}
              </td>
              <td>{formatDate(m.job.posted_at)}</td>
              <td onClick={(e) => e.stopPropagation()}>
                <a className="apply" href={m.job.url} target="_blank" rel="noreferrer noopener">
                  Apply ↗
                </a>
              </td>
            </tr>,
            expanded === m.id && (
              <tr key={`${m.id}-detail`}>
                <td colSpan={7} className="detail-cell">
                  <div className="detail">
                    <h4>Why apply</h4>
                    <p style={{ marginTop: 0 }}>{m.why_apply}</p>

                    <div className="components">
                      {Object.entries(m.components).map(([name, c]) => (
                        <div key={name} className="component">
                          <div className="label">
                            {name} · w{Math.round(c.weight * 100)}%
                          </div>
                          <div>{c.score}</div>
                          <div className="bar">
                            <div style={{ width: `${c.score}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>

                    <p className="info">
                      Difficulty: {m.application_difficulty}
                      {m.job.salary ? ` · Salary: ${m.job.salary}` : ""}
                    </p>

                    {m.job.description && (
                      <>
                        <h4>Description</h4>
                        <p className="info" style={{ whiteSpace: "pre-wrap" }}>
                          {m.job.description.slice(0, 1200)}
                          {m.job.description.length > 1200 ? "…" : ""}
                        </p>
                      </>
                    )}

                    {rec ? (
                      <>
                        <h4>Application kit ({rec.generated_by === "llm" ? "AI-generated" : "template"}) — priority: {rec.priority}</h4>
                        <p>{rec.why_fit}</p>
                        {rec.keywords_to_add.length > 0 && (
                          <p>
                            Add to resume:{" "}
                            {rec.keywords_to_add.map((k) => (
                              <span key={k} className="chip">{k}</span>
                            ))}
                          </p>
                        )}
                        <div className="row" style={{ alignItems: "flex-start" }}>
                          <div style={{ flex: 1, minWidth: 300 }}>
                            <div className="row" style={{ justifyContent: "space-between" }}>
                              <strong>Cover letter</strong>
                              <button className="secondary" onClick={() => void navigator.clipboard.writeText(rec.cover_letter)}>
                                Copy
                              </button>
                            </div>
                            <pre className="asset">{rec.cover_letter}</pre>
                          </div>
                          <div style={{ flex: 1, minWidth: 300 }}>
                            <div className="row" style={{ justifyContent: "space-between" }}>
                              <strong>LinkedIn message</strong>
                              <button className="secondary" onClick={() => void navigator.clipboard.writeText(rec.linkedin_message)}>
                                Copy
                              </button>
                            </div>
                            <pre className="asset">{rec.linkedin_message}</pre>
                          </div>
                        </div>
                      </>
                    ) : (
                      <button onClick={() => void loadRecommendation(m)} disabled={recBusy === m.id}>
                        {recBusy === m.id ? "Generating…" : "Generate application kit"}
                      </button>
                    )}
                    {recError && expanded === m.id && <p className="error">{recError}</p>}
                  </div>
                </td>
              </tr>
            ),
          ];
        })}
      </tbody>
    </table>
  );
}
