import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { EMPTY_STATES } from "@/utils/i18n";

function renderPdfForm() {
  const onSubmitPdf = vi.fn();
  const utils = render(
    <MaterialInputForm
      sourceType="pdf"
      onSubmitText={vi.fn()}
      onSubmitUrl={vi.fn()}
      onSubmitPdf={onSubmitPdf}
    />,
  );
  const form = utils.container.querySelector("form") as HTMLFormElement;
  return { ...utils, form, onSubmitPdf };
}

function pdf(name: string): File {
  return new File(["%PDF-1.4"], name, { type: "application/pdf" });
}

describe("MaterialInputForm drag-and-drop (PDF)", () => {
  it("accepts a dropped PDF and shows its name", () => {
    const { form } = renderPdfForm();
    fireEvent.drop(form, { dataTransfer: { files: [pdf("materi.pdf")] } });
    expect(screen.getByText("materi.pdf")).toBeInTheDocument();
  });

  it("rejects a dropped non-PDF with an error", () => {
    const { form } = renderPdfForm();
    fireEvent.drop(form, {
      dataTransfer: { files: [new File(["x"], "catatan.docx")] },
    });
    expect(screen.getByText(EMPTY_STATES.pdfMustBePdf)).toBeInTheDocument();
    expect(screen.queryByText("catatan.docx")).not.toBeInTheDocument();
  });

  it("shows the drop-active hint while dragging over", () => {
    const { form } = renderPdfForm();
    fireEvent.dragOver(form);
    expect(screen.getByText(EMPTY_STATES.pdfDropActive)).toBeInTheDocument();
  });
});
