from fastapi import APIRouter
from src.backend.services.rag_service import rag_service
from src.backend.models import VectorCollectionResponse, VectorDocument

router = APIRouter()

@router.get("/vectors", response_model=VectorCollectionResponse)
async def get_vectors():
    if not rag_service.collection:
        return VectorCollectionResponse(documents=[])
    
    # Fetch all documents (limit to 100 for performance if needed, but get() returns all by default)
    # We can use limit/offset if the DB grows, but for now 100 is fine.
    data = rag_service.collection.get(limit=100)
    
    documents = []
    if data and data['ids']:
        for i, doc_id in enumerate(data['ids']):
            documents.append(VectorDocument(
                id=doc_id,
                text=data['documents'][i] if data['documents'] else "",
                metadata=data['metadatas'][i] if data['metadatas'] else {}
            ))
            
    return VectorCollectionResponse(documents=documents)
