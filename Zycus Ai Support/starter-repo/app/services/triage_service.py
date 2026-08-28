import logging
from app.schemas.triage import TriageRequest, TriageResponse
from app.rag.retriever import retrieve_documents
from app.llm.client import LLMClient

logger = logging.getLogger(__name__)

class TriageService:
    def __init__(self):
        self.llm = LLMClient()
        
    def triage_ticket(self, request: TriageRequest) -> TriageResponse:
        # Step 1 - Validate input
        if not request.subject.strip() and not request.body.strip():
            raise ValueError("Subject and body cannot both be empty.")
            
        # Step 2 - Build retrieval query
        query = f"{request.subject} {request.body}"
        kb_results = retrieve_documents(query, top_k=3)
        
        kb_context = "\n\n".join([f"[{res['document']}] {res['chunk_text']}" for res in kb_results])
        kb_docs = list(set([res['document'] for res in kb_results]))
        
        # Step 3 & 4 - Determine triage and LLM integration
        llm_response = self.llm.generate_triage(request.subject, request.body, kb_context)
        
        # Enhance fallback response with actual retrieved docs
        if self.llm.use_fallback:
            llm_response["relevant_kb_docs"] = kb_docs
            
        return TriageResponse(**llm_response)
