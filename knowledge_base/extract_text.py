from pypdf import PdfReader
import os


def extract_pdf_text(path : str) -> str:
    reader = PdfReader(path)
    text = []

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text.append(content)

    return '\n'.join(text)


def process_pdf(input_folder : str, output_folder : str) -> None:

    # if the directory already exists then this won't do shit
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            full_path = os.path.join(input_folder, filename)
            text = extract_pdf_text(full_path)

            # create a text file containing all the text we extracted from the pdf
            with open(os.path.join(output_folder, filename.replace('.pdf','.txt')), "w", encoding="utf-8") as f:
                f.write(text)


if __name__ == '__main__':

    # extract the tax_code docs
    process_pdf("knowledge_base/documents/code_tva_impot_droit", "knowledge_base/extracted_text/tax_code")

    # extract the ifrs docs
    process_pdf("knowledge_base/documents/ifrs_ey_gaap_version", "knowledge_base/extracted_text/ifrs")

    # extract the local accounting standards
    process_pdf("knowledge_base/documents/normes_comptable", "knowledge_base/extracted_text/accounting_standards")