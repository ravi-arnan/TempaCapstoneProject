# Deployment — Asahlagi

**Status**: Planning / ready to execute.
**Last updated**: 2026-05-25

Three pieces:
1. **Quiz generator** — Hugging Face Space (already live)
2. **Backend (FastAPI)** — Hugging Face Space (chosen; no credit card needed)
3. **Frontend (React)** — Vercel

Deploying the backend to a public HTTPS URL is also the **prerequisite for the
Android app** (see `MOBILE.md`).

---

## 1. Quiz generator (Hugging Face Space)

Already deployed: `https://raviarnan-asahlagi-quizgen.hf.space`
(Dockerized, in `huggingface/quizgen/`.) No action needed unless the model
changes.

---

## 2. Backend — Hugging Face Space (Docker)

Chosen because it needs **no credit card** (unlike Render/Railway), provides
HTTPS automatically, and the team already uses HF Spaces. Config lives in
`huggingface/backend/` (Dockerfile + README). The Dockerfile clones the
`backend/` folder from GitHub at build time, so no code is duplicated and no
`.env` is ever exposed (it is gitignored).

### Steps
1. Create a new Space: huggingface.co, New, Space. SDK = **Docker**, name e.g.
   `asahlagi-backend`, hardware = CPU basic (free).
2. Push the two files from `huggingface/backend/` (Dockerfile + README.md)
   to the Space repo root. (Same flow as the quiz-gen Space:
   `huggingface-cli login`, then git push.)
3. In the Space, Settings, Variables and secrets, add **secrets**:
   - `DATABASE_URL` = the Neon connection string
   - `HF_SPACE_URL` = `https://raviarnan-asahlagi-quizgen.hf.space`
   - `CORS_ALLOWED_ORIGINS` = `https://<your-vercel-app>.vercel.app,https://localhost`
     (`https://localhost` is for the Capacitor Android app)
4. The Space builds automatically. Verify:
   `curl https://<user>-asahlagi-backend.hf.space/health` returns `{"status":"ok",...}`.

### Notes
- To deploy a newer backend commit: Settings, **Factory rebuild** (re-clones fresh).
- HF free CPU is generous (2 vCPU, 16 GB RAM) — fits scikit-learn + pandas easily.
- Free Spaces sleep after 48h idle; first request wakes it (~30-60s). Warm up
  before a demo by hitting `/health`.
- The classifier `.pkl` is committed in the repo, so no training runs on build.

### Alternative: Render (needs a card)
The repo also includes `render.yaml` (a Render Blueprint) if you ever prefer
Render. Render free tier requires a payment method on file (no charge on free).
Steps: Render dashboard, New, Blueprint, connect repo, add card + keep free plan,
set the same three secrets, deploy.

---

## 3. Frontend — Vercel

1. Vercel dashboard, New Project, import the repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite. Build command `npm run build`, output `dist`.
4. Set env var `VITE_API_BASE_URL` = the backend Space URL
   (e.g. `https://<user>-asahlagi-backend.hf.space`).
5. Deploy. Update the backend `CORS_ALLOWED_ORIGINS` to include the resulting
   Vercel URL, then redeploy the backend if needed.

---

## Post-deploy checklist

- [ ] `GET /health` on the backend Space URL returns ok
- [ ] Frontend on Vercel can generate a quiz (text)
- [ ] Submit works end-to-end (score, level, insight, recommendation)
- [ ] Gamification: `GET /gamification/stats` works with `X-Device-Id` header
- [ ] CORS allows the Vercel origin (no console errors in the browser)
- [ ] Update `VITE_API_BASE_URL` in the Android build before packaging (see `MOBILE.md`)
