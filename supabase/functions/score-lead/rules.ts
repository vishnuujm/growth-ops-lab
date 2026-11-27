// Rules-based lead score: the fallback used when the AI is unavailable.
// Mirrored in p01-lead-router/rules.py; a test fails if the two disagree.
// Pure function: no network, no environment variables.

export type Lead = {
  email?: string;
  company_size?: string;
  role?: string;
  timeline?: string;
  use_case?: string;
};

export type Tier = "A" | "B" | "C";
export type Score = { score: number; tier: Tier; reason: string };

type Rule = { points: number; words: string[]; label: string };

export type Icp = {
  thresholds: { A: number; B: number };
  company_size: Record<string, number>;
  size_labels: Record<string, string>;
  role: { negative: Rule; senior: Rule; manager: Rule; other: { points: number; label: string } };
  timeline: Record<string, { points: number; label: string }>;
  use_case: {
    points_per_need: number;
    max_points: number;
    needs: string[][];
    junk: { points: number; words: string[] };
  };
  free_email: { points: number; domains: string[] };
};

const clean = (value: unknown): string => String(value ?? "").trim().toLowerCase();
const words = (text: string): string => ` ${(text.match(/[a-z0-9]+/g) ?? []).join(" ")} `;
const hasAny = (padded: string, list: string[]): boolean => list.some((w) => padded.includes(` ${w} `));
const own = <T>(table: Record<string, T>, key: string): T | undefined =>
  Object.hasOwn(table, key) ? table[key] : undefined;

export function scoreLead(lead: Lead, icp: Icp): Score {
  let total = 0;
  const good: string[] = [];
  const bad: string[] = [];

  const size = clean(lead.company_size);
  const sizePoints = own(icp.company_size, size);
  if (sizePoints !== undefined) {
    total += sizePoints;
    good.push(icp.size_labels[size]);
  }

  const role = words(clean(lead.role));
  const r = icp.role;
  if (role.trim()) {
    if (hasAny(role, r.negative.words)) {
      total += r.negative.points;
      bad.push(r.negative.label);
    } else {
      const level = hasAny(role, r.senior.words) ? r.senior : hasAny(role, r.manager.words) ? r.manager : r.other;
      total += level.points;
      good.push(level.label);
    }
  }

  const timeline = own(icp.timeline, clean(lead.timeline));
  if (timeline) {
    total += timeline.points;
    good.push(timeline.label);
  }

  const need = words(clean(lead.use_case));
  const u = icp.use_case;
  const matched = u.needs.filter((group) => hasAny(need, group)).length;
  if (matched) {
    total += Math.min(matched * u.points_per_need, u.max_points);
    good.push("clear need");
  }
  if (hasAny(need, u.junk.words)) {
    total += u.junk.points;
    bad.push("message looks like junk or a job request");
  }

  const email = clean(lead.email);
  const domain = email.includes("@") ? email.slice(email.lastIndexOf("@") + 1) : "";
  if (icp.free_email.domains.includes(domain)) {
    total += icp.free_email.points;
    bad.push("personal email");
  }

  const score = Math.max(0, Math.min(100, total));
  const tier: Tier = score >= icp.thresholds.A ? "A" : score >= icp.thresholds.B ? "B" : "C";

  // Concerns come first for weak leads, so the reason explains the grade.
  const parts = tier === "C" ? [...bad, ...good] : [...good, ...bad];
  let reason = parts.join(", ") || "not enough information";
  reason = reason[0].toUpperCase() + reason.slice(1);
  return { score, tier, reason: reason.slice(0, 200) };
}
