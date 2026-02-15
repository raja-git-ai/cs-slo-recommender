import sqlite3
import pandas as pd
from src.backend.config import settings

class SQLiteService:
    def __init__(self):
        self.db_path = settings.SQLITE_DB_PATH

    def get_metrics(self, service_name: str, metric_name: str = None, hours: int = 24):
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT timestamp, metric_name, value 
            FROM metrics 
            WHERE service_name = '{service_name}' 
            AND timestamp >= datetime('now', '-{hours} hours')
        """
        if metric_name:
            query += f" AND metric_name = '{metric_name}'"
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient="records")

sqlite_service = SQLiteService()
