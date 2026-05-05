import { useNavigate } from "react-router-dom";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { useQuiz } from "@/hooks/useQuiz";
import { HOMEPAGE, getErrorMessage } from "@/utils/i18n";

/**
 * Home page: paste material → generate quiz → navigate to /quiz.
 * Owner: Ravi.
 */
export function HomePage() {
  const navigate = useNavigate();
  const { generate, generating, generateError } = useQuiz();

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
        error={
          generateError ? getErrorMessage(generateError.code, generateError.message) : null
        }
      />
    </div>
  );
}
