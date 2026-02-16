import os
import random
import time
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from neo4j import GraphDatabase
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", ".env")
load_dotenv(dotenv_path=env_path)

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chroma_db")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./metrics.db")

# Neo4j Driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# --- Data Definitions ---

services = [
    {"name": "Frontend", "type": "UI", "tier": "Tier-1"},
    {"name": "AdService", "type": "Microservice", "tier": "Tier-2"},
    {"name": "RecommendationService", "type": "Microservice", "tier": "Tier-2"},
    {"name": "ProductService", "type": "Microservice", "tier": "Tier-1"},
    {"name": "CartService", "type": "Microservice", "tier": "Tier-1"},
    {"name": "CurrencyService", "type": "Microservice", "tier": "Tier-3"},
    {"name": "PaymentService", "type": "Microservice", "tier": "Tier-1"},
    {"name": "ShippingService", "type": "Microservice", "tier": "Tier-2"},
    {"name": "EmailService", "type": "Microservice", "tier": "Tier-3"},
    {"name": "CheckoutService", "type": "Microservice", "tier": "Tier-1"},
    {"name": "RedisCache", "type": "Database", "tier": "Tier-1"},
    {"name": "PostgresDB", "type": "Database", "tier": "Tier-1"},
    {"name": "UserDB", "type": "Database", "tier": "Tier-1"},
]

relationships = [
    ("Frontend", "AdService"),
    ("Frontend", "RecommendationService"),
    ("Frontend", "ProductService"),
    ("Frontend", "CartService"),
    ("Frontend", "CheckoutService"),
    ("CheckoutService", "CartService"),
    ("CheckoutService", "PaymentService"),
    ("CheckoutService", "EmailService"),
    ("CheckoutService", "ShippingService"),
    ("CheckoutService", "CurrencyService"),
    ("RecommendationService", "ProductService"),
    ("ProductService", "RedisCache"),
    ("ProductService", "PostgresDB"),
    ("CartService", "RedisCache"),
    ("PaymentService", "UserDB"),
    ("AdService", "PostgresDB"),
]

runbooks = [
    {
        "id": "rb_001",
        "service": "PaymentService",
        "text": "PaymentService High Latency: Check connection pool to UserDB. If CPU > 80%, scale up replicas. Verify 3rd party gateway status. If latency persists > 500ms for 5m, failover to secondary provider.",
        "metadata": {"type": "latency", "service": "PaymentService"}
    },
    {
        "id": "rb_002",
        "service": "PaymentService",
        "text": "PaymentService Error Rate > 1%: Check for 5xx errors from UserDB. Rollback recent deployment if error rate spikes immediately after deploy. Check logs for 'Connection Refused'.",
        "metadata": {"type": "error_rate", "service": "PaymentService"}
    },
    {
        "id": "rb_003",
        "service": "ProductService",
        "text": "ProductService High Latency (Cache Miss): If P99 > 200ms, check RedisCache hit rate. If hit rate < 80%, investigate cache eviction policy or warm up cache. Check PostgresDB slow query logs.",
        "metadata": {"type": "latency", "service": "ProductService"}
    },
    {
        "id": "rb_004",
        "service": "Frontend",
        "text": "Frontend Slow Loading: Check CDN latency. Verify downstream dependencies (Cart, Product, Checkout) are healthy. Aggregated latency impacts user experience directly. Enable circuit breakers if downstream is slow.",
        "metadata": {"type": "latency", "service": "Frontend"}
    },
    {
        "id": "rb_005",
        "service": "RedisCache",
        "text": "Redis High Memory Usage: If memory > 90%, check for large keys or keys without TTL. Scaling policy: Add read replicas if read OPS are high. Investigate eviction logs.",
        "metadata": {"type": "saturation", "service": "RedisCache"}
    },
    {
        "id": "rb_006",
        "service": "PostgresDB",
        "text": "Postgres Connection Starvation: 'FATAL: remaining connection slots are reserved'. Check active connections. Increase max_connections or implement PgBouncer. Kill idle transactions > 10m.",
        "metadata": {"type": "saturation", "service": "PostgresDB"}
    },
    {
        "id": "rb_007",
        "service": "CheckoutService",
        "text": "Checkout Failure: Critical flow. If failure rate > 0.1%, immediately page on-call. Check PaymentService and ShippingService health. Verify inventory reservation consistency.",
        "metadata": {"type": "error_rate", "service": "CheckoutService"}
    },
    {
        "id": "rb_008",
        "service": "AdService",
        "text": "AdService Latency: Non-critical path. If latency > 1s, soft-fail and return empty ads to avoid blocking page load. Check external ad network timeouts.",
        "metadata": {"type": "latency", "service": "AdService"}
    }
]

