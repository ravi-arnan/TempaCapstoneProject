import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { QuizQuestionCard } from "@/components/QuizQuestionCard";
import { QuizTimer } from "@/components/QuizTimer";
import { useQuiz } from "@/hooks/useQuiz";
import { useTimer } from "@/hooks/useTimer";
import type { Answer, QuizGenerateResponse } from "@/types/quiz";
import { BUTTON_LABELS, getErrorMessage } from "@/utils/i18n";

interface QuizPageState {
  quiz: QuizGenerateResponse;
}

/**
 * Quiz page: render questions, track answers, run timer, submit.
 * Owner: Ravi.
 */
export function QuizPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as QuizPageState | null;
  const quiz = state?.quiz;

  const { submit, submitting, submitError } = useQuiz();
  const { seconds, start, stop } = useTimer({ autoStart: true });

  const [answers, setAnswers] = useState<Answer[]>(() =>
    quiz
      ? quiz.questions.map((q) => ({
          question_id: q.id,
          selected_option_index: null,
        }))
      : [],
  );

  useEffect(() => {
    if (!quiz) {
      navigate("/", { replace: true });
    }
  }, [quiz, navigate]);

  if (!quiz) return null;

  function handleSelect(questionIndex: number, optionIndex: number) {
    setAnswers((prev) =>
      prev.map((a, i) =>
        i === questionIndex ? { ...a, selected_option_index: optionIndex } : a,
      ),
    );
  }

  async function handleSubmit() {
    if (!quiz) return;
    stop();
    const result = await submit({
      quiz_id: quiz.quiz_id,
      answers,
      time_taken_seconds: seconds,
    });
    if (result) {
      navigate("/result", { state: { result } });
    } else {
      start();
    }
  }

  const allAnswered = answers.every((a) => a.selected_option_index !== null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-medium tracking-tight text-text-primary">
          Kuis sedang berlangsung
        </h1>
        <QuizTimer seconds={seconds} />
      </div>

      <div className="space-y-4">
        {quiz.questions.map((question, i) => (
          <QuizQuestionCard
            key={question.id}
            question={question}
            index={i}
            total={quiz.total_questions}
            selectedOptionIndex={answers[i]?.selected_option_index ?? null}
            onSelect={(opt) => handleSelect(i, opt)}
          />
        ))}
      </div>

      {submitError && (
        <p className="text-sm text-status-rendah">
          {getErrorMessage(submitError.code, submitError.message)}
        </p>
      )}

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={submitting || !allAnswered}
          className="rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Menganalisis hasil..." : BUTTON_LABELS.submitQuiz}
        </button>
      </div>
    </div>
  );
}
