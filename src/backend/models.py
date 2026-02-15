from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ServiceNode(BaseModel):
    name: str
    type: str
    tier: str

class Dependency(BaseModel):
    source: str
    target: str
    criticality: str

class MetricPoint(BaseModel):
    timestamp: str
    service_name: str
    metric_name: str
    value: float

class SLOResponse(BaseModel):
    service_name: str
    recommended_slo: str
    reasoning: str
    relevant_runbooks: List[str]
    metrics_context: Dict[str, Any]

class ServiceGraph(BaseModel):
    nodes: List[ServiceNode]
    edges: List[Dependency]

class VectorDocument(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]

class VectorCollectionResponse(BaseModel):
    documents: List[VectorDocument]

class MetricsResponse(BaseModel):
    metrics: List[MetricPoint]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    service_name: str
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    role: str
    content: str
