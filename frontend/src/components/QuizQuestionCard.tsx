import type { Question } from "@/types/quiz";
import { cn } from "@/lib/cn";

interface QuizQuestionCardProps {
  question: Question;
  index: number;
  total: number;
  selectedOptionIndex: number | null;
  onSelect: (optionIndex: number) => void;
}

/**
 * Single-question card with 4 selectable options.
 * Owner: Ravi. Wired up by QuizPage.
 */
export function QuizQuestionCard({
  question,
  index,
  total,
  selectedOptionIndex,
  onSelect,
}: QuizQuestionCardProps) {
  return (
    <div className="rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-1">
      <div className="mb-2 font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
        Soal {index + 1} / {total}
      </div>
      <h3 className="mb-6 text-xl font-medium leading-snug text-text-primary">
        {question.question}
      </h3>
      <div className="space-y-2">
        {question.options.map((option, i) => {
          const isSelected = selectedOptionIndex === i;
          return (
            <button
              key={i}
              type="button"
              onClick={() => onSelect(i)}
              className={cn(
                "w-full rounded-xl border px-4 py-3 text-left text-sm transition-colors",
                isSelected
                  ? "border-brand-accent bg-bg-alt text-text-primary"
                  : "border-border-standard bg-bg-page text-text-primary hover:bg-bg-alt",
              )}
            >
              <span className="mr-3 font-mono text-xs font-medium text-text-muted">
                {String.fromCharCode(65 + i)}
              </span>
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}
