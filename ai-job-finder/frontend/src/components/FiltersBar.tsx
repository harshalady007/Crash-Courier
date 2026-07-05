import type { Filters } from "../types";

interface Props {
  filters: Filters;
  onChange: (filters: Filters) => void;
}

export default function FiltersBar({ filters, onChange }: Props) {
  const set = <K extends keyof Filters>(key: K, value: Filters[K]) => onChange({ ...filters, [key]: value });

  return (
    <div className="filters">
      <label>
        Min score {filters.min_score}
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={filters.min_score}
          onChange={(e) => set("min_score", Number(e.target.value))}
        />
      </label>
      <label>
        <input type="checkbox" checked={filters.remote_only} onChange={(e) => set("remote_only", e.target.checked)} />
        Remote
      </label>
      <label>
        <input type="checkbox" checked={filters.fresher_only} onChange={(e) => set("fresher_only", e.target.checked)} />
        Fresher-friendly
      </label>
      <label>
        <input type="checkbox" checked={filters.internship} onChange={(e) => set("internship", e.target.checked)} />
        Internship
      </label>
      <label>
        <input type="checkbox" checked={filters.full_time} onChange={(e) => set("full_time", e.target.checked)} />
        Full-time
      </label>
      <label>
        Posted
        <select
          value={filters.posted_within}
          onChange={(e) => set("posted_within", e.target.value as Filters["posted_within"])}
        >
          <option value="">any time</option>
          <option value="24h">last 24h</option>
          <option value="7d">last 7 days</option>
          <option value="30d">last 30 days</option>
        </select>
      </label>
      <label>
        Location
        <input
          type="text"
          value={filters.location}
          placeholder="filter…"
          style={{ width: 120 }}
          onChange={(e) => set("location", e.target.value)}
        />
      </label>
      <label>
        Sort
        <select value={filters.sort} onChange={(e) => set("sort", e.target.value as Filters["sort"])}>
          <option value="score">match score</option>
          <option value="date">newest</option>
        </select>
      </label>
    </div>
  );
}
