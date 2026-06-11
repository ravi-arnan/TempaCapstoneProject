/**
 * Skeleton preview shown while a quiz is being generated (ROADMAP §5). Mirrors
 * the shape of QuizQuestionCard so the wait feels like "your quiz is coming"
 * instead of a blank gap. Decorative only — the loading status/aria-live lives
 * in the form's progress card, so this is aria-hidden.
 *
 * The shimmer respects prefers-reduced-motion via `motion-reduce:animate-none`.
 */
import { Asahi } from "@/components/mascot/Asahi";

const SHIMMER = "rounded bg-bg-subtle animate-pulse motion-reduce:animate-none";

export function QuizGenerationSkeleton() {
  return (
    <div
      aria-hidden="true"
      className="rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-1"
    >
      {/* Asahi "thinking" while the quiz is being written */}
      <Asahi mood="think" size={64} className="mx-auto mb-4" />
      {/* question label */}
      <div className={`mb-3 h-3 w-20 ${SHIMMER}`} />
      {/* question text (two lines) */}
      <div className="mb-6 space-y-2">
        <div className={`h-5 w-3/4 ${SHIMMER}`} />
        <div className={`h-5 w-1/2 ${SHIMMER}`} />
      </div>
      {/* 4 answer options */}
      <div className="space-y-2">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className={`h-11 w-full rounded-xl bg-bg-subtle animate-pulse motion-reduce:animate-none`} />
        ))}
      </div>
    </div>
  );
}
