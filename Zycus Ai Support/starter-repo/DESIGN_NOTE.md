# Zycus AI Support: Design Note

This document outlines key design decisions, trade-offs, and scaling considerations for the Zycus AI Support architecture, specifically addressing failure modes, latency vs. quality, data sensitivity, and scaling.

## 1. Failure Modes

While the current system utilizes robust deterministic fallbacks and comprehensive evaluation harnesses, there are three primary ways the solution could fail in a production setting:

### Failure Mode 1: Deterministic Fallback Misclassification
*   **What could go wrong:** If the external LLM is unavailable or disabled (using `dummy_key`), the deterministic fallback engine takes over. This engine relies on hardcoded keyword heuristics. A user might submit a complex edge-case ticket (e.g., "The platform is nominally up but critical SSO functionality is completely inaccessible") that lacks standard keywords, leading the fallback logic to incorrectly classify a P1 outage as a P3 issue.
*   **How it could be detected:** Discrepancies can be caught during routine executions of the evaluation harness (`evaluation.run_eval`), or in production via monitoring sudden spikes in customer escalation rates compared to the automated triage categories.
*   **How it could be mitigated:** Continuously expand and refine the keyword lists and heuristic rules within the fallback triage engine based on historical missed tickets. Additionally, implement a human-in-the-loop review queue for tickets where the engine's confidence score falls below a certain threshold.

### Failure Mode 2: RAG/ChromaDB Retrieval Mismatch
*   **What could go wrong:** The local ChromaDB and sentence-transformers embedding database might fail to retrieve the correct knowledge base (KB) article for a specific issue. This can happen due to poor query phrasing by the user or sub-optimal embedding chunking, returning irrelevant context to the triage agent.
*   **How it could be detected:** High rates of tickets escalated without relevant KB articles attached, or direct user feedback indicating irrelevant search results within the Streamlit dashboard interface.
*   **How it could be mitigated:** Regularly re-index the KB documentation, fine-tune chunk sizes and overlap parameters, and introduce a reranking model to improve the precision of the initial retrieval phase before the context is finalized.

### Failure Mode 3: TAM Data In-Memory Exhaustion
*   **What could go wrong:** The TAM account summarization heavily relies on parsing local mock JSON files (`tickets.json`, `accounts.json`). In a production setting with thousands of accounts, dynamically loading and filtering large volumes of data in-memory to calculate rolling 90-day ticket windows and unresolved P1/P2 risks will lead to severe memory exhaustion or application crashes.
*   **How it could be detected:** Increased latency, timeouts, and out-of-memory errors on the FastAPI backend during the `GET /account/{account_id}/brief` API calls.
*   **How it could be mitigated:** Migrate away from in-memory JSON data loading. Transition to a structured relational database (e.g., PostgreSQL) with indexed timestamps to enable rapid querying of 90-day rolling windows directly at the database layer.

## 2. Latency vs Quality

The primary architectural trade-off in the existing system is the RAG (Retrieval-Augmented Generation) pipeline for ticket triage. By executing semantic searches against a local ChromaDB instance to retrieve relevant knowledge base documents, the system dramatically improves the accuracy, grounding, and factual correctness of its triage output. However, this semantic search step—running sentence-transformers locally—adds significant processing time before the triage logic or LLM can even begin execution.

If low latency became the absolute highest priority for support responses, several optimizations would be required:
*   **Semantic Caching:** Cache common ticket embeddings or exact phrase matches to instantly bypass the retrieval process for frequently recurring issues.
*   **Reduced Chunk Retrieval:** Lower the `top_k` documents returned by ChromaDB to reduce the payload processing time.
*   **Smaller/Faster Models:** Switch to a highly quantized or distilled embedding model that sacrifices minor semantic accuracy in exchange for vastly accelerated inference times.
*   **Optimized Retrieval:** Offload the local vector database to a dedicated remote vector store, preventing the main FastAPI threads from being blocked by synchronous retrieval tasks.

## 3. Data Sensitivity

The current implementation of the Zycus AI Support project relies exclusively on the provided synthetic mock dataset (`accounts.json`, `tickets.json`). There is no active exposure or processing of real customer data.

However, in a real production environment, handling support tickets and TAM account data introduces significant data sensitivity risks, specifically concerning Personally Identifiable Information (PII) and proprietary corporate data. To ensure strict compliance and security, the following measures are highly recommended:
*   **PII Detection and Redaction:** All incoming tickets should pass through an automated local redaction layer to mask emails, phone numbers, and names before any data is transmitted to external model APIs.
*   **Logging Controls:** Sensitive ticket bodies and specific account details must never be logged in raw plaintext within application logs.
*   **Secure Secrets Management:** Use secure environment variables or a robust secrets manager for all credentials. API keys must never be committed to source control (the current `.env.example` setup is a foundation, but strict enforcement is required).
*   **Approved Infrastructure:** Utilize approved, private model infrastructure (such as self-hosted enterprise models or Azure OpenAI) rather than public API endpoints. This guarantees that proprietary data is not used to train third-party public models.
*   **Access Control and Encryption:** Implement strict Role-Based Access Control (RBAC) on the FastAPI backend and ensure all sensitive data is encrypted both at rest and in transit.

## 4. Scaling

Under a 10x increase in ticket volume, the current architecture would experience severe performance degradation. The system is designed around local mock data and synchronous processes, which inherently lack horizontal scalability.

**Likely Bottlenecks:**
*   **Local/Mock Data Architecture:** Reading and filtering the 90-day ticket window dynamically from JSON files into memory during TAM analysis will quickly crash under heavy concurrent load.
*   **Embedding Generation and Vector Retrieval:** Running local sentence-transformers synchronously on the FastAPI thread blocks the event loop, causing cascading latency spikes during RAG retrieval.
*   **LLM/API Inference:** Synchronous, blocking calls to external APIs or deterministic engines will severely limit the concurrent connections the server can handle.
*   **Repeated TAM Analysis:** Recalculating comprehensive account health from scratch on every incoming request is computationally wasteful.

**Scaling Strategies:**
To handle massive scale effectively, the system must evolve through key infrastructure upgrades:
*   **Persistent/Scalable Vector Database:** Migrate from a local ChromaDB instance to a managed, distributed vector database capable of horizontal scaling.
*   **Asynchronous Processing and Job Queues:** Offload ticket triage, embedding generation, and API inference to background workers (e.g., Celery, Redis Queue) instead of blocking the main FastAPI web threads.
*   **Database Indexing:** Replace JSON files with a proper relational database featuring optimized timestamp indexes for instantaneous 90-day window queries.
*   **Caching:** Implement aggressive Redis caching for frequently accessed TAM account briefs and common ticket queries to avoid redundant processing.
*   **Horizontal API Scaling:** Containerize the FastAPI application and deploy it across a Kubernetes cluster behind a load balancer, allowing for the independent scaling of web and worker nodes based on traffic.
*   **Batch Embedding:** Process non-urgent embedding generation for the knowledge base in scheduled background batches to optimize compute resources.
