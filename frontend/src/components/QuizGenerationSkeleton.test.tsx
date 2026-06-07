import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { QuizGenerationSkeleton } from "@/components/QuizGenerationSkeleton";

describe("QuizGenerationSkeleton", () => {
  it("is decorative (aria-hidden) so it doesn't pollute the a11y tree", () => {
    const { container } = render(<QuizGenerationSkeleton />);
    expect(container.firstElementChild).toHaveAttribute("aria-hidden", "true");
  });

  it("renders four answer-option placeholders", () => {
    const { container } = render(<QuizGenerationSkeleton />);
    expect(container.querySelectorAll(".h-11")).toHaveLength(4);
  });

  it("disables the shimmer under reduced motion", () => {
    const { container } = render(<QuizGenerationSkeleton />);
    const animated = container.querySelectorAll(".animate-pulse");
    expect(animated.length).toBeGreaterThan(0);
    animated.forEach((el) => {
      expect(el.className).toContain("motion-reduce:animate-none");
    });
  });
});
