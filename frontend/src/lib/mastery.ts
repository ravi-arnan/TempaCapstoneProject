/**
 * Shared score → visual-tone mapping for the progress dashboard.
 * Mirrors the three understanding tiers (tinggi / sedang / rendah) used across
 * the app so the trend chart and topic list stay color-consistent.
 */

export const MASTERY_HIGH_THRESHOLD = 75;
export const MASTERY_MEDIUM_THRESHOLD = 50;

export interface ScoreTone {
  /** Tailwind background class for bars/fills. */
  bar: string;
  /** Tailwind text class for matching labels. */
  text: string;
}

const HIGH: ScoreTone = { bar: "bg-status-tinggi", text: "text-status-tinggi" };
const MEDIUM: ScoreTone = { bar: "bg-status-sedang", text: "text-status-sedang" };
const LOW: ScoreTone = { bar: "bg-status-rendah", text: "text-status-rendah" };

export function scoreTone(score: number): ScoreTone {
  if (score >= MASTERY_HIGH_THRESHOLD) return HIGH;
  if (score >= MASTERY_MEDIUM_THRESHOLD) return MEDIUM;
  return LOW;
}

const ID_MONTHS_SHORT = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "Mei",
  "Jun",
  "Jul",
  "Agu",
  "Sep",
  "Okt",
  "Nov",
  "Des",
] as const;

/**
 * Formats an ISO date (YYYY-MM-DD) to a short Indonesian label like "6 Jun".
 * Parses the parts directly to avoid timezone shifts from `new Date(string)`.
 */
export function formatTrendDate(isoDate: string): string {
  const [, month, day] = isoDate.split("-").map(Number);
  if (!month || !day) return isoDate;
  return `${day} ${ID_MONTHS_SHORT[month - 1] ?? ""}`.trim();
}
