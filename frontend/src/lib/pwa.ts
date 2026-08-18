/**
 * Service worker registration (ROADMAP §6.5 — PWA).
 *
 * Only registers on a real deploy: in dev a cached shell would shadow HMR, and
 * in tests there is no `navigator.serviceWorker` at all.
 */
export function registerServiceWorker(
  isProduction: boolean = import.meta.env.PROD,
): void {
  if (!isProduction) return;
  if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) return;

  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // An unavailable service worker degrades to a plain website — nothing to
      // tell the user about.
    });
  });
}
