import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ResultPage } from "@/pages/ResultPage";
import type { QuizSubmitResponse } from "@/types/result";
import type { RecordAttemptResult } from "@/types/gamification";
import { RESULT_HEADERS } from "@/utils/i18n";

vi.mock("@/services/api", () => ({
  regenerateQuiz: vi.fn(),
  submitQuiz: vi.fn(),
  generateQuiz: vi.fn(),
  generateQuizFromUrl: vi.fn(),
  generateQuizFromPdf: vi.fn(),
  getDailyChallenge: vi.fn(),
  recordQuizAttempt: vi.fn(),
}));

const result: QuizSubmitResponse = {
  quiz_id: "q1",
  score: {
    score_percentage: 60, // < 80 so no confetti fires in the test
    correct_count: 3,
    wrong_count: 2,
    unanswered_count: 0,
    total_questions: 5,
  },
  time_taken_seconds: 120,
  understanding_level: "medium",
  insight: "Pemahamanmu sebagian sudah terbentuk.",
  recommendation: "Baca ulang bagian yang masih ragu.",
  chart_data: { correct: 3, wrong: 2, unanswered: 0 },
  submitted_at: "2026-06-07T00:00:00Z",
  question_reviews: [
    {
      question_id: 1,
      question: "Apa itu fotosintesis?",
      options: ["A", "B", "C", "D"],
      selected_option_index: 0,
      correct_option_index: 0,
      is_correct: true,
      is_unanswered: false,
    },
  ],
};

const reward: RecordAttemptResult = {
  xp_earned: 40,
  leveled_up: true,
  new_level: 3,
  stats: {
    total_xp: 300,
    level: 3,
    xp_into_level: 0,
    xp_for_next_level: 100,
    current_streak: 1,
    longest_streak: 2,
  },
  newly_unlocked: [
    { code: "perfect_score", label: "Sempurna", description: "d", icon: "Star", unlocked_at: "2026-06-07T00:00:00Z" },
  ],
};

function renderResult(state: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/result", state }]}>
      <Routes>
        <Route path="/result" element={<ResultPage />} />
        <Route path="/" element={<div>home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ResultPage", () => {
  it("renders headline, insight, recommendation and the reward banner", () => {
    renderResult({ result, reward });
    expect(screen.getByText(RESULT_HEADERS.medium.headline)).toBeInTheDocument();
    expect(screen.getByText(result.insight)).toBeInTheDocument();
    expect(screen.getByText(result.recommendation)).toBeInTheDocument();
    expect(screen.getByText("+40 XP")).toBeInTheDocument(); // reward banner
    expect(screen.getByText("Sempurna")).toBeInTheDocument(); // unlocked badge
  });

  it("renders without a reward banner when reward is null", () => {
    renderResult({ result, reward: null });
    expect(screen.getByText(RESULT_HEADERS.medium.headline)).toBeInTheDocument();
    expect(screen.queryByText("+40 XP")).not.toBeInTheDocument();
  });
});
