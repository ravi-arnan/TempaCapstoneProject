/**
 * Recovery for a lazy route chunk that no longer exists (ROADMAP §6.5).
 *
 * Every route except the landing page is code-split, so the filenames are
 * content-hashed. A tab left open across a deploy asks for a chunk that is gone
 * from the server, and once the service worker landed it is gone from the cache
 * too: `activate` deletes the previous cache version. The import rejects and the
 * user lands on a blank route when a refresh would have fixed it.
 *
 * Reloading once fixes it. The only real hazard is reloading forever when the
 * chunk is permanently missing, so the decision is a small pure function with a
 * cooldown and it is tested.
 */
export const CHUNK_RELOAD_KEY = "asahlagi:chunk-reload-at";

/**
 * A reload is near-instant, so a genuinely broken chunk fails again well inside
 * this window and falls through to the error UI instead of looping. A later
 * deploy in the same session is outside it and can still self-heal.
 */
export const CHUNK_RELOAD_COOLDOWN_MS = 10_000;

export function shouldReloadForChunkError(
  lastAttemptAt: number | null,
  now: number,
): boolean {
  if (!lastAttemptAt) return true;
  return now - lastAttemptAt > CHUNK_RELOAD_COOLDOWN_MS;
}

/**
 * Wrap a `() => import(...)` so a missing chunk reloads the page once.
 * Rethrows instead of reloading when storage is unavailable, because without
 * somewhere to record the attempt there is no way to bound the loop.
 */
export function withChunkReload<T>(load: () => Promise<T>): () => Promise<T> {
  return () =>
    load().catch((error) => {
      let last: number | null = null;
      try {
        last = Number(sessionStorage.getItem(CHUNK_RELOAD_KEY)) || null;
      } catch {
        throw error;
      }
      if (!shouldReloadForChunkError(last, Date.now())) throw error;
      try {
        sessionStorage.setItem(CHUNK_RELOAD_KEY, String(Date.now()));
      } catch {
        throw error;
      }
      window.location.reload();
      // Deliberately never settles: the page is being replaced.
      return new Promise<T>(() => {});
    });
}
