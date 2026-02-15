from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.services.neo4j_service import neo4j_service
from src.backend.routers import slo, graph, vectors, metrics, chat

app = FastAPI(
    title="SLO Recommender Agent",
    description="AI-driven SLO recommendations based on Service Topology, Metrics, and Runbooks.",
    version="1.0.0"
)


# CORS (Allow Frontend)
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(slo.router, prefix="/api/v1", tags=["SLO"])
app.include_router(graph.router, prefix="/api/v1", tags=["Graph"])
app.include_router(vectors.router, prefix="/api/v1", tags=["Vectors"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

@app.on_event("shutdown")
def shutdown_event():
    neo4j_service.close()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
