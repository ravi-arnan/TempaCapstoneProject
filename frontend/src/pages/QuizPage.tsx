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

  const answeredCount = answers.filter(
    (a) => a.selected_option_index !== null,
  ).length;
  const allAnswered = answeredCount === quiz.total_questions;
  const progressPercent = (answeredCount / quiz.total_questions) * 100;

  return (
    <div className="space-y-6 pb-32">
      {/* Sticky header: title + timer + progress bar */}
      <div className="sticky top-0 z-10 -mx-6 bg-bg-page/80 px-6 py-3 backdrop-blur-sm sm:-mx-0 sm:rounded-xl sm:border sm:border-border-standard sm:bg-bg-page sm:px-4 sm:shadow-level-1">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-xl font-medium tracking-tight text-text-primary sm:text-2xl">
            Kuis sedang berlangsung
          </h1>
          <QuizTimer seconds={seconds} />
        </div>

        <div className="mt-3 space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-mono uppercase tracking-[1.2px] text-text-muted">
              {answeredCount} / {quiz.total_questions} terjawab
            </span>
            <span className="font-mono tabular-nums text-text-secondary">
              {Math.round(progressPercent)}%
            </span>
          </div>
          <div className="h-1 w-full overflow-hidden rounded-full bg-bg-subtle">
            <div
              className="h-full bg-brand-button transition-all duration-300 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
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
        <p className="rounded-xl border border-status-rendah bg-bg-alt p-3 text-sm text-status-rendah">
          {getErrorMessage(submitError.code, submitError.message)}
        </p>
      )}

      {/* Sticky bottom submit bar */}
      <div className="fixed inset-x-0 bottom-0 z-10 border-t border-border-standard bg-bg-page/95 px-6 py-4 backdrop-blur-sm shadow-level-3">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-text-muted">
            {allAnswered
              ? "Semua soal sudah terjawab"
              : `Sisa ${quiz.total_questions - answeredCount} soal`}
          </p>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting || !allAnswered}
            className="rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Menganalisis hasil..." : BUTTON_LABELS.submitQuiz}
          </button>
        </div>
      </div>
    </div>
  );
}
