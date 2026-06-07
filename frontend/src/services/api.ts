/**
 * API client — single source of all backend HTTP access.
 * Implements the contract defined in API.md §10.
 *
 * Components MUST NOT call fetch() directly. Always go through this module.
 */

import type {
  QuizGenerateFromUrlRequest,
  QuizGenerateRequest,
  QuizGenerateResponse,
  QuizSubmitRequest,
} from "@/types/quiz";
import type { QuizSubmitResponse } from "@/types/result";
import type { ApiError } from "@/types/api";
import { ApiException } from "@/types/api";
import type {
  Badge,
  GamificationStats,
  GamificationAnalytics,
  HistoryResponse,
  RecordAttemptResult,
} from "@/types/gamification";
import type { AuthUser } from "@/types/auth";
import { getDeviceId, setDeviceId } from "@/lib/deviceId";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

// Default timeout for most endpoints
const DEFAULT_TIMEOUT_MS = 10_000;

// Quiz generation goes through DL inference (HF Space) and can take 6-15s
// for a normal quiz, longer if Space is cold-starting (~30s).
// 90s gives safe headroom without making users wait absurdly long.
const QUIZ_GENERATE_TIMEOUT_MS = 90_000;

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errBody: ApiError;
    try {
      errBody = (await res.json()) as ApiError;
    } catch {
      errBody = { detail: "Terjadi kesalahan tak terduga." };
    }
    throw new ApiException(errBody, res.status);
  }
  return (await res.json()) as T;
}

function networkErrorToApiException(err: unknown): ApiException {
  if (err instanceof DOMException && err.name === "AbortError") {
    return new ApiException(
      {
        detail:
          "Permintaan terlalu lama. Coba lagi sebentar, sistem sedang menyiapkan model.",
        code: "TIMEOUT",
      },
      408,
    );
  }
  return new ApiException(
    { detail: "Koneksi terputus. Pastikan kamu terhubung ke internet." },
    0,
  );
}

async function postJson<TReq, TRes>(
  path: string,
  body: TReq,
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<TRes> {
  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}${path}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      timeoutMs,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<TRes>(res);
}

async function getJson<TRes>(
  path: string,
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<TRes> {
  let res: Response;
  try {
    res = await fetchWithTimeout(`${BASE_URL}${path}`, { method: "GET" }, timeoutMs);
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<TRes>(res);
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
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}

export function generateQuizFromUrl(
  req: QuizGenerateFromUrlRequest,
): Promise<QuizGenerateResponse> {
  return postJson<QuizGenerateFromUrlRequest, QuizGenerateResponse>(
    "/quiz/generate-from-url",
    req,
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}

export async function generateQuizFromPdf(
  file: File,
): Promise<QuizGenerateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}/quiz/generate-from-pdf`,
      { method: "POST", body: formData },
      QUIZ_GENERATE_TIMEOUT_MS,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<QuizGenerateResponse>(res);
}

export function submitQuiz(
  req: QuizSubmitRequest,
): Promise<QuizSubmitResponse> {
  return postJson<QuizSubmitRequest, QuizSubmitResponse>("/quiz/submit", req);
}

// ============================================================================
// Auth — Google login. Throws ApiException on failure (caller handles it).
// ============================================================================

/**
 * Verify a Google ID token (credential) with the backend and link/create the
 * account. The caller's current anonymous device id is sent so guest progress
 * carries over; on success the client adopts the returned canonical device id.
 */
export async function loginWithGoogle(credential: string): Promise<AuthUser> {
  const user = await postJson<
    { credential: string; device_id: string },
    AuthUser
  >("/auth/google", { credential, device_id: getDeviceId() });
  setDeviceId(user.device_id);
  return user;
}

// ============================================================================
// Gamification — non-blocking. All methods return null on any failure
// (including 503 when DATABASE_URL is unset) so quiz UX is never blocked.
// ============================================================================

async function gamificationFetch<T>(
  path: string,
  init: RequestInit,
): Promise<T | null> {
  try {
    const res = await fetchWithTimeout(
      `${BASE_URL}${path}`,
      {
        ...init,
        headers: { ...init.headers, "X-Device-Id": getDeviceId() },
      },
      DEFAULT_TIMEOUT_MS,
    );
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export function getGamificationStats(): Promise<GamificationStats | null> {
  return gamificationFetch<GamificationStats>("/gamification/stats", {
    method: "GET",
  });
}

export function recordQuizAttempt(body: {
  quiz_id: string;
  score: number;
  understanding_level: string;
}): Promise<RecordAttemptResult | null> {
  return gamificationFetch<RecordAttemptResult>("/gamification/record-attempt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

/**
 * Quiz history (summary + items). Returns null when gamification is unavailable
 * (503 / network failure) so the History page can show a graceful "off" state.
 */
export function getGamificationHistory(
  limit = 10,
): Promise<HistoryResponse | null> {
  return gamificationFetch<HistoryResponse>(
    `/gamification/history?limit=${limit}`,
    { method: "GET" },
  );
}

export async function getGamificationAnalytics(): Promise<GamificationAnalytics | null> {
  return gamificationFetch<GamificationAnalytics>("/gamification/analytics", {
    method: "GET",
  });
}

export async function getAchievements(): Promise<Badge[]> {
  const res = await gamificationFetch<Badge[]>("/gamification/achievements", {
    method: "GET",
  });
  return res ?? [];
}

export function regenerateQuiz(
  quizId: string,
): Promise<QuizGenerateResponse> {
  return postJson<{ quiz_id: string }, QuizGenerateResponse>(
    "/quiz/regenerate",
    { quiz_id: quizId },
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}
