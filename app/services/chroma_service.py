from chromadb import PersistentClient

client  = PersistentClient(path="knowledge_base/chroma_db")

collection = client.get_collection(name="ai_assistant")