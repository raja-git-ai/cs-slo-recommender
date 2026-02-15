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
        
    dependencies = neo4j_service.get_dependencies(service_name)
    
    query = f"{service_name} latency error failure"
    runbook_results = rag_service.query_runbooks(query)
    runbooks = runbook_results['documents'][0] if runbook_results and runbook_results['documents'] else []
    
    metrics = sqlite_service.get_metrics(service_name, hours=24)
    metrics_summary = metrics if len(metrics) < 10 else metrics[-10:]

    # 2. Convert Pydantic models to dict for LLM service
    messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]

    # 3. Generate Response
    response_content = llm_service.chat_with_context(
        service_data=service_details,
        dependencies=dependencies,
        runbooks=runbooks,
        metrics=metrics_summary,
        messages=messages_dicts
    )
    
    return ChatResponse(role="assistant", content=response_content)
