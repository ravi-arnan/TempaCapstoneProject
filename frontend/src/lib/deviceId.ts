/**
 * Anonymous device identity for gamification.
 *
 * Generates a UUID once and persists it in localStorage. Sent as the
 * `X-Device-Id` header so the backend can attribute XP/streak/level to a
 * device without requiring login. Designed to be swappable for a real auth
 * user id later.
 */

const KEY = "asahlagi-device-id";

export function getDeviceId(): string {
  try {
    let id = localStorage.getItem(KEY);
    if (!id) {
      id =
        typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `dev-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      localStorage.setItem(KEY, id);
    }
    return id;
  } catch {
    // localStorage unavailable (private mode); ephemeral id for this session.
    return `ephemeral-${Math.random().toString(36).slice(2)}`;
  }
}
