/**
 * Gamification types — mirror backend/app/schemas/gamification.py.
 */

export interface GamificationStats {
  total_xp: number;
  level: number;
  xp_into_level: number;
  xp_for_next_level: number;
  current_streak: number;
  longest_streak: number;
}

export interface Badge {
  code: string;
  label: string;
  description: string;
  icon: string; // Lucide icon name
  unlocked_at: string | null;
}

export interface RecordAttemptResult {
  xp_earned: number;
  leveled_up: boolean;
  new_level: number;
  stats: GamificationStats;
  newly_unlocked: Badge[];
}

export interface HistoryItem {
  quiz_id: string;
  score: number;
  understanding_level: string;
  xp_earned: number;
  completed_at: string;
  topic?: string | null;
}

export interface HistorySummary {
  total_quizzes: number;
  average_score: number;
  total_xp: number;
  best_score: number;
  worst_score: number;
  most_recent_topic?: string | null;
}

export interface TrendPoint {
  date: string;
  average_score: number;
  attempt_count: number;
}

export interface TopicMasteryItem {
  topic: string;
  average_score: number;
  attempt_count: number;
}

export interface GamificationAnalytics {
  quiz_count: number;
  average_score: number;
  total_xp: number;
  score_trend: TrendPoint[];
  topic_mastery: TopicMasteryItem[];
}
