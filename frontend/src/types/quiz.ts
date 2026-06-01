/**
 * Quiz-related types — mirrors API.md §5.2-5.4.
 * Source of truth: /API.md
 */

export interface Question {
  id: number;
  question: string;
  options: [string, string, string, string];
}

export interface Answer {
  question_id: number;
  selected_option_index: number | null;
}

export interface QuizGenerateRequest {
  material_text: string;
}

export interface QuizGenerateFromUrlRequest {
  url: string;
}

export type SourceType = "text" | "url" | "pdf";

export interface QuizGenerateResponse {
  quiz_id: string;
  questions: Question[];
  total_questions: number;
  generated_at: string;
}

export interface QuizSubmitRequest {
  quiz_id: string;
  answers: Answer[];
  time_taken_seconds: number;
}
