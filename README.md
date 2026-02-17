# SLO Recommender Agent

An AI-driven system to recommend Service Level Objectives (SLOs) based on microservice topology, historical metrics, and operational runbooks.

## Architecture

-   **Backend**: FastAPI (Python)
-   **Frontend**: React (Vite)
-   **Graph DB**: Neo4j (Service Topology)
-   **Vector DB**: ChromaDB (Runbooks)
-   **Metrics DB**: SQLite (Time-series data)
-   **LLM**: Ollama (Reasoning)

## Prerequisites

1.  **Neo4j**: Local instance running at `bolt://localhost:7687`.
2.  **Ollama**: running at `http://localhost:11434` (Model: `mistral` pulled).
3.  **Python 3.9+** & **Node.js 16+**.

## Setup & Run

## Documentation

-   [Code Architecture & Flow Explained](documents/ArchDesign/architecture.md)
-   [Code Flow Diagram](documents/ArchDesign/codeflow.png)
-   [Architecture & System Design - Diagram](documents/ArchDesign/SLORecommendation.png)
-   [Architecture & System Design - Draw.io file](documents/ArchDesign/SLORecommendation.drawio)
-   [Architecture & System Design - Explanation](documents/Documentation/ArchExplanation.md)


## Setup & Run

The project includes helper scripts for easy startup.

### 1. Backend

```bash
./run_backend.sh
```
This script will:
*   Create a python virtual environment.
*   Install dependencies.
*   Generate fresh synthetic data for Neo4j, ChromaDB, and SQLite.
*   Start the FastAPI server at `http://localhost:8000`.

### 2. Frontend

```bash
./run_frontend.sh
```
This script will:
*   Install npm dependencies.
*   Start the React dev server.

Visit `http://localhost:5174` to use the application.

## Usage

1.  Select a service from the input box (e.g., `PaymentService`, `Frontend`, `CartService`).
2.  Click **Get Recommendation**.
3.  View the generated SLOs, reasoning, and relevant runbooks.
4.  Explore the service topology in the graph view.

![App Demo](documents/ArchDesign/SLOGenAppInAction.mp4)