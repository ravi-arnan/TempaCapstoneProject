# API Contract — TempaCapstoneProject

**Project**: Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data
**Team**: TP-G005
**Status**: Draft v1.0 — needs team review before lock-in
**Last updated**: 2026-05-04

---

## 1. Overview

This document is the **single source of truth** for the HTTP contract between the React frontend and the Python backend. Any field added, renamed, or removed must be reflected here AND signed off by both sides before merging.

### Why this document exists
- Frontend (Ravi) and Backend (Audry / Ariq / Desta) work in parallel.
- The dependency chain is: `material_text → quiz → answers → result → display`. A drift in any shape blocks the whole chain.
- Discovering an API mismatch in Week 5 = demo failure. Locking the contract in Week 1 = predictable integration.

### Scope
- 5 endpoints (`/health`, `/quiz/generate`, `/quiz/generate-from-url`, `/quiz/generate-from-pdf`, `/quiz/submit`).
- All data shapes used in those endpoints.
- All error codes and validation rules.
- Side-by-side TypeScript + Pydantic models for shared types.

### Out of scope (NOT this document)
- Internal classification / insight / recommendation rule logic → see `CLASSIFICATION_RULES.md` (TBD).
- Architecture diagrams of internal modules → see `ARCHITECTURE.md` (TBD).
- Frontend component design → see `DESIGN.md`.

### Relationship to CLAUDE.md / PRD.md

The API sketches in `CLAUDE.md` §"API Contract Suggestions" and `PRD.md` were preliminary. **This document supersedes them.** Two intentional differences from those sketches — please review:

1. **`correct_answer` is no longer returned in the `/quiz/generate` response.**
   _Why_: returning correct answers to the client lets users see them in DevTools → Network tab. The correct answer is now stored server-side and used internally by `/quiz/submit`. See §8 for storage strategy.

2. **`selected_answer: "A"` → `selected_option_index: 0`** in `/quiz/submit` request.
   _Why_: integer index (0–3) is robust to display reordering and avoids letter-parsing on the backend. Frontend can map index → letter label for display only.

If the team prefers the original sketches, raise it in the §12 sign-off discussion **before** Audry/Ariq start implementing. Otherwise these changes are in effect.

---

## 2. Conventions

### Base URL
- **Development**: `http://localhost:8000`
- **Demo**: TBD (likely tunneled via `ngrok` or similar for the demo session)
- All endpoint paths in this document are **relative to base URL**.

### Content type
- All requests: `Content-Type: application/json`
- All responses: `Content-Type: application/json; charset=utf-8`

### HTTP methods
- `GET` for read-only operations
- `POST` for creating quizzes and submitting answers
- No `PUT`/`PATCH`/`DELETE` in MVP

### Status codes used

| Code | Meaning | When |
|---|---|---|
| `200 OK` | Success | All successful responses |
| `400 Bad Request` | Validation failure | Empty material, material too short, missing required field |
| `404 Not Found` | Resource missing | `quiz_id` not found at submit time |
| `422 Unprocessable Entity` | Schema validation failure | Pydantic-level type errors (FastAPI default) |
| `500 Internal Server Error` | Unexpected backend error | Any uncaught exception |

### Response envelope

**Success responses** return the resource directly (no envelope):
```json
{ "quiz_id": "...", "questions": [...] }
```

**Error responses** use a consistent error envelope:
```json
{
  "detail": "Human-readable error message in Indonesian by default",
  "code": "MATERIAL_TOO_SHORT"
}
```

- `detail`: localized message safe to show to users
- `code`: machine-readable error code (uppercase, snake-case, stable across versions)

> FastAPI default uses just `{"detail": "..."}` without `code`. We extend it with `code` for robust frontend error handling. Backend wraps all custom errors via a shared exception handler (see implementation note in §10).

### Localization
- API response **enum values** use lowercase English codes (`"high"`, `"medium"`, `"low"`) — language-agnostic.
- API response **display strings** (`insight`, `recommendation`, error `detail`) come in **Indonesian by default**.
- Future-proofing: `?lang=en` query param can be added later without breaking changes (out of scope for MVP).

### IDs
- `quiz_id`: UUID v4 string, e.g., `"550e8400-e29b-41d4-a716-446655440000"`
- `question.id`: simple integer (1-based) within a quiz, e.g., `1, 2, 3, ...`

