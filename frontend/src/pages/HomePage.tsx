import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { SourceTypeTabs } from "@/components/SourceTypeTabs";
import { useQuiz } from "@/hooks/useQuiz";
import type { SourceType } from "@/types/quiz";
import {
  HOMEPAGE,
  LOADING_PROGRESS_MESSAGES,
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
        <h1 className="text-5xl font-medium leading-[1.05] tracking-tight text-text-primary">
          {HOMEPAGE.hero}
        </h1>
        <p className="max-w-2xl text-lg text-text-secondary">
          {HOMEPAGE.subtitle}
        </p>
      </header>

      <div>
        <SourceTypeTabs
          value={sourceType}
          onChange={setSourceType}
          disabled={generating}
        />
      </div>

      <MaterialInputForm
        sourceType={sourceType}
        onSubmitText={async (text) => handleSubmit(await generateFromText(text))}
        onSubmitUrl={async (url) => handleSubmit(await generateFromUrl(url))}
        onSubmitPdf={async (file) => handleSubmit(await generateFromPdf(file))}
        isSubmitting={generating}
        loadingMessage={
          generating ? LOADING_PROGRESS_MESSAGES[loadingMessageIndex] : undefined
        }
        error={
          generateError
            ? getErrorMessage(generateError.code, generateError.message)
            : null
        }
      />
    </div>
  );
}
