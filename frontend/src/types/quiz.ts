/**
 * Quiz-related types — mirrors API.md §5.2-5.4.
 * Source of truth: /API.md
 */

export type QuestionType = "multiple_choice" | "true_false" | "short_answer";

export interface Question {
  id: number;
  type: QuestionType;
  question: string;
  options: string[] | null;
}

export interface Answer {
  question_id: number;
  selected_option_index: number | null;
  text_answer: string | null;
}

// §4.3 Quiz settings (pre-generate)
export type QuestionCount = 3 | 5 | 7 | 10;
export type Difficulty = "easy" | "medium" | "hard";

export interface QuizSettings {
  num_questions: QuestionCount;
  difficulty: Difficulty;
  shuffle_options: boolean;
}

export const DEFAULT_QUIZ_SETTINGS: QuizSettings = {
  num_questions: 5,
  difficulty: "medium",
  shuffle_options: true,
};

export interface QuizGenerateRequest {
  material_text: string;
  num_questions?: QuestionCount;
  difficulty?: Difficulty;
  shuffle_options?: boolean;
}

export interface QuizGenerateFromUrlRequest {
  url: string;
  num_questions?: QuestionCount;
  difficulty?: Difficulty;
  shuffle_options?: boolean;
}

export type SourceType = "text" | "url" | "pdf";

export interface QuizGenerateResponse {
  quiz_id: string;
  questions: Question[];
  total_questions: number;
  generated_at: string;
  difficulty?: Difficulty;
}

export interface QuizSubmitRequest {
  quiz_id: string;
  answers: Answer[];
  time_taken_seconds: number;
}