### Time
- Always integer seconds (e.g., `time_taken_seconds: 120` = 2 minutes).
- All timestamps (if added later) use ISO 8601 UTC: `"2026-05-04T15:30:00Z"`.

---

## 3. Authentication

**MVP: no authentication.** All endpoints are open. This is consistent with the project scope — no user accounts, no persistent storage of user data.

If auth is added post-MVP, the convention will be: `Authorization: Bearer <token>` header. Reserve this header now; do not use it for other purposes.

---

## 4. Endpoints

### 4.1 Health check

```
GET /health
```

Returns backend liveness. Used by frontend to detect "backend is down" state and by demo runner to verify boot.

#### Response · 200 OK

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

#### Errors
None defined. Any non-200 = backend dead.

#### Example
```bash
curl http://localhost:8000/health
```

---

### 4.2 Generate quiz

```
POST /quiz/generate
```

Generates a multiple-choice quiz from learning material.

#### Request body

```json
{
  "material_text": "Fotosintesis adalah proses pembentukan glukosa..."
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `material_text` | string | yes | min 100 chars, max 20,000 chars; non-empty after trimming |

#### Response · 200 OK

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "id": 1,
      "question": "Apa peran utama klorofil dalam fotosintesis?",
      "options": [
        "Menyerap cahaya matahari",
        "Menghasilkan oksigen",
        "Menyimpan glukosa",
        "Memecah air"
      ]
    }
  ],
  "total_questions": 5,
  "generated_at": "2026-05-04T15:30:00Z"
}
```

| Field | Type | Notes |
|---|---|---|
| `quiz_id` | string (UUID) | Use this when calling `/quiz/submit` |
| `questions[]` | Question[] | 5–10 items in MVP |
| `questions[].id` | int | 1-based, sequential within this quiz |
| `questions[].question` | string | Question prompt in Indonesian |
| `questions[].options` | string[] | Always 4 options (A, B, C, D positions) |
| `total_questions` | int | Convenience count, equals `questions.length` |
| `generated_at` | string (ISO 8601) | UTC timestamp |

> **IMPORTANT — `correct_answer` is NOT exposed.**
> The correct answer is stored server-side keyed by `quiz_id`. Returning correct answers to the client would let users inspect the network tab and "win" trivially. This also keeps the request/response payload smaller.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `MATERIAL_EMPTY` | `material_text` is missing/empty/whitespace | "Materi tidak boleh kosong." |
| 400 | `MATERIAL_TOO_SHORT` | < 100 chars after trim | "Materi terlalu pendek. Minimal 100 karakter." |
| 400 | `MATERIAL_TOO_LONG` | > 20,000 chars | "Materi terlalu panjang. Maksimal 20.000 karakter." |
| 422 | (FastAPI auto) | wrong types, missing field | (FastAPI default body) |
| 500 | `QUIZ_GENERATION_FAILED` | Generator raises | "Gagal menghasilkan kuis. Silakan coba lagi." |

### Response time expectation

> ⚠️ **`POST /quiz/generate` is the slowest endpoint by design.**
> The DL model (fine-tuned IndoT5) runs inference on CPU (no GPU at runtime). Expected latency:
> - **Cold start** (first request after server boot): 25-50s — includes ~10s model load + ~15-40s generation
> - **Warm inference** (subsequent requests): 15-40s for 5 questions
> - **Per question**: 3-8s on typical CPU
>
> Frontend MUST show loading state with progress messages during this wait. See `BRAND.md` §7.3 for copy.
> Frontend timeout for this endpoint should be set to at least **60 seconds** to avoid spurious "connection lost" errors.
>
> All other endpoints (`/health`, `/quiz/submit`) respond in < 100ms.
>
> See `ML.md` §7 for full latency breakdown and optimization options.

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "material_text": "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di kloroplas dan menghasilkan oksigen sebagai produk samping..."
  }'
