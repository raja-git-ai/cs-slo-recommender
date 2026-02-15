import chromadb
from src.backend.config import settings

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
        # Assumes collection 'runbooks' is already created by generate_data.py
        try:
            self.collection = self.client.get_collection("runbooks")
        except:
            self.collection = None # Handle case where collection doesn't exist yet

    def query_runbooks(self, query_text: str, n_results: int = 3):
        if not self.collection:
             return []
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

rag_service = RAGService()
