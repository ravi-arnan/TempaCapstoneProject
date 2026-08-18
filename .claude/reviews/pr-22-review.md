# PR Review: #22 — feat(mobile): responsive + touch polish (ROADMAP §6.5-A)

**Reviewed**: 2026-06-14
**Author**: Ravi Arnan
**Branch**: feat/mobile-polish-6.5a → main
**Decision**: APPROVE

## Summary
Clean, well-scoped mobile-polish pass: 44px touch targets, `active:` pressed states,
notch-safe gutters, responsive type/spacing, and two real bundle wins (route code-split
+ on-demand `canvas-confetti` + Lucide icon allow-list). Frontend-only, no API/backend
changes. Typecheck, 100 tests, and production build all green. No correctness or security
issues found.

## Findings

### CRITICAL
None.

### HIGH
None.

### MEDIUM
None.

### LOW
- **`hooks/useConfetti.ts`** — `void import("canvas-confetti").then(...)` has no `.catch`.
  If the lazy chunk fails to load (network blip / offline), it surfaces as an unhandled
  promise rejection. Confetti is non-critical, so impact is cosmetic — adding
  `.catch(() => {})` would keep the console clean. Optional.

### NOTE (verified, no action needed)
- **`components/BadgeGrid.tsx`** — replacing the dynamic `icons[name]` lookup with the
  explicit `BADGE_ICONS` allow-list is a strong bundle win (avoids pulling ~1000 Lucide
  icons). Verified the allow-list (`Sparkles, Star, Flame, TrendingUp, Trophy`) is **in
  sync** with backend `achievements.py` — every badge icon is covered; none fall back to
  `Award`. The in-code "keep in sync" comment correctly flags the only residual risk
  (future drift).
- **`index.css` `.safe-px`** — switching to `max(var(--safe-gutter,0px), env(...))` is
  backwards-compatible: when `--safe-gutter` is unset it reduces to `env(...)` exactly as
  before, so untouched `.safe-px` callers don't regress. The three touched callers
  (nav, main, quiz bottom bar) all set `--safe-gutter` explicitly.

## Validation Results

| Check | Result |
|---|---|
| Type check (`tsc --noEmit`) | Pass |
| Lint | Skipped (no `lint` script in package.json) |
| Tests (`vitest run`) | Pass — 100/100 across 23 files |
| Build (`tsc -b && vite build`) | Pass — code-split confirmed; main chunk 75.56 kB gzip (under budget) |

## Files Reviewed
- docs/ROADMAP.md (Modified — docs)
- frontend/src/App.tsx (Modified — route code-split + Suspense)
- frontend/src/components/BadgeGrid.tsx (Modified — icon allow-list)
- frontend/src/components/DailyChallengeCard.tsx (Modified — touch target/active)
- frontend/src/components/Layout.tsx (Modified — nav gutters + XP badge gating)
- frontend/src/components/Logo.tsx (Modified — wordmark hidden < 360px)
- frontend/src/components/MaterialInputForm.tsx (Modified — touch target)
- frontend/src/components/QuestionPills.tsx (Modified — size + active)
- frontend/src/components/ResultSummary.tsx (Modified — wrap spacing)
- frontend/src/components/SourceTypeTabs.tsx (Modified — touch target)
- frontend/src/components/StatTile.tsx (Modified — responsive padding/text + truncate)
- frontend/src/components/ThemeToggle.tsx (Modified — mobile icon toggle / desktop segmented)
- frontend/src/components/XpBadge.tsx (Modified — streak hidden on mobile)
- frontend/src/components/auth/UserMenu.tsx (Modified — touch targets + active)
- frontend/src/hooks/useConfetti.ts (Modified — lazy import)
- frontend/src/index.css (Modified — safe-px gutter fix)
- frontend/src/pages/HomePage.tsx (Modified — responsive hero + touch target)
- frontend/src/pages/ProgressPage.tsx (Modified — touch target)
- frontend/src/pages/QuizPage.tsx (Modified — safe-area bottom bar + touch targets)
- frontend/src/pages/ResultPage.tsx (Modified — touch targets)
- frontend/src/pages/SettingsPage.tsx (Modified — touch target)
- frontend/src/utils/i18n.ts (Modified — theme aria labels)
