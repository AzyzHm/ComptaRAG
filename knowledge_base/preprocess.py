import re
import os

def clean_text(text : str) -> str:
    text = text.replace("\n", " ") # replace all new line characters with spaces.
    text = re.sub(r'\s+', ' ', text) # replace any sequence of spaces into a single one.
    return text.strip()

def chunk_text(text : str, chunk_size:int=800, overlap:int=150) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

def preprocess_text(input_folder : str, output_folder : str,category : str) -> None:
    
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(input_folder):
        if file.endswith('.txt'):
            with open(os.path.join(input_folder, file), "r", encoding="utf-8") as f:
                raw = f.read()

            text = clean_text(raw)
            chunks = chunk_text(text)

            output_path = os.path.join(output_folder, file.replace('.txt', '.jsonl'))
            with open(output_path, 'w', encoding='utf-8') as out:
                for i, chunk in enumerate(chunks):
                    out.write(f'{{"id" : "{file}_{i}", "text" : "{chunk}", "category" : "{category}"}}\n')


if __name__ == '__main__':

    # preprocess ifrs text
    preprocess_text("knowledge_base/extracted_text/ifrs", "knowledge_base/processed_chunks/ifrs","ifrs")
    
    # preprocess tax_code text
    preprocess_text("knowledge_base/extracted_text/tax_code", "knowledge_base/processed_chunks/tax_code","tax_code")

    # preprocess accounting standards text
    preprocess_text("knowledge_base/extracted_text/accounting_standards", "knowledge_base/processed_chunks/accounting_standards","accounting_standards")