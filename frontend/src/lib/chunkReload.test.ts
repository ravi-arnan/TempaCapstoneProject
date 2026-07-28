import { describe, expect, it, vi, afterEach } from "vitest";
import {
  CHUNK_RELOAD_COOLDOWN_MS,
  CHUNK_RELOAD_KEY,
  shouldReloadForChunkError,
  withChunkReload,
} from "@/lib/chunkReload";

afterEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe("shouldReloadForChunkError", () => {
  it("allows a reload when nothing has been tried yet", () => {
    expect(shouldReloadForChunkError(null, 1_000_000)).toBe(true);
    expect(shouldReloadForChunkError(0, 1_000_000)).toBe(true);
  });

  it("refuses a second reload inside the cooldown, so it cannot loop", () => {
    const now = 1_000_000;
    expect(shouldReloadForChunkError(now, now)).toBe(false);
    expect(shouldReloadForChunkError(now - CHUNK_RELOAD_COOLDOWN_MS, now)).toBe(
      false,
    );
  });

  it("allows a reload again after the cooldown, for a later deploy", () => {
    const now = 1_000_000;
    expect(
      shouldReloadForChunkError(now - CHUNK_RELOAD_COOLDOWN_MS - 1, now),
    ).toBe(true);
  });
});

describe("withChunkReload", () => {
  it("passes a successful import straight through", async () => {
    const loaded = { default: "page" };
    await expect(withChunkReload(async () => loaded)()).resolves.toBe(loaded);
    expect(sessionStorage.getItem(CHUNK_RELOAD_KEY)).toBeNull();
  });

  it("reloads once on a failed import and records the attempt", () => {
    const reload = vi.fn();
    vi.spyOn(window, "location", "get").mockReturnValue({
      ...window.location,
      reload,
    } as unknown as Location);

    void withChunkReload(async () => {
      throw new Error("Failed to fetch dynamically imported module");
    })();

    return Promise.resolve().then(() => {
      expect(reload).toHaveBeenCalledTimes(1);
      expect(sessionStorage.getItem(CHUNK_RELOAD_KEY)).not.toBeNull();
    });
  });

  it("rethrows instead of reloading when an attempt was just made", async () => {
    const reload = vi.fn();
    vi.spyOn(window, "location", "get").mockReturnValue({
      ...window.location,
      reload,
    } as unknown as Location);
    sessionStorage.setItem(CHUNK_RELOAD_KEY, String(Date.now()));

    await expect(
      withChunkReload(async () => {
        throw new Error("Failed to fetch dynamically imported module");
      })(),
    ).rejects.toThrow("Failed to fetch");
    expect(reload).not.toHaveBeenCalled();
  });
});
