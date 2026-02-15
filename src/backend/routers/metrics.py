from fastapi import APIRouter
from src.backend.services.sqlite_service import sqlite_service
from src.backend.models import MetricsResponse, MetricPoint
import sqlite3
import pandas as pd

router = APIRouter()

@router.get("/metrics/all", response_model=MetricsResponse)
async def get_all_metrics(limit: int = 100):
    # Retrieve latest metrics
    conn = sqlite3.connect(sqlite_service.db_path)
    query = f"""
        SELECT timestamp, service_name, metric_name, value 
        FROM metrics 
        ORDER BY timestamp DESC 
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    metrics = []
    for _, row in df.iterrows():
        metrics.append(MetricPoint(
            timestamp=str(row['timestamp']),
            service_name=row['service_name'],
            metric_name=row['metric_name'],
            value=float(row['value'])
        ))
        
    return MetricsResponse(metrics=metrics)
