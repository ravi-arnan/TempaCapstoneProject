import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/lib/cn";

/**
 * Theme toggle pill — segmented control, sticky top-right.
 * Mirrors the pattern from preview.html.
 */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div
      role="tablist"
      aria-label="Theme switcher"
      className="inline-flex rounded-full border border-border-standard bg-bg-page p-1 shadow-level-1"
    >
      <button
        type="button"
        role="tab"
        aria-selected={theme === "light"}
        onClick={() => setTheme("light")}
        className={cn(
          "flex items-center gap-1.5 rounded-full px-4 py-2 font-mono text-[11px] font-medium uppercase tracking-[1.2px] transition-colors",
          theme === "light"
            ? "bg-text-primary text-bg-page"
            : "text-text-muted hover:text-text-primary",
        )}
      >
        <SunIcon />
        Light
      </button>
      <button
        type="button"
        role="tab"
        aria-selected={theme === "dark"}
        onClick={() => setTheme("dark")}
        className={cn(
          "flex items-center gap-1.5 rounded-full px-4 py-2 font-mono text-[11px] font-medium uppercase tracking-[1.2px] transition-colors",
          theme === "dark"
            ? "bg-text-primary text-bg-page"
            : "text-text-muted hover:text-text-primary",
        )}
      >
        <MoonIcon />
        Dark
      </button>
    </div>
  );
}

function SunIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      className="h-3 w-3"
      aria-hidden="true"
    >
      <circle cx="8" cy="8" r="3" />
      <line x1="8" y1="1" x2="8" y2="3" />
      <line x1="8" y1="13" x2="8" y2="15" />
      <line x1="1" y1="8" x2="3" y2="8" />
      <line x1="13" y1="8" x2="15" y2="8" />
      <line x1="3.05" y1="3.05" x2="4.46" y2="4.46" />
      <line x1="11.54" y1="11.54" x2="12.95" y2="12.95" />
      <line x1="3.05" y1="12.95" x2="4.46" y2="11.54" />
      <line x1="11.54" y1="4.46" x2="12.95" y2="3.05" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-3 w-3"
      aria-hidden="true"
    >
      <path d="M14 9.5a6 6 0 11-7.5-7.5 5 5 0 007.5 7.5z" />
    </svg>
  );
}
