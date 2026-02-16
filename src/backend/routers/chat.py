from fastapi import APIRouter, HTTPException
from src.backend.models import ChatRequest, ChatResponse
from src.backend.services.neo4j_service import neo4j_service
from src.backend.services.rag_service import rag_service
from src.backend.services.sqlite_service import sqlite_service
from src.backend.services.llm_service import llm_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_slo(request: ChatRequest):
    service_name = request.service_name
    
    # 1. Re-fetch Context (To keep the assistant stateless and up-to-date)
    service_details = neo4j_service.get_service_details(service_name)
    if not service_details:
        raise HTTPException(status_code=404, detail="Service not found")
        
    # Fetch BLAST RADIUS Context (Upstream & Downstream)
    downstream_deps = neo4j_service.get_dependencies(service_name)
    upstream_deps = neo4j_service.get_upstream_dependencies(service_name)
    
    # Collect all relevant service names for metrics
    related_services = [service_name] + \
                      [d['name'] for d in downstream_deps] + \
                      [u['name'] for u in upstream_deps]
    
    # Deduplicate
    related_services = list(set(related_services))
    
    query = f"{service_name} latency error failure"
    runbook_results = rag_service.query_runbooks(query)
    runbooks = runbook_results['documents'][0] if runbook_results and runbook_results['documents'] else []
    
    # Fetch metrics for ALL related services
    # We limit to last 3 hours for chat to keep context small but relevant
    metrics = sqlite_service.get_multi_service_metrics(related_services, hours=3)
    
    # Summarize metrics: We can't dump thousands of rows. 
    # Let's take the last 5 data points per service/metric combo
    metrics_summary = []
    # Simple grouping by service+metric
    from collections import defaultdict
    grouped = defaultdict(list)
    for m in metrics:
        key = f"{m['service_name']}_{m['metric_name']}"
        grouped[key].append(m)
    
    for key, values in grouped.items():
        # Take last 3 values
        metrics_summary.extend(values[-3:])

    # 2. Convert Pydantic models to dict for LLM service
    messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]

    # 3. Generate Response
    response_content = llm_service.chat_with_context(
        service_data=service_details,
        dependencies=downstream_deps,
        upstream_dependencies=upstream_deps, # New
        runbooks=runbooks,
        metrics=metrics_summary,
        messages=messages_dicts
    )
    
    return ChatResponse(role="assistant", content=response_content)