```

---

### 4.3 Generate quiz from URL

```
POST /quiz/generate-from-url
```

Fetches an article from a public URL, extracts the main text, then generates a quiz the same way as `/quiz/generate`.

#### Request body

```json
{
  "url": "https://contoh.com/artikel-pelajaran"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `url` | string | yes | must start with `http://` or `https://`; publicly reachable; HTML page (not PDF/binary) |

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response. The backend extracts the article text via `trafilatura` (with optional Playwright fallback for SPA/lazy-loaded pages), then applies the standard quiz pipeline.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `URL_INVALID` | not http(s) or malformed | "URL tidak valid. Pastikan dimulai dengan http:// atau https://" |
| 400 | `URL_FETCH_FAILED` | DNS/connection failure or non-200 status | "Gagal mengambil halaman dari URL." |
| 400 | `URL_EMPTY_CONTENT` | trafilatura returned nothing extractable | "Halaman tidak punya artikel yang bisa diambil." |
| 400 | `URL_TOO_SHORT` | extracted text < 100 chars | "Artikel di URL terlalu pendek." |
| 400 | `URL_TOO_LONG` | extracted text > 20,000 chars (auto-truncated, warning) | "Artikel terlalu panjang." |
| 500 | `QUIZ_GENERATION_FAILED` | downstream generator failure | "Gagal membuat kuis dari URL." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate-from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://id.wikipedia.org/wiki/Fotosintesis"}'
```

> **User-Agent**: backend sends `AsahlagiBot/1.0` when fetching pages, so server logs can identify the source.

---

### 4.4 Generate quiz from PDF

```
POST /quiz/generate-from-pdf
```

Accepts a PDF file upload, extracts text via `pdfplumber`, then generates a quiz.

#### Request body

`multipart/form-data` with one part:

| Field | Type | Required | Validation |
|---|---|---|---|
| `file` | binary PDF | yes | content-type `application/pdf`; file size ≤ 10 MB; PDF must contain extractable text (not scanned images) |

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `PDF_INVALID` | file is not a valid PDF | "File PDF tidak bisa diproses." |
| 400 | `PDF_EMPTY` | pdfplumber returns no text (scan or empty) | "PDF tidak punya teks yang bisa diekstrak." |
| 400 | `PDF_TOO_SHORT` | extracted text < 100 chars | "Teks PDF terlalu pendek." |
| 400 | `PDF_TOO_LONG` | extracted text > 20,000 chars (auto-truncated, warning) | "PDF terlalu panjang." |
| 413 | (FastAPI auto) | file > 10 MB | (FastAPI default body) |
| 500 | `QUIZ_GENERATION_FAILED` | downstream generator failure | "Gagal membuat kuis dari PDF." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate-from-pdf \
  -F "file=@/path/to/material.pdf"
```

---

### 4.5 Submit quiz

```
POST /quiz/submit
```

Submits user's answers and returns full result analysis.

#### Request body

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "answers": [
    { "question_id": 1, "selected_option_index": 0 },
    { "question_id": 2, "selected_option_index": 2 },
    { "question_id": 3, "selected_option_index": null }
  ],
  "time_taken_seconds": 245
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `quiz_id` | string (UUID) | yes | must match an existing generated quiz |
| `answers[]` | Answer[] | yes | length must equal `total_questions` from generate response |
| `answers[].question_id` | int | yes | must reference an existing question in the quiz |
| `answers[].selected_option_index` | int \| null | yes | 0–3 (matches `options` array index), or `null` for unanswered |
| `time_taken_seconds` | int | yes | ≥ 0, ≤ 7200 (2 hours sanity cap) |

> **Why `selected_option_index` (int 0–3) instead of `selected_answer` (string "A"–"D")?**
> Index is robust to display reordering and avoids parsing. Frontend can map index→letter label for display purposes only.

#### Response · 200 OK

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": {
    "score_percentage": 80,
    "correct_count": 4,
    "wrong_count": 1,
    "unanswered_count": 0,
    "total_questions": 5
  },
  "time_taken_seconds": 245,
  "understanding_level": "high",
  "insight": "Kamu memahami konsep utama materi dengan baik. Skor tinggi disertai waktu pengerjaan yang efisien menunjukkan pemahaman yang mantap.",
  "recommendation": "Lanjut ke materi berikutnya atau coba kuis dengan tingkat kesulitan lebih tinggi.",
  "chart_data": {
    "correct": 4,
    "wrong": 1,
    "unanswered": 0
  },
  "submitted_at": "2026-05-04T15:34:05Z"
}
```

| Field | Type | Notes |
|---|---|---|
| `quiz_id` | string | echoed back for client correlation |
| `score.score_percentage` | int | 0–100, rounded to nearest int |
| `score.correct_count` | int | 0 ≤ x ≤ total |
| `score.wrong_count` | int | 0 ≤ x ≤ total |
| `score.unanswered_count` | int | 0 ≤ x ≤ total |
| `score.total_questions` | int | matches generate-time count |
| `time_taken_seconds` | int | echoed from request |
| `understanding_level` | enum | `"high"` \| `"medium"` \| `"low"` (lowercase English code) |
| `insight` | string | Indonesian, 1–2 sentences |
| `recommendation` | string | Indonesian, 1–2 sentences, actionable |
| `chart_data` | object | numeric fields for direct chart consumption |
| `submitted_at` | string (ISO 8601) | UTC timestamp |

> **Frontend display tip**: map `understanding_level` to localized label using a lookup table:
> ```ts
> const LEVEL_LABEL: Record<UnderstandingLevel, { id: string; en: string }> = {
>   high:   { id: "Tinggi", en: "High" },
>   medium: { id: "Sedang", en: "Medium" },
>   low:    { id: "Rendah", en: "Low" }
> };
> ```

#### Invariants (must hold in every successful response)
1. `correct_count + wrong_count + unanswered_count === total_questions`
2. `score_percentage === round(correct_count / total_questions × 100)`
3. `chart_data.correct === score.correct_count`, same for wrong/unanswered
4. `total_questions` equals the number sent at generate time
5. `understanding_level` is one of the 3 enum values (never null, never empty string)

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `ANSWERS_LENGTH_MISMATCH` | `answers.length !== total_questions` | "Jumlah jawaban tidak sesuai dengan jumlah soal." |
| 400 | `INVALID_OPTION_INDEX` | option index out of range | "Pilihan jawaban tidak valid." |
| 400 | `INVALID_QUESTION_ID` | `question_id` not in quiz | "Soal tidak ditemukan dalam kuis." |
| 400 | `INVALID_TIME` | negative or > 7200 | "Waktu pengerjaan tidak valid." |
| 404 | `QUIZ_NOT_FOUND` | `quiz_id` doesn't exist | "Kuis tidak ditemukan atau sudah kedaluwarsa." |
| 422 | (FastAPI auto) | wrong types | (FastAPI default body) |
| 500 | `EVALUATION_FAILED` | evaluator/classifier raises | "Gagal menganalisis hasil kuis." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/submit \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
    "answers": [
      { "question_id": 1, "selected_option_index": 0 },
      { "question_id": 2, "selected_option_index": 2 },
      { "question_id": 3, "selected_option_index": 1 },
      { "question_id": 4, "selected_option_index": null },
      { "question_id": 5, "selected_option_index": 3 }
    ],
    "time_taken_seconds": 245
  }'
```

