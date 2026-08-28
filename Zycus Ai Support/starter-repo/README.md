# Zycus AI Support Intelligence

## Project Overview
Zycus AI Support is an intelligent, deterministic support assessment platform that automatically triages incoming support requests and evaluates Technical Account Management (TAM) health scores across a subset of B2B client accounts. The architecture heavily incorporates local mock datasets and deterministic LLM fallback simulations.

## Problem Statement
Support teams often struggle with high ticket volume, manual routing inefficiencies, and limited visibility into churn risks for specific accounts. This project aims to demonstrate an agentic approach to automatically classifying support issues, identifying relevant KB documentation, evaluating urgency, and systematically calculating account health based on rolling 90-day ticket windows.

## Features
- **Intelligent Ticket Triage:** Categorizes issues by Product Area and Issue Category.
- **Dynamic Urgency Detection:** Accurately classifies P1-P4 severities based on outage scope, security, and user impact without blindly trusting input keywords.
- **RAG Knowledge Base:** Searches through internal markdown documentation via a local ChromaDB/sentence-transformers embedding database.
- **TAM Account Health Summarizer:** Generates executive health briefs dynamically by analyzing a company's 90-day ticket history for escalation/churn signals and unresolved P1/P2 issues.
- **Streamlit Dashboard:** Provides an interactive interface for support personnel to triage tickets or query account health on demand.
- **Automated Evaluation Harness:** Ensures 100% regression stability and determinism via comprehensive CLI test runners.

## Architecture
The application runs as a modular FastAPI backend paired with a Streamlit presentation layer.

```text
Streamlit UI (Frontend)
      ↓
FastAPI App / Services (Backend)
      ↓
RAG DB (Chroma) + LLM Client (Deterministic Engine)
      ↓
Local Data Loader (tickets.json / accounts.json / KB)
```

## Technology Stack
- **Backend**: Python 3.9+, FastAPI, Pydantic
- **Frontend**: Streamlit
- **Database/RAG**: ChromaDB, Sentence-Transformers
- **Testing**: Pytest, Custom Evaluation Harness

## Installation Instructions

1. **Clone the repository.**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   A `.env` file should be located at the project root with the following:
   ```env
   API_KEY=dummy_key
   ```
   *(Leaving it as `dummy_key` ensures the highly-optimized deterministic fallback mode is used instead of attempting an external LLM request).*

## How to Run the Application

### Option A: Run the Backend and Frontend separately
**1. Start the API:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
**2. Start the UI:**
```bash
streamlit run streamlit_app.py
```

### Option B: Quickstart Batch Script (Windows)
Double click `run.bat` in the root directory to immediately launch the API server.

## Testing Instructions

**1. Run the Evaluation Harness:**
Tests the integration pipelines for both Triage and TAM agents against pre-defined adversarial, nominal, and baseline cases.
```bash
python -m evaluation.run_eval
```

**2. Run the Unit Tests:**
Tests the granular, deterministic text-matching and logic branching of the Triage agent.
```bash
python verify_triage.py
```

## Example Inputs and Outputs

**Support Triage Example**
- *Input:* "System down - The entire platform is down for everyone."
- *Output:* P1 Urgency, Performance / Availability, assigned to Platform Engineering.

**TAM Account Analysis Example**
- *Input:* "ACC-3336"
- *Output:* Stable Health, 1 recent ticket, 0 active risks (resolved P2).

## Future Improvements
- Integrate robust multi-agent LLM pipelines using LangChain or OpenAI.
- Connect to an actual ticketing CRM (e.g., Zendesk, Jira).
- Expand data-loader implementations to utilize cloud-hosted vector databases (Pinecone, Weaviate).

## Design Note
For a detailed analysis of the architectural trade-offs, potential failure modes, data sensitivity considerations, and scaling strategies for this system, please review the [DESIGN_NOTE.md](./DESIGN_NOTE.md) file.
