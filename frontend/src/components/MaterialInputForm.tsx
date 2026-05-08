import { useState } from "react";
import { EMPTY_STATES, BUTTON_LABELS } from "@/utils/i18n";

interface MaterialInputFormProps {
  onSubmit: (materialText: string) => void;
  isSubmitting?: boolean;
  loadingMessage?: string;
  error?: string | null;
}

/**
 * Homepage material input form.
 * Validates length client-side (mirrors API.md §7), shows error inline.
 * During DL inference (~9-15s), shows rotating progress messages.
 */
export function MaterialInputForm({
  onSubmit,
  isSubmitting,
  loadingMessage,
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
        className="w-full resize-y rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)] disabled:opacity-70"
        disabled={isSubmitting}
      />

      {!isSubmitting && !error && (
        <p className="text-sm text-text-muted">{EMPTY_STATES.materialHelp}</p>
      )}

      {error && <p className="text-sm text-status-rendah">{error}</p>}

      {isSubmitting && loadingMessage && (
        <div
          className="flex items-center gap-3 rounded-xl border border-brand-accent bg-bg-alt p-4 shadow-level-1"
          role="status"
          aria-live="polite"
        >
          <PulsingDot />
          <p className="flex-1 text-sm font-medium text-text-primary">
            {loadingMessage}
          </p>
          <span className="font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
            Mohon tunggu
          </span>
        </div>
      )}

      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? BUTTON_LABELS.homeLoading : BUTTON_LABELS.homePrimary}
      </button>
    </form>
  );
}

/**
 * Subtle pulsing dot indicator — gentler than spinning loader.
 * Three concentric circles fade in/out at staggered intervals.
 */
function PulsingDot() {
  return (
    <span className="relative inline-flex h-3 w-3 flex-shrink-0">
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-button opacity-60" />
      <span className="relative inline-flex h-3 w-3 rounded-full bg-brand-button" />
    </span>
  );
}
