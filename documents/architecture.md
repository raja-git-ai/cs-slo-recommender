# Architecture & System Design

## Overview
The **SLO Recommender Agent** is an AI-driven system designed to assist Site Reliability Engineers (SREs) in defining appropriate Service Level Objectives (SLOs). It aggregates data from multiple sources (Topology, Metrics, Runbooks) and uses a Large Language Model (LLM) to reason about the service's context and recommend realistic reliability targets.

## Technology Stack

### Backend
-   **Framework**: FastAPI (Python) - High-performance async API.
-   **LLM Engine**: Ollama (running local models like `mistral`).
-   **Databases**:
    -   **Neo4j** (Graph DB): Stores microservice topology (Services, Dependencies, Criticality).
    -   **ChromaDB** (Vector DB): Stores embeddings of operational runbooks for RAG (Retrieval-Augmented Generation).
    -   **SQLite** (Relational DB): Stores historical time-series metrics (Latency, Error Rate, Throughput).

### Frontend
-   **Framework**: React (Vite).
-   **Visualization**: `react-force-graph-2d` for interactive topology visualization.
-   **Styling**: Pure CSS (Light Theme, Responsive).

## Data Flow Pipeline

1.  **User Request**: User selects a service (e.g., `PaymentService`) and initiates a request via the React Frontend.
2.  **Orchestrator (`main.py` -> `routers/slo.py`)**:
    -   The backend API receives the request.
    -   It triggers three specialized "Agents" (Data retrievers) in parallel:
3.  **Context Retrieval**:
    -   **Graph Agent**: Queries Neo4j to find the service's Tier (1/2/3) and immediate dependencies.
    -   **Metric Agent**: Queries SQLite to fetch the last 24h of performance data (P95 Latency peaks, Error Rate anomalies).
    -   **RAG Agent**: Embeds the service name and query terms to find relevant troubleshooting runbooks in ChromaDB.
4.  **LLM Reasoning**:
    -   The aggregated context is formatted into a structured prompt.
    -   Ollama generates a response recommending SLOs (e.g., "Latency < 200ms") with a detailed reasoning section explaining *why* based on the provided metrics and dependencies.
5.  **Chat Interaction**:
    -   User can ask follow-up questions (`/api/v1/chat`).
    -   The Chat endpoint maintains the retrieved context and appends the conversation history for the LLM.

## Key Components

### Data Generation (`generate_data.py`)
A synthetic data generator that simulates:
-   **12+ Microservices**: Covering common patterns (Frontend, Cart, Payment, DBs, Cache).
-   **Complex Topology**: Multi-tier dependencies.
-   **Realistic Metrics**: Includes simulated daily traffic patterns, random spikes, and specific failure scenarios (e.g., Memory Leaks, 14:00 PaymentService Latency Spike).

### Data Models
-   `ServiceNode`: Represents a microservice in the graph.
-   `SLOResponse`: The structured output containing the recommendation and context.
-   `ChatRequest/Response`: Handles the conversational interface.
