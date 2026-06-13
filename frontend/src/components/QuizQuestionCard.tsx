import type { Question } from "@/types/quiz";
import { QUIZ_PAGE } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface QuizQuestionCardProps {
  question: Question;
  index: number;
  total: number;
  selectedOptionIndex: number | null;
  textAnswer?: string | null;
  isCurrent?: boolean;
  onSelect: (optionIndex: number) => void;
  onTextChange?: (text: string) => void;
  onFocus?: () => void;
}

/**
 * Single-question card with 4 selectable options.
 * `isCurrent` adds a subtle highlight to indicate this card is the target
 * for keyboard shortcuts (1-4 keys).
 */
export function QuizQuestionCard({
  question,
  index,
  total,
  selectedOptionIndex,
  textAnswer,
  isCurrent,
  onSelect,
  onTextChange,
  onFocus,
}: QuizQuestionCardProps) {
  return (
    <div
      data-question-index={index}
      onClick={onFocus}
      className={cn(
        "rounded-2xl border bg-bg-page p-6 shadow-level-1 transition-colors",
        isCurrent
          ? "border-brand-accent ring-1 ring-brand-accent/40"
          : "border-border-standard",
      )}
    >
      <div className="mb-2 font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
        {QUIZ_PAGE.questionLabelTemplate(index, total)}
      </div>
      <h3 className="mb-6 text-xl font-medium leading-snug text-text-primary">
        {question.question}
      </h3>
      <div className="space-y-2">
        {question.type === "short_answer" ? (
          <input
            type="text"
            value={textAnswer ?? ""}
            onChange={(e) => onTextChange?.(e.target.value)}
            placeholder="Ketik jawaban kamu di sini..."
            className={cn(
              "w-full rounded-xl border px-4 py-3 text-sm transition-colors",
              "border-border-standard bg-bg-page text-text-primary focus:border-brand-accent focus:outline-none focus:ring-1 focus:ring-brand-accent/40"
            )}
          />
        ) : (
          question.options?.map((option, i) => {
            const isSelected = selectedOptionIndex === i;
            return (
              <button
                key={i}
                type="button"
                onClick={() => onSelect(i)}
                className={cn(
                  "w-full rounded-xl border px-4 py-3 text-left text-sm transition-colors active:bg-bg-alt",
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
          })
        )}
      </div>
    </div>
  );
}
