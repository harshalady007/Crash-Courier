import { useState } from "react";
import { createSchedule } from "../api";

interface Props {
  resumeId: number;
  minScore: number;
}

export default function AutomationCard({ resumeId, minScore }: Props) {
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    setError("");
    try {
      await createSchedule(resumeId, "", false, minScore, email);
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save schedule");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>4 · Automate</h2>
      <p className="subtitle">Re-run this search every day and (optionally) email new matches above your score threshold.</p>
      {saved ? (
        <p className="info">✓ Daily search scheduled. Manage schedules via the API (/api/automation/schedules).</p>
      ) : (
        <div className="row">
          <input
            type="email"
            placeholder="Email for digest (optional)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ minWidth: 260 }}
          />
          <button onClick={() => void save()} disabled={busy}>
            {busy ? "Saving…" : "Run daily"}
          </button>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
