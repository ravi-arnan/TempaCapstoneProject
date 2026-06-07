import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { CircleUserRound, TrendingUp } from "lucide-react";
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
 * Nav: Asahlagi logo (left); profil + progress links, XP/streak widget, theme
 * toggle, auth (right). The hub links only appear when gamification is active.
 */
export function Layout({ children }: LayoutProps) {
  const { stats } = useGamificationStats();
  const { pathname } = useLocation();

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
              <>
                <NavPill
                  to="/profil"
                  icon={CircleUserRound}
                  label={NAV_LABELS.profile}
                  active={pathname === "/profil"}
                />
                <NavPill
                  to="/progress"
                  icon={TrendingUp}
                  label={NAV_LABELS.progress}
                  active={pathname === "/progress"}
                />
              </>
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

function NavPill({
  to,
  icon: Icon,
  label,
  active,
}: {
  to: string;
  icon: LucideIcon;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      to={to}
      aria-current={active ? "page" : undefined}
      className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[1.2px] shadow-level-1 outline-none transition-colors focus-visible:[box-shadow:var(--focus-ring)] ${
        active
          ? "border-brand-button bg-brand-button text-white"
          : "border-border-standard bg-bg-page text-text-primary hover:bg-[var(--hover-tint)]"
      }`}
    >
      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
      <span className="hidden font-mono sm:inline">{label}</span>
    </Link>
  );
}
