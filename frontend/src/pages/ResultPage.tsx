import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { InsightCard } from "@/components/InsightCard";
import { RecommendationCard } from "@/components/RecommendationCard";
import { ResultSummary } from "@/components/ResultSummary";
import { ScoreChart } from "@/components/ScoreChart";
import { UnderstandingBadge } from "@/components/UnderstandingBadge";
import type { QuizSubmitResponse } from "@/types/result";
import { BUTTON_LABELS, RESULT_HEADERS } from "@/utils/i18n";

interface ResultPageState {
  result: QuizSubmitResponse;
}

/**
 * Result page: display score, level, insight, recommendation, and chart.
 * Owner: Ravi.
 */
export function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as ResultPageState | null;
  const result = state?.result;

  useEffect(() => {
    if (!result) {
      navigate("/", { replace: true });
    }
  }, [result, navigate]);

  if (!result) return null;

  const headers = RESULT_HEADERS[result.understanding_level];

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <UnderstandingBadge level={result.understanding_level} />
        <h1 className="text-4xl font-medium leading-tight tracking-tight text-text-primary">
          {headers.headline}
        </h1>
        <p className="text-lg text-text-secondary">{headers.subhead}</p>
      </header>

      <ResultSummary
        score={result.score}
        timeTakenSeconds={result.time_taken_seconds}
      />

      <div className="grid gap-4 md:grid-cols-2">
        <InsightCard insight={result.insight} />
        <RecommendationCard recommendation={result.recommendation} />
      </div>

      <ScoreChart data={result.chart_data} />

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => navigate("/", { replace: true })}
          className="rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover"
        >
          {BUTTON_LABELS.resultRetry}
        </button>
        <button
          type="button"
          onClick={() => navigate("/", { replace: true })}
          className="rounded-md border border-transparent bg-transparent px-4 py-2 text-sm font-medium text-text-primary hover:bg-[var(--hover-tint)]"
        >
          {BUTTON_LABELS.backToHome}
        </button>
      </div>
    </div>
  );
}
