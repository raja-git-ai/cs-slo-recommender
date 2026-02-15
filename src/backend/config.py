import os
from dotenv import load_dotenv

# Load .env from the same directory as config.py
config_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(config_dir, ".env")
load_dotenv(dotenv_path=env_path)

class Settings:
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chroma_db")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./metrics.db")

settings = Settings()
