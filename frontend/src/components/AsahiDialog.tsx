import { useEffect, useRef, useState } from "react";
import { Asahi } from "@/components/mascot/Asahi";
import { sendChat } from "@/services/api";
import type { ChatContext, ChatIntent } from "@/types/chat";

/**
 * Asahi game-dialog on the result page (docs/CHATBOT.md). Asahi reacts to the
 * quiz result and offers button choices; each button hits POST /chat.
 *
 * If the backend is unreachable, we fall back to a local on-brand template so
 * the dialog never breaks — the AI is an upgrade on top, not a hard dependency.
 */

interface AsahiDialogProps {
  context: ChatContext;
}

interface Bubble {
  id: number;
  text: string;
}

const ACTIONS: { intent: ChatIntent; label: string }[] = [
  { intent: "weak_points", label: "Lihat kelemahanku" },
  { intent: "study_tips", label: "Tips belajar" },
  { intent: "encouragement", label: "Semangatin aku" },
];

const CLOSING = "Sip! Semangat terus ya — asah lagi kapan pun kamu siap.";

// On-brand fallback used only when the backend can't be reached.
const FALLBACK: Record<ChatIntent, (c: ChatContext) => string> = {
  opening: (c) =>
    `Hai, kamu! Skor kamu ${c.score_percentage}%. ${
      c.score_percentage >= 80
        ? "Mantap, pemahamanmu sudah kuat."
        : c.score_percentage >= 50
          ? "Lumayan — masih ada yang bisa diasah lagi."
          : "Belum apa-apa, ini langkah awal yang baik."
    }`,
  weak_points: (c) =>
    `Kamu salah di ${c.wrong_count} soal${
      c.unanswered_count ? ` dan ${c.unanswered_count} belum dijawab` : ""
    }. Coba baca ulang bagian itu, lalu asah lagi ya.`,
  study_tips: () =>
    "Coba baca ulang materinya, buat catatan singkat pakai kata-katamu sendiri, lalu asah lagi.",
  encouragement: () =>
    "Tiap kali kamu asah lagi, pemahamanmu nambah sedikit demi sedikit. Kamu pasti bisa!",
};

export function AsahiDialog({ context }: AsahiDialogProps) {
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [loading, setLoading] = useState(false);
  const [closed, setClosed] = useState(false);
  const nextId = useRef(0);

  const addBubble = (text: string) =>
    setBubbles((prev) => [...prev, { id: nextId.current++, text }]);

  // Opening line — fetched once when the dialog mounts.
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      try {
        const res = await sendChat({ intent: "opening", context });
        if (active) addBubble(res.reply);
      } catch {
        if (active) addBubble(FALLBACK.opening(context));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [context]);

  async function handleIntent(intent: ChatIntent) {
    if (loading) return;
    setLoading(true);
    try {
      const res = await sendChat({ intent, context });
      addBubble(res.reply);
    } catch {
      addBubble(FALLBACK[intent](context));
    } finally {
      setLoading(false);
    }
  }

  function handleClose() {
    addBubble(CLOSING);
    setClosed(true);
  }

  return (
    <section
      aria-labelledby="asahi-dialog-heading"
      className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1 sm:p-6"
    >
      <h2 id="asahi-dialog-heading" className="sr-only">
        Ngobrol dengan Asahi
      </h2>
      <div className="flex items-start gap-4">
        <Asahi
          mood="wave"
          size={84}
          className="hidden shrink-0 self-end sm:block"
        />
        <div className="min-w-0 flex-1 space-y-3">
          <div className="space-y-2" aria-live="polite">
            {bubbles.map((b) => (
              <p
                key={b.id}
                className="w-fit max-w-prose rounded-2xl rounded-tl-sm bg-bg-alt px-4 py-2.5 text-[15px] leading-relaxed text-text-primary"
              >
                {b.text}
              </p>
            ))}
            {loading && (
              <p className="w-fit rounded-2xl rounded-tl-sm bg-bg-alt px-4 py-2.5 text-sm text-text-secondary">
                <span className="inline-flex gap-1 align-middle">
                  <Dot /> <Dot delay="150ms" /> <Dot delay="300ms" />
                </span>
                <span className="sr-only">Asahi sedang mengetik</span>
              </p>
            )}
          </div>

          {!closed && (
            <div className="flex flex-wrap gap-2 pt-1">
              {ACTIONS.map((a) => (
                <button
                  key={a.intent}
                  type="button"
                  onClick={() => handleIntent(a.intent)}
                  disabled={loading}
                  className="rounded-pill border border-border-standard bg-bg-page px-4 py-1.5 text-sm text-text-primary shadow-level-1 transition-colors hover:bg-bg-alt active:bg-bg-alt disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {a.label}
                </button>
              ))}
              <button
                type="button"
                onClick={handleClose}
                disabled={loading}
                className="rounded-pill px-4 py-1.5 text-sm text-text-secondary transition-colors hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                Makasih, Asahi
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function Dot({ delay = "0ms" }: { delay?: string }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-text-secondary motion-reduce:animate-none"
      style={{ animationDelay: delay }}
    />
  );
}
