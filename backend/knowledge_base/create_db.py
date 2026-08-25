import json
from chromadb import PersistentClient
import ollama
import os
import time

BATCH_SIZE = 50  
MODEL_NAME = "embeddinggemma"
KEEP_ALIVE = "60m" # Keep model in memory for 60 minutes to prevent reloading

def warm_up_model():
    """
    Sends a dummy request to force the model to load into VRAM 
    before processing starts.
    """
    print(f"Loading model '{MODEL_NAME}' into memory...")
    try:
        ollama.embeddings(
            model=MODEL_NAME, 
            prompt="warmup", 
            keep_alive=KEEP_ALIVE
        )
        print("Model loaded and ready.")
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)

def get_embedding(text: str):
    """
    Get embedding for a single text, ensuring the model stays alive.
    """
    response = ollama.embeddings(
        model=MODEL_NAME,
        prompt=text,
        keep_alive=KEEP_ALIVE 
    )
    return response["embedding"]

def process_batch(batch_entries, collection):
    """
    Takes a list of entries, generates embeddings, and writes to DB in one go.
    """
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for entry in batch_entries:
        try:
            emb = get_embedding(entry["text"])
            
            ids.append(entry["id"])
            embeddings.append(emb)
            documents.append(entry["text"])
            metadatas.append({"category": entry["category"]})
        except Exception as e:
            print(f"Failed to embed chunk {entry.get('id', 'unknown')}: {e}")
            continue

    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

def ingest_jsonl(path: str) -> None:
    print(f"Processing file: {path}")
    current_batch = []
    count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                current_batch.append(entry)
                
                if len(current_batch) >= BATCH_SIZE:
                    process_batch(current_batch, collection)
                    count += len(current_batch)
                    print(f"  - Processed {count} chunks...", end='\r')
                    current_batch = []
                    
            except json.JSONDecodeError:
                continue

        if current_batch:
            process_batch(current_batch, collection)
            count += len(current_batch)

    print(f"  - Completed {path} ({count} chunks total)")

def ingest_into_db(input_folder: str) -> None:
    """ Insert JSONL files into a chromadb database """
    if not os.path.exists(input_folder):
        print(f"Folder not found: {input_folder}")
        return

    for file in os.listdir(input_folder):
        if file.endswith(".jsonl"):
            ingest_jsonl(os.path.join(input_folder, file))

client = PersistentClient(path="knowledge_base/chroma_db")

collection = client.get_or_create_collection(
    name="ai_assistant",
    metadata={"hnsw:space": "cosine"}
)
print("ChromaDB Initialized successfully!")

if __name__ == "__main__":
    warm_up_model()

    folders_to_process = [
        "knowledge_base/processed_chunks/tax_code",
        "knowledge_base/processed_chunks/ifrs",
        "knowledge_base/processed_chunks/accounting_standards"
    ]

    start_time = time.time()
    
    for folder in folders_to_process:
        print(f"--- Ingesting from: {folder} ---")
        ingest_into_db(folder)

    print(f"\nAll data ingested in {time.time() - start_time:.2f} seconds!")

    # this script took 5454.63 seconds to execute !