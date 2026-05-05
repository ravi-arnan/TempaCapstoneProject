import { useCallback, useState } from "react";
import { generateQuiz, submitQuiz } from "@/services/api";
import type {
  QuizGenerateResponse,
  QuizSubmitRequest,
} from "@/types/quiz";
import type { QuizSubmitResponse } from "@/types/result";
import { ApiException } from "@/types/api";

interface UseQuizState {
  generating: boolean;
  submitting: boolean;
  generateError: ApiException | null;
  submitError: ApiException | null;
}

/**
 * Hook for orchestrating the generate + submit flow.
 * Owns the loading/error states; pages own the navigation between them.
 */
export function useQuiz() {
  const [state, setState] = useState<UseQuizState>({
    generating: false,
    submitting: false,
    generateError: null,
    submitError: null,
  });

  const generate = useCallback(
    async (materialText: string): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await generateQuiz({ material_text: materialText });
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        const apiErr =
          err instanceof ApiException
            ? err
            : new ApiException({ detail: "Terjadi kesalahan tak terduga." }, 0);
        setState((s) => ({ ...s, generating: false, generateError: apiErr }));
        return null;
      }
    },
    [],
  );

  const submit = useCallback(
    async (req: QuizSubmitRequest): Promise<QuizSubmitResponse | null> => {
      setState((s) => ({ ...s, submitting: true, submitError: null }));
      try {
        const res = await submitQuiz(req);
        setState((s) => ({ ...s, submitting: false }));
        return res;
      } catch (err) {
        const apiErr =
          err instanceof ApiException
            ? err
            : new ApiException({ detail: "Terjadi kesalahan tak terduga." }, 0);
        setState((s) => ({ ...s, submitting: false, submitError: apiErr }));
        return null;
      }
    },
    [],
  );

  return {
    ...state,
    generate,
    submit,
  };
}
