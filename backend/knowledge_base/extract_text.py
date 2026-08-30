import os

from pypdf import PdfReader


def extract_pdf_text(path: str) -> str:
    """Extract text from a pdf file"""
    reader = PdfReader(path)
    text = []

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text.append(content)

    return "\n".join(text)


def process_pdf(input_folder: str, output_folder: str) -> None:
    """process pdf files in a given folder"""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            full_path = os.path.join(input_folder, filename)
            text = extract_pdf_text(full_path)

            with open(
                os.path.join(output_folder, filename.replace(".pdf", ".txt")), "w", encoding="utf-8"
            ) as f:
                f.write(text)


if __name__ == "__main__":
    process_pdf(
        "knowledge_base/documents/code_tva_impot_droit", "knowledge_base/extracted_text/tax_code"
    )
    process_pdf(
        "knowledge_base/documents/ifrs_ey_gaap_version", "knowledge_base/extracted_text/ifrs"
    )
    process_pdf(
        "knowledge_base/documents/normes_comptable",
        "knowledge_base/extracted_text/accounting_standards",
    )
