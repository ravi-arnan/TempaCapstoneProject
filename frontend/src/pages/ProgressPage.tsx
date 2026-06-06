import { Link } from "react-router-dom";
import { TrendingUp } from "lucide-react";
import { ScoreTrendChart } from "@/components/ScoreTrendChart";
import { TopicMasteryList } from "@/components/TopicMasteryList";
import { useGamificationAnalytics } from "@/hooks/useGamificationAnalytics";
import type { GamificationAnalytics } from "@/types/gamification";
import { PROGRESS_PAGE } from "@/utils/i18n";

/**
 * Progress dashboard: score trend + per-topic mastery (Gamification Fase 3).
 * Owner: Ravi. Degrades gracefully when gamification is unavailable (503).
 */
export function ProgressPage() {
  const state = useGamificationAnalytics();

  if (state.status === "loading") {
    return (
      <p className="py-16 text-center text-sm text-text-muted">
        {PROGRESS_PAGE.loading}
      </p>
    );
  }

  if (state.status === "unavailable") {
    return (
      <MessageCard
        title={PROGRESS_PAGE.unavailableTitle}
        body={PROGRESS_PAGE.unavailableBody}
      />
    );
  }

  const { data } = state;
  if (data.quiz_count === 0) {
    return (
      <MessageCard title={PROGRESS_PAGE.emptyTitle} body={PROGRESS_PAGE.emptyBody}>
        <Link
          to="/"
          className="rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover"
        >
          {PROGRESS_PAGE.emptyCta}
        </Link>
      </MessageCard>
    );
  }

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <div className="flex items-center gap-2 text-brand-green">
          <TrendingUp className="h-5 w-5" aria-hidden="true" />
          <span className="font-mono text-[11px] uppercase tracking-[1.2px]">
            {PROGRESS_PAGE.title}
          </span>
        </div>
        <h1 className="text-4xl font-medium leading-tight tracking-tight text-text-primary">
          {PROGRESS_PAGE.title}
        </h1>
        <p className="text-lg text-text-secondary">{PROGRESS_PAGE.subtitle}</p>
      </header>

      <AnalyticsSummary data={data} />
      <ScoreTrendChart points={data.score_trend} />
      <TopicMasteryList items={data.topic_mastery} />
    </div>
  );
}

function AnalyticsSummary({ data }: { data: GamificationAnalytics }) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <StatTile label={PROGRESS_PAGE.summaryQuizzes} value={data.quiz_count} />
      <StatTile label={PROGRESS_PAGE.summaryAvg} value={data.average_score} />
      <StatTile label={PROGRESS_PAGE.summaryXp} value={data.total_xp} />
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-border-standard bg-bg-page p-4 shadow-level-1">
      <div className="font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
        {label}
      </div>
      <div className="mt-1 text-2xl font-medium tabular-nums text-text-primary">
        {value}
      </div>
    </div>
  );
}

function MessageCard({
  title,
  body,
  children,
}: {
  title: string;
  body: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="mx-auto max-w-md space-y-4 rounded-2xl border border-border-standard bg-bg-page p-8 text-center shadow-level-1">
      <h1 className="text-2xl font-medium text-text-primary">{title}</h1>
      <p className="text-text-secondary">{body}</p>
      {children && <div className="flex justify-center pt-2">{children}</div>}
    </div>
  );
}
