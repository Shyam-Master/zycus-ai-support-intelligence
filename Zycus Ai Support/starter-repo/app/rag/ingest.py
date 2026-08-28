import os
import re
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

def chunk_markdown(content: str, max_chars: int = 800, overlap: int = 150):
    chunks = []
    # Split by headers
    sections = re.split(r'(?=\n#{1,4} )', content)
    
    for section in sections:
        section = section.strip()
        if not section: continue
        
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            # Further split by double newline
            sub_paragraphs = section.split('\n\n')
            current_chunk = ""
            for p in sub_paragraphs:
                if len(current_chunk) + len(p) <= max_chars:
                    current_chunk += p + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = p + "\n\n"
            if current_chunk:
                chunks.append(current_chunk.strip())
    return chunks

def ingest_documents():
    client = chromadb.PersistentClient(path=str(settings.chroma_db_dir))
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="knowledge_base", embedding_function=emb_fn)
    
    # Idempotent: delete existing chunks
    existing = collection.get()
    if existing and existing['ids']:
        collection.delete(ids=existing['ids'])
        
    docs, metadatas, ids = [], [], []
    
    idx = 0
    for md_file in settings.kb_dir.rglob('*.md'):
        category = md_file.parent.name
        rel_path = md_file.relative_to(settings.base_dir)
        content = md_file.read_text(encoding='utf-8')
        
        chunks = chunk_markdown(content)
        for chunk_idx, chunk in enumerate(chunks):
            docs.append(chunk)
            metadatas.append({
                "filename": md_file.name,
                "relative_path": str(rel_path),
                "category": category,
                "chunk_index": chunk_idx
            })
            ids.append(f"{md_file.name}_{chunk_idx}")
            idx += 1
            
    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
    return len(docs), len(list(settings.kb_dir.rglob('*.md')))
