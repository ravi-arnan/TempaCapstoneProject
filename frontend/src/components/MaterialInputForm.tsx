import { useState } from "react";
import { EMPTY_STATES, BUTTON_LABELS } from "@/utils/i18n";

interface MaterialInputFormProps {
  onSubmit: (materialText: string) => void;
  isSubmitting?: boolean;
  error?: string | null;
}

/**
 * Homepage material input form.
 * Validates length client-side (mirrors API.md §7), shows error inline.
 */
export function MaterialInputForm({
  onSubmit,
  isSubmitting,
  error,
}: MaterialInputFormProps) {
  const [text, setText] = useState("");
  const trimmed = text.trim();
  const isTooShort = trimmed.length > 0 && trimmed.length < 100;
  const isEmpty = trimmed.length === 0;
  const canSubmit = !isSubmitting && !isEmpty && !isTooShort;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (canSubmit) onSubmit(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={EMPTY_STATES.materialPlaceholder}
        rows={10}
        className="w-full resize-y rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)]"
        disabled={isSubmitting}
      />
      <p className="text-sm text-text-muted">{EMPTY_STATES.materialHelp}</p>
      {error && <p className="text-sm text-status-rendah">{error}</p>}
      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? BUTTON_LABELS.homeLoading : BUTTON_LABELS.homePrimary}
      </button>
    </form>
  );
}
