import type { ScoreSummary } from "@/types/result";
import { STAT_LABELS, formatSeconds } from "@/utils/i18n";

interface ResultSummaryProps {
  score: ScoreSummary;
  timeTakenSeconds: number;
}

/**
 * Three-stat summary block: SKOR / WAKTU / BENAR.
 * Used at the top of the result page.
 */
export function ResultSummary({ score, timeTakenSeconds }: ResultSummaryProps) {
  return (
    <div className="flex flex-wrap gap-8 border-t border-border-subtle pt-4">
      <Stat label={STAT_LABELS.score} value={`${score.score_percentage}%`} />
      <Stat label={STAT_LABELS.time} value={formatSeconds(timeTakenSeconds)} />
      <Stat
        label={STAT_LABELS.correct}
        value={`${score.correct_count}/${score.total_questions}`}
      />
    </div>
  );
}

interface StatProps {
  label: string;
  value: string;
}

function Stat({ label, value }: StatProps) {
  return (
    <div>
      <div className="text-3xl font-medium leading-none text-text-primary">
        {value}
      </div>
      <div className="mt-1 font-mono text-[10px] font-medium uppercase tracking-[1.2px] text-text-muted">
        {label}
      </div>
    </div>
  );
}
