from fastapi import APIRouter, HTTPException
from src.backend.models import SLOResponse
from src.backend.services.neo4j_service import neo4j_service
from src.backend.services.rag_service import rag_service
from src.backend.services.sqlite_service import sqlite_service
from src.backend.services.llm_service import llm_service

router = APIRouter()

@router.get("/recommend/{service_name}", response_model=SLOResponse)
async def recommend_slo(service_name: str):
    # 1. Get Service Details & Dependencies (Graph Agent)
    service_details = neo4j_service.get_service_details(service_name)
    if not service_details:
        raise HTTPException(status_code=404, detail="Service not found in Graph")
        
    dependencies = neo4j_service.get_dependencies(service_name)
    
    # 2. Get Runbooks (RAG Agent)
    # Query based on service name and common failure modes
    query = f"{service_name} latency error failure"
    runbook_results = rag_service.query_runbooks(query)
    runbooks = runbook_results['documents'][0] if runbook_results and runbook_results['documents'] else []
    
    # 3. Get Metrics (Metric Agent)
    # Get last 24h summary
    metrics = sqlite_service.get_metrics(service_name, hours=24)
    # Simple aggregation for context (in a real app, we'd do smarter aggregation)
    # Just take a few representative points or calculate stats
    metrics_summary = metrics if len(metrics) < 10 else metrics[-10:] 
    
    # 4. Generate Recommendation (LLM Agent)
    recommendation = llm_service.generate_slo_recommendation(
        service_data=service_details,
        dependencies=dependencies,
        runbooks=runbooks,
        metrics=metrics_summary
    )
    
    return SLOResponse(
        service_name=service_name,
        recommended_slo="See detailed reasoning", # LLM returns full text, we can parse it or just return it in reasoning
        reasoning=recommendation,
        relevant_runbooks=runbooks,
        metrics_context={"count": len(metrics), "latest": metrics[-1] if metrics else None}
    )
