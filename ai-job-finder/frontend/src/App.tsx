import { useCallback, useEffect, useState } from "react";
import { analyzeResume, fetchJobs, runSearch } from "./api";
import AutomationCard from "./components/AutomationCard";
import FiltersBar from "./components/FiltersBar";
import JobsTable from "./components/JobsTable";
import RoleFitPanel from "./components/RoleFitPanel";
import UploadCard from "./components/UploadCard";
import type { Filters, JobMatch, Resume, RoleFit, SearchResult } from "./types";

const DEFAULT_FILTERS: Filters = {
  min_score: 40,
  remote_only: false,
  fresher_only: false,
  internship: false,
  full_time: false,
  location: "",
  posted_within: "",
  sort: "score",
};

export default function App() {
  const [resume, setResume] = useState<Resume | null>(null);
  const [roleFits, setRoleFits] = useState<RoleFit[]>([]);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [searchStats, setSearchStats] = useState<SearchResult["stats"] | null>(null);
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [analyzing, setAnalyzing] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const refreshJobs = useCallback(async () => {
    if (!resume || !searched) return;
    try {
      setMatches(await fetchJobs(resume.id, filters));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load jobs");
    }
  }, [resume, filters, searched]);

  // Debounced filter refresh
  useEffect(() => {
    const t = setTimeout(() => void refreshJobs(), 300);
    return () => clearTimeout(t);
  }, [refreshJobs]);

  async function handleAnalyze() {
    if (!resume) return;
    setAnalyzing(true);
    setError("");
    try {
      setRoleFits(await analyzeResume(resume.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleSearch(roles: string[], location: string, remoteOnly: boolean) {
    if (!resume) return;
    setSearching(true);
    setError("");
    try {
      const result = await runSearch(resume.id, location, remoteOnly, roles);
      setSearchStats(result.stats);
      setMatches(result.matches);
      setSearched(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="container">
      <header className="app-header">
        <h1>AI Job Finder</h1>
        <p>Upload your resume → see your best-fit roles → get scored, ready-to-apply job matches.</p>
      </header>

      {error && <p className="error">{error}</p>}

      <UploadCard
        resume={resume}
        onUploaded={(r) => {
          setResume(r);
          setRoleFits([]);
          setMatches([]);
          setSearchStats(null);
          setSearched(false);
        }}
      />

      {resume && (
        <RoleFitPanel
          roleFits={roleFits}
          analyzing={analyzing}
          searching={searching}
          onAnalyze={() => void handleAnalyze()}
          onSearch={(roles, location, remote) => void handleSearch(roles, location, remote)}
        />
      )}

      {searched && resume && (
        <>
          <section className="card">
            <h2>3 · Job matches</h2>
            {searchStats && (
              <p className="subtitle">
                Sources:{" "}
                {Object.entries(searchStats.sources)
                  .filter(([, s]) => !s.error?.startsWith("disabled"))
                  .map(([id, s]) => `${id} (${s.error ? "error" : s.fetched})`)
                  .join(" · ")}
              </p>
            )}
            <FiltersBar filters={filters} onChange={setFilters} />
            <div style={{ marginTop: 14, overflowX: "auto" }}>
              <JobsTable matches={matches} />
            </div>
          </section>

          <AutomationCard resumeId={resume.id} minScore={filters.min_score} />
        </>
      )}
    </div>
  );
}