---

## 5. Shared Data Models

Side-by-side TypeScript interfaces (frontend) and Pydantic models (backend). **These two columns must stay in sync.** Any change requires updating both.

### 5.1 `UnderstandingLevel` (enum)

```ts
// frontend/src/types/result.ts
export type UnderstandingLevel = "high" | "medium" | "low";
```

```python
# backend/app/schemas/result.py
from enum import Enum

class UnderstandingLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### 5.2 `Question`

```ts
// frontend/src/types/quiz.ts
export interface Question {
  id: number;
  question: string;
  options: [string, string, string, string]; // exactly 4
}
```

```python
# backend/app/schemas/quiz.py
from pydantic import BaseModel, Field, conlist

class Question(BaseModel):
    id: int = Field(..., ge=1)
    question: str = Field(..., min_length=1)
    options: conlist(str, min_length=4, max_length=4)
```

> Backend stores a separate `QuestionInternal` that adds `correct_option_index: int` — that field never leaves the backend.

### 5.3 `Answer`

```ts
// frontend/src/types/quiz.ts
export interface Answer {
  question_id: number;
  selected_option_index: number | null; // 0-3 or null for unanswered
}
```

```python
# backend/app/schemas/quiz.py
from typing import Optional
from pydantic import BaseModel, Field

class Answer(BaseModel):
    question_id: int = Field(..., ge=1)
    selected_option_index: Optional[int] = Field(None, ge=0, le=3)
