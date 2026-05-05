/**
 * Result-related types — mirrors API.md §5.1, 5.5.
 * Source of truth: /API.md
 */

export type UnderstandingLevel = "high" | "medium" | "low";

export interface ScoreSummary {
  score_percentage: number;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  total_questions: number;
}

export interface ChartData {
  correct: number;
  wrong: number;
  unanswered: number;
}

export interface QuizSubmitResponse {
  quiz_id: string;
  score: ScoreSummary;
  time_taken_seconds: number;
  understanding_level: UnderstandingLevel;
  insight: string;
  recommendation: string;
  chart_data: ChartData;
  submitted_at: string;
}
