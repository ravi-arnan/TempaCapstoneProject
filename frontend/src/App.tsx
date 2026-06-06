import { Navigate, Route, Routes } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { QuizPage } from "@/pages/QuizPage";
import { ResultPage } from "@/pages/ResultPage";
import { ProgressPage } from "@/pages/ProgressPage";
import { Layout } from "@/components/Layout";

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
