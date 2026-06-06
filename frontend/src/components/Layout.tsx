import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { TrendingUp } from "lucide-react";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";
import { XpBadge } from "@/components/XpBadge";
import { AuthNav } from "@/components/auth/AuthNav";
import { useGamificationStats } from "@/hooks/useGamificationStats";
import { NAV_LABELS } from "@/utils/i18n";

interface LayoutProps {
  children: ReactNode;
}

/**
 * App-level layout: nav + main content area.
 * Nav: Asahlagi logo (left); progress link, XP/streak widget, theme toggle (right).
 * The progress link only appears when gamification is active (stats present).
 */
export function Layout({ children }: LayoutProps) {
  const { stats } = useGamificationStats();
  const { pathname } = useLocation();
  const isProgressActive = pathname === "/progress";

  return (
    <div className="min-h-screen bg-bg-page">
      <header className="border-b border-border-standard bg-bg-page">
        <nav className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-6 py-4">
          <Link
            to="/"
            className="rounded-md outline-none focus-visible:[box-shadow:var(--focus-ring)]"
            aria-label="Asahlagi, Beranda"
          >
            <Logo variant="full" />
          </Link>
          <div className="flex items-center gap-3">
            {stats && (
              <Link
                to="/progress"
                aria-current={isProgressActive ? "page" : undefined}
                className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[1.2px] shadow-level-1 outline-none transition-colors focus-visible:[box-shadow:var(--focus-ring)] ${
                  isProgressActive
                    ? "border-brand-button bg-brand-button text-white"
                    : "border-border-standard bg-bg-page text-text-primary hover:bg-[var(--hover-tint)]"
                }`}
              >
                <TrendingUp className="h-3.5 w-3.5" aria-hidden="true" />
                <span className="hidden sm:inline font-mono">
                  {NAV_LABELS.progress}
                </span>
              </Link>
            )}
            <XpBadge stats={stats} />
            <ThemeToggle />
            <AuthNav />
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-12">{children}</main>
    </div>
  );
}