# --- Functions ---

def generate_neo4j_data():
    print("Generating Neo4j Data...")
    try:
        with driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create Services
            for service in services:
                session.run(
                    "CREATE (s:Service {name: $name, type: $type, tier: $tier})",
                    name=service["name"], type=service["type"], tier=service["tier"]
                )
                
            # Create Relationships
            for source, target in relationships:
                # Determine criticality based on Tier
                # If target is Tier-1, dependency is High criticality
                target_service = next(s for s in services if s["name"] == target)
                criticality = "High" if target_service["tier"] == "Tier-1" else "Low"
                
                session.run(
                    """
                    MATCH (s:Service {name: $source}), (t:Service {name: $target})
                    CREATE (s)-[:DEPENDS_ON {criticality: $criticality}]->(t)
                    """,
                    source=source, target=target, criticality=criticality
                )
        print("Neo4j Data Generated.")
    except Exception as e:
        print(f"Error generating Neo4j data: {e}")

def generate_chromadb_data():
    print("Generating ChromaDB Data...")
    try:
        client = chromadb.PersistentClient(path=CHROMADB_PATH)
        collection_name = "runbooks"
        
        try:
            client.delete_collection(name=collection_name)
        except:
            pass
            
        collection = client.create_collection(name=collection_name)
        
        collection.add(
            documents=[rb["text"] for rb in runbooks],
            metadatas=[rb["metadata"] for rb in runbooks],
            ids=[rb["id"] for rb in runbooks]
        )
        print("ChromaDB Data Generated.")
    except Exception as e:
        print(f"Error generating ChromaDB data: {e}")

def generate_sqlite_data():
    print("Generating SQLite Data...")
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp DATETIME,
                service_name TEXT,
                metric_name TEXT,
                value REAL
            )
        """)
        
        cursor.execute("DELETE FROM metrics")
        
        # Generator Settings
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        current_time = start_time
        
        while current_time <= end_time:
            time_hour = current_time.hour
            is_peak = 18 <= time_hour <= 22 # Peak traffic 6PM-10PM
            
            for service in services:
                # 1. Base Latency
                base_latency = 50.0
                if service["tier"] == "Tier-1": base_latency = 20.0
                if service["type"] == "Database": base_latency = 5.0
                
                # Randomized variability
                val = random.gauss(base_latency, base_latency * 0.1)
                
                # Patterns
                if is_peak:
                    val *= 1.5
                    
                # Specific service anomalies
                # Make PaymentService slow in the last 4 hours for DEMO purposes
                if service["name"] == "PaymentService" and (time_hour >= end_time.hour - 4 or (14 <= time_hour <= 15)):
                    val += 200 # Latency spike
                    
                if service["name"] == "RedisCache" and (time_hour % 6 == 0):
                    val += 50 # Periodic cache maintenance spike
                    
                if service["name"] == "ProductService":
                     # Memory leak simulation (latency creeps up over timewindow)
                     elapsed = (current_time - start_time).total_seconds() / 3600
                     val += elapsed * 2 

                cursor.execute("INSERT INTO metrics VALUES (?, ?, ?, ?)", 
                               (current_time, service["name"], "latency_p95", max(0, val)))
                
                # 2. Error Rate
                err_rate = random.expovariate(100) # Mostly 0, rare spikes
                if service["name"] == "CheckoutService" and is_peak:
                     err_rate += random.uniform(0.1, 0.5) # Flaky during peak
                
                cursor.execute("INSERT INTO metrics VALUES (?, ?, ?, ?)", 
                               (current_time, service["name"], "error_rate", err_rate))
                
                # 3. Throughput
                tput = random.uniform(100, 1000)
                if is_peak: tput *= 2.5
                
                cursor.execute("INSERT INTO metrics VALUES (?, ?, ?, ?)", 
                               (current_time, service["name"], "throughput", tput))
                
            current_time += timedelta(hours=1)
        
        conn.commit()
        conn.close()
        print("SQLite Data Generated.")
    except Exception as e:
        print(f"Error generating SQLite data: {e}")

if __name__ == "__main__":
    generate_neo4j_data()
    generate_chromadb_data()
    generate_sqlite_data()
    driver.close()
    print("All Data Generated Successfully.")
