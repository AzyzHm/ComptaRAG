import ollama
from app.services.chroma_service import collection
from app.graph.state import GraphState

def retrieve_context(query: str, category, n_results: int = 5):
    """
    Retrieves relevant chunks from ChromaDB filtered by category.
    """
    query_embedding = ollama.embed(
        model="embeddinggemma",
        input=query
    )["embeddings"][0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"category": {"$eq": category}} 
    )

    documents = results.get("documents", [[]])
    context_list = documents[0] if documents and len(documents) > 0 else []
    if not context_list or not isinstance(context_list, list):
        return "No local documents found."
    return "\n\n".join(context_list)

def retrieval_node(state: GraphState):
    context = retrieve_context(state["query"], state["category"], 5)
    return {"context": context}