// API contract types — mirror backend/app/schemas.py

export interface Resume {
  id: number;
  filename: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: string[];
  tools: string[];
  education: { degree?: string; institution?: string; year?: string }[];
  projects: { title?: string; description?: string }[];
  experience: { title?: string; description?: string }[];
  certifications: string[];
  target_roles: string[];
  experience_years: number;
}

export interface RoleFit {
  id: number;
  role_name: string;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  description: string;
  required_skills: string[];
  experience_required: string | null;
  fresher_friendly: boolean;
  salary: string | null;
  url: string;
  source: string;
  posted_at: string | null;
}

export interface ScoreComponent {
  score: number;
  weight: number;
}

export interface JobMatch {
  id: number;
  score: number;
  components: Record<string, ScoreComponent>;
  matched_skills: string[];
  missing_skills: string[];
  shortlist_chance: string;
  application_difficulty: string;
  why_apply: string;
  recommendation: Recommendation | null;
  job: Job;
}

export interface Recommendation {
  why_fit: string;
  keywords_to_add: string[];
  cover_letter: string;
  linkedin_message: string;
  priority: string;
  generated_by: string;
}

export interface SearchResult {
  run_id: number;
  stats: {
    sources: Record<string, { fetched: number; error: string | null }>;
    keywords: string[];
  };
  total_jobs: number;
  new_jobs: number;
  matches: JobMatch[];
}

export interface Filters {
  min_score: number;
  remote_only: boolean;
  fresher_only: boolean;
  internship: boolean;
  full_time: boolean;
  location: string;
  posted_within: "" | "24h" | "7d" | "30d";
  sort: "score" | "date";
}
