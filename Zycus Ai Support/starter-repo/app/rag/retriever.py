import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

def retrieve_documents(query: str, top_k: int = 3, distance_threshold: float = 1.6):
    client = chromadb.PersistentClient(path=str(settings.chroma_db_dir))
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    try:
        collection = client.get_collection(name="knowledge_base", embedding_function=emb_fn)
    except Exception:
        return []
        
    results = collection.query(query_texts=[query], n_results=top_k)
    
    retrieved = []
    if results and results['documents']:
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
            
            if dist <= distance_threshold:
                retrieved.append({
                    "document": meta['filename'],
                    "relative_path": meta['relative_path'],
                    "category": meta['category'],
                    "chunk_text": doc,
                    "distance": dist
                })
    return retrieved