```

### 5.4 `QuizGenerateRequest` / `QuizGenerateResponse`

```ts
// frontend/src/types/quiz.ts
export interface QuizGenerateRequest {
  material_text: string;
}

export interface QuizGenerateResponse {
  quiz_id: string;
  questions: Question[];
  total_questions: number;
  generated_at: string; // ISO 8601 UTC
}
```

```python
# backend/app/schemas/quiz.py
from datetime import datetime

class QuizGenerateRequest(BaseModel):
    material_text: str = Field(..., min_length=100, max_length=20000)

class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: list[Question]
    total_questions: int
    generated_at: datetime
```

### 5.5 `QuizSubmitRequest` / `QuizSubmitResponse`

```ts
// frontend/src/types/quiz.ts
export interface QuizSubmitRequest {
  quiz_id: string;
  answers: Answer[];
  time_taken_seconds: number;
}

export interface ScoreSummary {
  score_percentage: number;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  total_questions: number;
}

export interface ChartData {
  correct: number;
  wrong: number;
  unanswered: number;
}

export interface QuizSubmitResponse {
  quiz_id: string;
  score: ScoreSummary;
  time_taken_seconds: number;
  understanding_level: UnderstandingLevel;
  insight: string;
  recommendation: string;
  chart_data: ChartData;
  submitted_at: string; // ISO 8601 UTC
}
```

```python
# backend/app/schemas/result.py
class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: list[Answer]
    time_taken_seconds: int = Field(..., ge=0, le=7200)

class ScoreSummary(BaseModel):
    score_percentage: int = Field(..., ge=0, le=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    unanswered_count: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=1)

class ChartData(BaseModel):
    correct: int
    wrong: int
    unanswered: int

class QuizSubmitResponse(BaseModel):
    quiz_id: str
    score: ScoreSummary
    time_taken_seconds: int
    understanding_level: UnderstandingLevel
    insight: str
    recommendation: str
    chart_data: ChartData
    submitted_at: datetime
```

### 5.6 `ApiError` (error response shape)

```ts
// frontend/src/types/api.ts
export interface ApiError {
  detail: string;
  code?: string; // optional — present on backend-defined errors, absent on FastAPI auto-422
}
```

```python
# backend/app/schemas/error.py
class ApiError(BaseModel):
    detail: str
    code: Optional[str] = None
```

---

## 6. Error Codes Reference

Centralized list of all error codes for frontend handling. Match the `code` field in error responses.

### Generic
- `INTERNAL_ERROR` (500): unexpected server error — show generic "Terjadi kesalahan. Silakan coba lagi."

### Material input (POST /quiz/generate)
- `MATERIAL_EMPTY` (400)
- `MATERIAL_TOO_SHORT` (400)
- `MATERIAL_TOO_LONG` (400)
- `QUIZ_GENERATION_FAILED` (500)

### Quiz submission (POST /quiz/submit)
- `QUIZ_NOT_FOUND` (404)
- `ANSWERS_LENGTH_MISMATCH` (400)
- `INVALID_QUESTION_ID` (400)
- `INVALID_OPTION_INDEX` (400)
- `INVALID_TIME` (400)
- `EVALUATION_FAILED` (500)

### Frontend handling pattern

```ts
// frontend/src/services/api.ts
async function postJson<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err: ApiError = await res.json().catch(() => ({
      detail: "Tidak dapat terhubung ke server."
    }));
    throw new ApiException(err, res.status);
  }
  return res.json();
}
```

---

## 7. Validation Rules Summary

Quick reference for both sides to keep validation consistent.

### Material text
- Trim whitespace before validating
- Min length: **100 characters** (after trim)
- Max length: **20,000 characters**
- Empty string after trim → `MATERIAL_EMPTY`

### Quiz generation output
- Generate **5–10 questions** (configurable, default 5 for MVP)
- Every question has **exactly 4 options**
- Every question has **exactly 1 correct option index** stored server-side

### Submit input
- `answers.length` MUST equal `total_questions` from generate
- `selected_option_index`: integer 0–3 or `null` (no other types)
- `time_taken_seconds`: integer 0–7200
- `quiz_id`: must exist in server state (in-memory store for MVP)

### Submit output invariants
See §4.5 "Invariants" — all 5 must hold for every successful submit response.

---

## 8. State Management (MVP Implementation Note)

> This section documents the **expected internal behavior**, not part of the public contract. Backend implementers (Audry) should follow this approach unless explicitly changed.

### Quiz storage strategy
- **MVP**: in-memory dict keyed by `quiz_id` → full quiz object (including `correct_option_index` per question)
- Stored on `/quiz/generate`, read on `/quiz/submit`
- Eviction: keep last N quizzes (e.g., 100) or evict on app restart — acceptable for demo
- **Trade-off**: server restart loses all quizzes. For MVP single-session demo, this is fine.

### Why not return correct_answer to the client?
1. **Security**: any user can open browser DevTools → Network tab → see correct answers before submitting
2. **Cleaner contract**: submit endpoint doesn't need to be told the correct answers (server already knows)
3. **Future-proof**: enables features like "view explanation after submit" without contract changes

### Post-MVP migration path
- Replace in-memory dict with SQLite (`sqlite3` in stdlib, no install) → persistent across restarts
- Add `expires_at` field → auto-evict quizzes older than 24h
- Optional: add `GET /quiz/{quiz_id}` to retrieve a previously generated quiz

---

## 9. CORS

Frontend dev server (Vite default `http://localhost:5173`) is on a different origin from the backend (`http://localhost:8000`). Backend MUST enable CORS for development:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

