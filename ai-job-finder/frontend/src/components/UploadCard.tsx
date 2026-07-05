import { useRef, useState } from "react";
import { uploadResume } from "../api";
import type { Resume } from "../types";

interface Props {
  resume: Resume | null;
  onUploaded: (resume: Resume) => void;
}

export default function UploadCard({ resume, onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      onUploaded(await uploadResume(file));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>1 · Upload your resume</h2>
      <p className="subtitle">PDF or DOCX, up to 10 MB. Parsed locally on your backend.</p>

      <div
        className={`dropzone${drag ? " drag" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          void handleFile(e.dataTransfer.files[0]);
        }}
      >
        {busy ? "Parsing…" : resume ? `Uploaded: ${resume.filename} — click to replace` : "Drop your resume here or click to browse"}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        hidden
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />
      {error && <p className="error">{error}</p>}

      {resume && (
        <div style={{ marginTop: 14 }}>
          <div className="row" style={{ gap: 24 }}>
            <div>
              <strong>{resume.name ?? "Name not detected"}</strong>
              <div className="info">
                {resume.email ?? "no email found"} · {resume.experience_years} yrs experience
              </div>
            </div>
          </div>
          <div style={{ marginTop: 10 }}>
            {resume.skills.map((s) => (
              <span key={s} className="chip">
                {s}
              </span>
            ))}
            {resume.skills.length === 0 && <span className="info">No known skills detected — is the resume text-based?</span>}
          </div>
        </div>
      )}
    </section>
  );
}
