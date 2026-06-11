/**
 * Asahi chatbot types — mirrors backend app/schemas/chat.py and docs/CHATBOT.md.
 * Interaction is button-based: `intent` is a closed union.
 */

import type { UnderstandingLevel } from "@/types/result";

export type ChatIntent =
  | "opening"
  | "weak_points"
  | "study_tips"
  | "encouragement";

export interface ChatContext {
  quiz_id?: string;
  score_percentage: number;
  understanding_level: UnderstandingLevel;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  weak_topics?: string[];
}

export interface ChatRequest {
  intent: ChatIntent;
  context: ChatContext;
}

export interface ChatResponse {
  reply: string;
}
