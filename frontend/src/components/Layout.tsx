import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";
import { XpBadge } from "@/components/XpBadge";
import { AuthNav } from "@/components/auth/AuthNav";
import { useAuth } from "@/context/AuthContext";
import { useGamificationStats } from "@/hooks/useGamificationStats";

interface LayoutProps {
  children: ReactNode;
}

/**
 * App-level layout: nav + main content area.
 * Nav: Asahlagi logo (left); XP/streak widget, theme toggle, account menu
 * (right). Profil / Progres / Riwayat / Pengaturan live inside the account menu.
 */
export function Layout({ children }: LayoutProps) {
  const { stats } = useGamificationStats();
  const { user } = useAuth();
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen bg-bg-page">
      <header className="safe-pt border-b border-border-standard bg-bg-page">
        <nav className="safe-px mx-auto flex max-w-5xl items-center justify-between gap-2 py-4 [--safe-gutter:1rem] sm:gap-3 sm:[--safe-gutter:1.5rem]">
          <Link
            to={pathname === "/" ? "/" : "/app"}
            className="rounded-md outline-none focus-visible:[box-shadow:var(--focus-ring)]"
            aria-label="Asahlagi, Beranda"
          >
            <Logo variant="full" />
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            {/* XP/streak only for logged-in users (gamification is account-bound);
                guests and the marketing landing nav stay clean. */}
            {pathname !== "/" && user && <XpBadge stats={stats} />}
            <ThemeToggle />
            <AuthNav />
          </div>
        </nav>
      </header>
      <main className="safe-px mx-auto max-w-5xl pt-12 pb-[calc(6rem_+_env(safe-area-inset-bottom,0px))] [--safe-gutter:1.5rem]">
        {children}
      </main>
    </div>
  );
}
