# Deployment — Asahlagi

**Status**: Planning / ready to execute.
**Last updated**: 2026-05-25

Three pieces:
1. **Quiz generator** — Hugging Face Space (already live)
2. **Backend (FastAPI)** — Render
3. **Frontend (React)** — Vercel

Deploying the backend to a public HTTPS URL is also the **prerequisite for the
Android app** (see `MOBILE.md`).

---

## 1. Quiz generator (Hugging Face Space)

Already deployed: `https://raviarnan-asahlagi-quizgen.hf.space`
(Dockerized, in `huggingface-space/`.) No action needed unless the model
changes.

---

## 2. Backend — Render

The repo includes `render.yaml` (a Render Blueprint), so most config is
codified. Render free tier requires a payment method on file (no charge on the
free plan), and the service spins down after ~15 min idle (cold start ~30s).

### Steps
1. Push the repo to GitHub (done).
2. Render dashboard, New, Blueprint, connect the repo. Render reads `render.yaml`.
3. Add billing (card) to the account if prompted, then keep the **free** plan.
4. Set the secret env vars in the dashboard (they are `sync: false` in the blueprint):
   - `HF_SPACE_URL` = `https://raviarnan-asahlagi-quizgen.hf.space`
   - `DATABASE_URL` = the Neon connection string
   - `CORS_ALLOWED_ORIGINS` = `https://<your-vercel-app>.vercel.app,https://localhost`
     (the `https://localhost` entry is for the Capacitor Android app)
5. Deploy. Verify: `curl https://asahlagi-backend.onrender.com/health` returns
   `{"status":"ok",...}`.

### Notes
- `render.yaml` sets `rootDir: backend`, build `pip install -r requirements.txt`,
  start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, health check `/health`.
- Free tier RAM is 512 MB. scikit-learn + numpy + pandas fit, but if the build
  is memory-tight, upgrade the plan or trim deps.
- The classifier `.pkl` is committed, so no training runs on Render.

---

## 3. Frontend — Vercel

1. Vercel dashboard, New Project, import the repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite. Build command `npm run build`, output `dist`.
4. Set env var `VITE_API_BASE_URL` = the Render backend URL
   (e.g. `https://asahlagi-backend.onrender.com`).
5. Deploy. Update the backend `CORS_ALLOWED_ORIGINS` to include the resulting
   Vercel URL, then redeploy the backend if needed.

---

## Post-deploy checklist

- [ ] `GET /health` on the Render URL returns ok
- [ ] Frontend on Vercel can generate a quiz (text)
- [ ] Submit works end-to-end (score, level, insight, recommendation)
- [ ] Gamification: `GET /gamification/stats` works with `X-Device-Id` header
- [ ] CORS allows the Vercel origin (no console errors in the browser)
- [ ] Update `VITE_API_BASE_URL` in the Android build before packaging (see `MOBILE.md`)
