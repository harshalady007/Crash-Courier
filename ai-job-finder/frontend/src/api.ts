// Thin fetch wrapper for the backend REST API.
import type { Filters, JobMatch, Recommendation, Resume, RoleFit, SearchResult } from "./types";

async function handle<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return resp.json() as Promise<T>;
}

export async function uploadResume(file: File): Promise<Resume> {
  const form = new FormData();
  form.append("file", file);
  return handle(await fetch("/api/resumes", { method: "POST", body: form }));
}

export async function analyzeResume(resumeId: number): Promise<RoleFit[]> {
  return handle(await fetch(`/api/resumes/${resumeId}/analyze`, { method: "POST" }));
}

export async function runSearch(
  resumeId: number,
  location: string,
  remoteOnly: boolean,
  roles: string[],
): Promise<SearchResult> {
  return handle(
    await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: resumeId,
        location: location || null,
        remote_only: remoteOnly,
        roles: roles.length ? roles : null,
      }),
    }),
  );
}

export async function fetchJobs(resumeId: number, filters: Filters): Promise<JobMatch[]> {
  const params = new URLSearchParams({
    resume_id: String(resumeId),
    min_score: String(filters.min_score),
    sort: filters.sort,
    limit: "100",
  });
  if (filters.remote_only) params.set("remote_only", "true");
  if (filters.fresher_only) params.set("fresher_only", "true");
  if (filters.internship) params.set("internship", "true");
  if (filters.full_time) params.set("full_time", "true");
  if (filters.location) params.set("location", filters.location);
  if (filters.posted_within) params.set("posted_within", filters.posted_within);
  return handle(await fetch(`/api/jobs?${params}`));
}

export async function generateRecommendation(matchId: number): Promise<Recommendation> {
  return handle(await fetch(`/api/jobs/${matchId}/recommend`, { method: "POST" }));
}

export async function createSchedule(
  resumeId: number,
  location: string,
  remoteOnly: boolean,
  minScore: number,
  email: string,
): Promise<unknown> {
  return handle(
    await fetch("/api/automation/schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: resumeId,
        location: location || null,
        remote_only: remoteOnly,
        min_score: minScore,
        email: email || null,
      }),
    }),
  );
}
