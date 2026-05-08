import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { useQuiz } from "@/hooks/useQuiz";
import {
  HOMEPAGE,
  LOADING_PROGRESS_MESSAGES,
  getErrorMessage,
} from "@/utils/i18n";

const MESSAGE_ROTATION_INTERVAL_MS = 3500;

/**
 * Home page: paste material → generate quiz → navigate to /quiz.
 * Owner: Ravi.
 */
export function HomePage() {
  const navigate = useNavigate();
  const { generate, generating, generateError } = useQuiz();
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  // Rotate loading messages while DL inference runs (~9-15s typically).
  // Stays on the last message if generation takes longer than expected.
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

  async function handleSubmit(materialText: string) {
    const quiz = await generate(materialText);
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

      <MaterialInputForm
        onSubmit={handleSubmit}
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
