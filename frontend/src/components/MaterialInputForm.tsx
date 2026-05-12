import { useRef, useState } from "react";
import type { SourceType } from "@/types/quiz";
import { EMPTY_STATES, BUTTON_LABELS } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface MaterialInputFormProps {
  sourceType: SourceType;
  onSubmitText: (materialText: string) => void;
  onSubmitUrl: (url: string) => void;
  onSubmitPdf: (file: File) => void;
  isSubmitting?: boolean;
  loadingMessage?: string;
  error?: string | null;
}

const MAX_PDF_BYTES = 10 * 1024 * 1024; // 10 MB

/**
 * Material input form supporting 3 source types: text, URL, PDF.
 * Renders the appropriate input based on `sourceType`.
 */
export function MaterialInputForm({
  sourceType,
  onSubmitText,
  onSubmitUrl,
  onSubmitPdf,
  isSubmitting,
  loadingMessage,
  error,
}: MaterialInputFormProps) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Per-source validation
  const trimmedText = text.trim();
  const textValid = trimmedText.length >= 100;
  const textTooShort = trimmedText.length > 0 && trimmedText.length < 100;

  const trimmedUrl = url.trim();
  const urlValid =
    trimmedUrl.startsWith("http://") || trimmedUrl.startsWith("https://");

  const pdfValid = pdfFile !== null;

  const canSubmit =
    !isSubmitting &&
    ((sourceType === "text" && textValid) ||
      (sourceType === "url" && urlValid) ||
      (sourceType === "pdf" && pdfValid));

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    if (sourceType === "text") onSubmitText(trimmedText);
    else if (sourceType === "url") onSubmitUrl(trimmedUrl);
    else if (sourceType === "pdf" && pdfFile) onSubmitPdf(pdfFile);
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setPdfError(null);
    const file = e.target.files?.[0] ?? null;
    if (!file) {
      setPdfFile(null);
      return;
    }
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setPdfError("File harus berformat .pdf");
      setPdfFile(null);
      return;
    }
    if (file.size > MAX_PDF_BYTES) {
      setPdfError("File terlalu besar. Maksimal 10 MB.");
      setPdfFile(null);
      return;
    }
    setPdfFile(file);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {sourceType === "text" && (
        <>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={EMPTY_STATES.materialPlaceholder}
            rows={10}
            className="w-full resize-y rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)] disabled:opacity-70"
            disabled={isSubmitting}
          />
          {!isSubmitting && !error && !textTooShort && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.materialHelp}</p>
          )}
          {textTooShort && !isSubmitting && (
            <p className="text-sm text-text-muted">
              {trimmedText.length} / 100 karakter (minimal)
            </p>
          )}
        </>
      )}

      {sourceType === "url" && (
        <>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={EMPTY_STATES.urlPlaceholder}
            className="w-full rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)] disabled:opacity-70"
            disabled={isSubmitting}
          />
          {!isSubmitting && !error && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.urlHelp}</p>
          )}
        </>
      )}

      {sourceType === "pdf" && (
        <>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={isSubmitting}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isSubmitting}
            className={cn(
              "flex w-full items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border-standard bg-bg-alt p-8 text-text-muted transition-colors hover:border-brand-accent hover:text-text-primary",
              "disabled:cursor-not-allowed disabled:opacity-60",
              pdfFile && "border-brand-accent text-text-primary",
            )}
          >
            {pdfFile ? (
              <span className="flex flex-col items-center gap-1">
                <span className="font-medium">{pdfFile.name}</span>
                <span className="text-xs text-text-muted">
                  {(pdfFile.size / 1024).toFixed(0)} KB · klik untuk ganti file
                </span>
              </span>
            ) : (
              <span className="flex flex-col items-center gap-1">
                <PdfUploadIcon />
                <span>{EMPTY_STATES.pdfDropzone}</span>
              </span>
            )}
          </button>
          {pdfError && <p className="text-sm text-status-rendah">{pdfError}</p>}
          {!isSubmitting && !error && !pdfError && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.pdfHelp}</p>
          )}
        </>
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

function PulsingDot() {
  return (
    <span className="relative inline-flex h-3 w-3 flex-shrink-0">
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-button opacity-60" />
      <span className="relative inline-flex h-3 w-3 rounded-full bg-brand-button" />
    </span>
  );
}

function PdfUploadIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8"
      aria-hidden="true"
    >
      <path d="M5 4 H14 L19 9 V20 H5 Z" />
      <path d="M14 4 V9 H19" />
      <path d="M9 14 L12 11 L15 14" />
      <path d="M12 11 V18" />
    </svg>
  );
}
