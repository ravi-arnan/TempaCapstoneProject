import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { AsahiChatWidget } from "@/components/AsahiChatWidget";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { SourceTypeTabs } from "@/components/SourceTypeTabs";
import { DailyChallengeCard } from "@/components/DailyChallengeCard";
import { QuizGenerationSkeleton } from "@/components/QuizGenerationSkeleton";
import { QuizSettingsControl } from "@/components/QuizSettingsControl";
import { useQuiz } from "@/hooks/useQuiz";
import { useOnboardingTour } from "@/hooks/useOnboardingTour";
import { hasOnboarded } from "@/lib/onboarding";
import type { QuizSettings, SourceType } from "@/types/quiz";
import { DEFAULT_QUIZ_SETTINGS } from "@/types/quiz";
import {
  HOMEPAGE,
  LOADING_PROGRESS_MESSAGES,
  SAMPLE_MATERIALS,
  getErrorMessage,
} from "@/utils/i18n";

const MESSAGE_ROTATION_INTERVAL_MS = 3500;

/**
 * Home page: pick source (text/url/pdf), submit, generate quiz, navigate.
 * Owner: Ravi.
 */
export function HomePage() {
  const navigate = useNavigate();
  const {
    generateFromText,
    generateFromUrl,
    generateFromPdf,
    generating,
    generateError,
  } = useQuiz();

  const [sourceType, setSourceType] = useState<SourceType>("text");
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [prefillText, setPrefillText] = useState<string | null>(null);
  const [prefillUrl, setPrefillUrl] = useState<string | null>(null);
  const [settings, setSettings] = useState<QuizSettings>(DEFAULT_QUIZ_SETTINGS);

  // §4.6 Onboarding tour: auto-start on first visit, or when the nav "?" button
  // sends the user here with ?tour=1. Runs once per mount.
  const { startTour } = useOnboardingTour();
  const [searchParams, setSearchParams] = useSearchParams();
  const tourStartedRef = useRef(false);

  useEffect(() => {
    if (tourStartedRef.current) return;
    const forced = searchParams.get("tour") === "1";
    if (!forced && hasOnboarded()) return;

    tourStartedRef.current = true;
    if (forced) {
      // Drop the param so a refresh doesn't replay the tour.
      searchParams.delete("tour");
      setSearchParams(searchParams, { replace: true });
    }
    // Let the page paint (and lazy elements mount) before highlighting.
    const id = setTimeout(() => startTour(), 400);
    return () => clearTimeout(id);
  }, [searchParams, setSearchParams, startTour]);

  function handleSampleClick() {
    setSourceType("text");
    setPrefillText(SAMPLE_MATERIALS.fotosintesis.text);
  }

  function handleSmartUrlPaste(url: string) {
    setSourceType("url");
    setPrefillUrl(url);
  }

  // Rotate loading messages while generation runs (~9-25s typically).
  useEffect(() => {
    if (!generating) {
      setLoadingMessageIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setLoadingMessageIndex((i) =>
        Math.min(i + 1, LOADING_PROGRESS_MESSAGES.length - 1),
      );
    }, MESSAGE_ROTATION_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [generating]);

  async function handleSubmit(quiz: Awaited<ReturnType<typeof generateFromText>>) {
    if (quiz) {
      navigate("/quiz", { state: { quiz } });
    }
  }

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <h1 className="text-4xl font-medium leading-[1.05] tracking-tight text-text-primary sm:text-5xl">
          {HOMEPAGE.hero}
        </h1>
        <p className="max-w-2xl text-lg text-text-secondary">
          {HOMEPAGE.subtitle}
        </p>
      </header>

      <div data-tour="daily-challenge">
        <DailyChallengeCard />
      </div>

      <div data-tour="source-tabs" className="flex flex-wrap items-center gap-3">
        <SourceTypeTabs
          value={sourceType}
          onChange={setSourceType}
          disabled={generating}
        />
        {sourceType === "text" && !generating && (
          <button
            type="button"
            onClick={handleSampleClick}
            className="inline-flex min-h-[44px] items-center rounded-full border border-border-standard bg-bg-page px-4 py-2 text-sm text-text-secondary shadow-level-1 transition-colors hover:bg-bg-alt hover:text-text-primary active:bg-bg-alt"
          >
            {SAMPLE_MATERIALS.fotosintesis.label}
          </button>
        )}
      </div>

      <div data-tour="quiz-settings">
        <QuizSettingsControl
          settings={settings}
          onChange={setSettings}
          disabled={generating}
        />
      </div>

      <div data-tour="material-input">
      <MaterialInputForm
        sourceType={sourceType}
        onSubmitText={async (text) =>
          handleSubmit(await generateFromText(text, settings))
        }
        onSubmitUrl={async (url) =>
          handleSubmit(await generateFromUrl(url, settings))
        }
        onSubmitPdf={async (file) =>
          handleSubmit(await generateFromPdf(file, settings))
        }
        isSubmitting={generating}
        loadingMessage={
          generating ? LOADING_PROGRESS_MESSAGES[loadingMessageIndex] : undefined
        }
        error={
          generateError
            ? getErrorMessage(generateError.code, generateError.message)
            : null
        }
        prefillText={prefillText}
        prefillUrl={prefillUrl}
        onSmartUrlPaste={handleSmartUrlPaste}
      />
      </div>

      {generating && <QuizGenerationSkeleton />}

      <AsahiChatWidget />
    </div>
  );
}
