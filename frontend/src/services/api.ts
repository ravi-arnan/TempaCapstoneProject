/**
 * API client — single source of all backend HTTP access.
 * Implements the contract defined in API.md §10.
 *
 * Components MUST NOT call fetch() directly. Always go through this module.
 */

import type {
  QuizGenerateRequest,
  QuizGenerateResponse,
  QuizSubmitRequest,
} from "@/types/quiz";
import type { QuizSubmitResponse } from "@/types/result";
import type { ApiError } from "@/types/api";
import { ApiException } from "@/types/api";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

async function postJson<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiException(
      { detail: "Koneksi terputus. Pastikan kamu terhubung ke internet." },
      0,
    );
  }

  if (!res.ok) {
    let errBody: ApiError;
    try {
      errBody = (await res.json()) as ApiError;
    } catch {
      errBody = { detail: "Terjadi kesalahan tak terduga." };
    }
    throw new ApiException(errBody, res.status);
  }

  return (await res.json()) as TRes;
}

async function getJson<TRes>(path: string): Promise<TRes> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { method: "GET" });
  } catch {
    throw new ApiException(
      { detail: "Koneksi terputus. Pastikan kamu terhubung ke internet." },
      0,
    );
  }

  if (!res.ok) {
    let errBody: ApiError;
    try {
      errBody = (await res.json()) as ApiError;
    } catch {
      errBody = { detail: "Terjadi kesalahan tak terduga." };
    }
    throw new ApiException(errBody, res.status);
  }

  return (await res.json()) as TRes;
}

// ============================================================================
// Public API
// ============================================================================

export interface HealthResponse {
  status: "ok";
  version: string;
}

export function checkHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/health");
}

export function generateQuiz(
  req: QuizGenerateRequest,
): Promise<QuizGenerateResponse> {
  return postJson<QuizGenerateRequest, QuizGenerateResponse>(
    "/quiz/generate",
    req,
  );
}

export function submitQuiz(
  req: QuizSubmitRequest,
): Promise<QuizSubmitResponse> {
  return postJson<QuizSubmitRequest, QuizSubmitResponse>("/quiz/submit", req);
}
