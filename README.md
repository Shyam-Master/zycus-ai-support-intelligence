# Zycus AI Support Intelligence

An AI-powered internal support tool built for two customer-facing teams:

- **Technical Support** – automatically triages incoming support tickets.
- **Technical Account Management (TAM)** – generates actionable customer account health briefs.

The project uses only the mock dataset and knowledge base provided in the starter repository.

---

## Features

### Task 1: Intelligent Support Ticket Triage

The system accepts a support ticket containing a subject and description and produces:

- Product Area
- Issue Category
- Urgency Tier (P1–P4)
- Recommended Responder Team
- Reasoning for the classification
- Draft First Response
- Relevant Knowledge Base Documents
- Known Issue Pattern Detection

### Task 2: TAM Account Intelligence

Given an Account ID, the system:

- Retrieves account information
- Analyzes recent ticket history
- Generates an Executive Summary
- Detects Open Risks
- Identifies Escalation Signals
- Identifies Churn Risk Signals
- Provides direct evidence quotes from tickets
- Suggests Recommended Talking Points
- Produces deterministic output for the same input

### Task 3: Evaluation Harness

The project includes automated evaluation and regression testing.

Tests include:

- Support ticket classification
- Urgency detection
- Product routing
- Knowledge base retrieval
- Ambiguous input handling
- Prompt injection handling
- TAM account analysis
- Invalid account handling
- Deterministic output validation
- Adversarial test cases

### Bonus

A Streamlit UI is included for demonstrating both:

- Support Issue Triage
- TAM Account Analysis

---

# Architecture

## Support Triage Pipeline

```text
Incoming Support Ticket
        |
        v
Text Processing
        |
        +--------------------+
        |                    |
        v                    v
RAG Retrieval          Triage Engine
        |                    |
        v                    v
Relevant KB Docs       Product Area
                       Issue Category
                       Urgency
                       Recommended Team
        |                    |
        +---------+----------+
                  |
                  v
          Structured Output
                  |
                  v
          Streamlit UI / API
