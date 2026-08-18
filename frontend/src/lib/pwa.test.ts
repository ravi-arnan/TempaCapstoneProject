import { describe, expect, it, vi, afterEach } from "vitest";
import { registerServiceWorker } from "@/lib/pwa";

function stubServiceWorker(register: ReturnType<typeof vi.fn>) {
  Object.defineProperty(navigator, "serviceWorker", {
    value: { register },
    configurable: true,
  });
}

/**
 * Capture the load listener instead of dispatching a real `load` event: the
 * jsdom window is shared between tests, so a dispatched event would also fire
 * listeners left behind by earlier cases.
 */
function captureLoadListener() {
  const listeners: EventListener[] = [];
  const spy = vi
    .spyOn(window, "addEventListener")
    .mockImplementation((type, listener) => {
      if (type === "load") listeners.push(listener as EventListener);
    });
  return { listeners, spy };
}

afterEach(() => {
  vi.restoreAllMocks();
  // @ts-expect-error — remove the stub so other suites see a clean navigator.
  delete navigator.serviceWorker;
});

describe("registerServiceWorker", () => {
  it("registers /sw.js after load in production", () => {
    const register = vi.fn().mockResolvedValue(undefined);
    stubServiceWorker(register);
    const { listeners } = captureLoadListener();

    registerServiceWorker(true);
    expect(register).not.toHaveBeenCalled(); // waits for the load event

    listeners.forEach((fn) => fn(new Event("load")));
    expect(register).toHaveBeenCalledWith("/sw.js");
  });

  it("does nothing outside production", () => {
    const register = vi.fn();
    stubServiceWorker(register);
    const { listeners } = captureLoadListener();

    registerServiceWorker(false);

    expect(listeners).toHaveLength(0);
    expect(register).not.toHaveBeenCalled();
  });

  it("does nothing when the browser has no service worker support", () => {
    const { listeners } = captureLoadListener();

    expect(() => registerServiceWorker(true)).not.toThrow();
    expect(listeners).toHaveLength(0);
  });
});
