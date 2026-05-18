import type { Answer } from "@/types/quiz";
import { cn } from "@/lib/cn";

interface QuestionPillsProps {
  answers: Answer[];
  currentIndex: number;
  onJump: (index: number) => void;
}

/**
 * Compact pills showing per-question status: answered / current / pending.
 * Clicking a pill jumps to that question. Lives in the sticky quiz header.
 */
export function QuestionPills({ answers, currentIndex, onJump }: QuestionPillsProps) {
  return (
    <div
      role="navigation"
      aria-label="Navigasi soal"
      className="flex flex-wrap items-center gap-1.5"
    >
      {answers.map((a, i) => {
        const answered = a.selected_option_index !== null;
        const isCurrent = i === currentIndex;
        return (
          <button
            key={a.question_id}
            type="button"
            onClick={() => onJump(i)}
            aria-label={`Soal ${i + 1}${answered ? ", terjawab" : ""}`}
            aria-current={isCurrent ? "step" : undefined}
            className={cn(
              "inline-flex h-7 w-7 items-center justify-center rounded-full font-mono text-[11px] font-medium transition-all",
              isCurrent
                ? "bg-text-primary text-bg-page ring-2 ring-brand-accent ring-offset-2 ring-offset-bg-page"
                : answered
                  ? "bg-brand-button text-white hover:opacity-90"
                  : "border border-border-prominent bg-bg-page text-text-muted hover:border-text-muted hover:text-text-primary",
            )}
          >
            {i + 1}
          </button>
        );
      })}
    </div>
  );
}
