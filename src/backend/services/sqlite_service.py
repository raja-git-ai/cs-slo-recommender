import sqlite3
import pandas as pd
from src.backend.config import settings

class SQLiteService:
    def __init__(self):
        self.db_path = settings.SQLITE_DB_PATH

    def get_metrics(self, service_name: str, metric_name: str = None, hours: int = 24):
        return self.get_multi_service_metrics([service_name], metric_name, hours)

    def get_multi_service_metrics(self, service_names: list[str], metric_name: str = None, hours: int = 24):
        if not service_names:
            return []
            
        conn = sqlite3.connect(self.db_path)
        
        # Format list for SQL IN clause
        services_str = "', '".join(service_names)
        
        query = f"""
            SELECT timestamp, service_name, metric_name, value 
            FROM metrics 
            WHERE service_name IN ('{services_str}')
            AND timestamp >= datetime('now', '-{hours} hours')
        """
        if metric_name:
            query += f" AND metric_name = '{metric_name}'"
        
        # Order by timestamp to make it easier to read
        query += " ORDER BY timestamp ASC"
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient="records")

sqlite_service = SQLiteService()