For demo deployment, add the deployed frontend URL to `allow_origins`.

---

## 10. Implementation Notes

### Backend (FastAPI suggested)

**Custom exception with `code`:**
```python
# backend/app/utils/errors.py
from fastapi import HTTPException

class ApiException(HTTPException):
    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
```

**Wire it up in main.py:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ApiException)
async def api_exception_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )
```

**Raise in services:**
```python
raise ApiException(
    status_code=400,
    code="MATERIAL_TOO_SHORT",
    detail="Materi terlalu pendek. Minimal 100 karakter."
)
```

### Frontend (React + TypeScript suggested)

**Centralized API client:**
```ts
// frontend/src/services/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiException extends Error {
  constructor(
    public readonly error: ApiError,
    public readonly status: number,
  ) {
    super(error.detail);
  }
}

export async function generateQuiz(req: QuizGenerateRequest): Promise<QuizGenerateResponse> {
  return postJson("/quiz/generate", req);
}

export async function submitQuiz(req: QuizSubmitRequest): Promise<QuizSubmitResponse> {
  return postJson("/quiz/submit", req);
}
```

**Store API base URL via env:**
```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

---

## 11. Open Questions / Future Work

These are intentionally **out of scope for v1.0** but worth tracking:

- [ ] Should `total_questions` be configurable via generate request (e.g., `?count=10`)? Currently fixed.
- [ ] Should we support multi-language insight/recommendation via `?lang=en`? Currently Indonesian-only.
- [ ] Should generated quizzes persist across server restarts? Currently in-memory only.
- [ ] Should we add `GET /quiz/{quiz_id}` for resuming an in-progress quiz? Not needed for single-session demo.
- [ ] Should we add per-question explanation in submit response (`why_correct: string`)? Useful but not MVP.
- [ ] Rate limiting? Not needed for capstone scope.

---

## 12. Sign-off

This contract requires sign-off from all 4 team members before locking. Tick the box and add a date when you have reviewed AND agreed.

- [ ] **Audry** (Backend — Quiz Generator) — produces shapes in §4.2 response, §5.2 `Question`
- [ ] **Ariq** (Backend — Data & Analysis) — consumes §5.3 `Answer`, produces §4.5 `score`, `chart_data`
- [ ] **Desta** (Backend — Logic, Insight & Recommendation) — produces §4.5 `understanding_level`, `insight`, `recommendation`
- [ ] **Ravi** (Frontend) — consumes §4.2 and §4.5 responses, displays per `DESIGN.md`

After all four boxes are ticked, this document moves from "Draft v1.0" to "Locked v1.0". Any subsequent change requires a new minor version + changelog entry at the bottom of this file.

---

## Changelog

- **v1.0 (2026-05-04)** — Initial draft: 3 endpoints, error codes, shared types, validation rules, implementation notes. Awaiting team review.
