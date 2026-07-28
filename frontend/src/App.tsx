import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { LandingPage } from "@/pages/LandingPage";
import { Layout } from "@/components/Layout";
import { withChunkReload } from "@/lib/chunkReload";

// Landing is the entry route → keep it eager (no loading flash on first paint).
// Every other page is code-split so the initial bundle stays light on mobile.
//
// Each loader goes through withChunkReload so a tab left open across a deploy
// recovers by itself instead of dead-ending on a chunk that no longer exists.
// Wrapped inline rather than through a generic helper: React.lazy infers each
// page's props from its loader, and a helper signature erases that inference.

const HomePage = lazy(
  withChunkReload(() =>
    import("@/pages/HomePage").then((m) => ({ default: m.HomePage })),
  ),
);
const QuizPage = lazy(
  withChunkReload(() =>
    import("@/pages/QuizPage").then((m) => ({ default: m.QuizPage })),
  ),
);
const ResultPage = lazy(
  withChunkReload(() =>
    import("@/pages/ResultPage").then((m) => ({ default: m.ResultPage })),
  ),
);
const ProgressPage = lazy(
  withChunkReload(() =>
    import("@/pages/ProgressPage").then((m) => ({ default: m.ProgressPage })),
  ),
);
const ProfilePage = lazy(
  withChunkReload(() =>
    import("@/pages/ProfilePage").then((m) => ({ default: m.ProfilePage })),
  ),
);
const HistoryPage = lazy(
  withChunkReload(() =>
    import("@/pages/HistoryPage").then((m) => ({ default: m.HistoryPage })),
  ),
);
const LeaderboardPage = lazy(
  withChunkReload(() =>
    import("@/pages/LeaderboardPage").then((m) => ({
      default: m.LeaderboardPage,
    })),
  ),
);
const SettingsPage = lazy(
  withChunkReload(() =>
    import("@/pages/SettingsPage").then((m) => ({ default: m.SettingsPage })),
  ),
);

function RouteFallback() {
  return (
    <p className="py-16 text-center text-sm text-text-muted" role="status">
      Memuat…
    </p>
  );
}

export function App() {
  return (
    <Layout>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<HomePage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/profil" element={<ProfilePage />} />
          <Route path="/riwayat" element={<HistoryPage />} />
          <Route path="/peringkat" element={<LeaderboardPage />} />
          <Route path="/pengaturan" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}
