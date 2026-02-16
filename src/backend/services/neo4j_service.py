from neo4j import GraphDatabase
from src.backend.config import settings

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def get_dependencies(self, service_name: str):
        """Get downstream dependencies (services this service calls)"""
        query = """
        MATCH (s:Service {name: $service_name})-[r:DEPENDS_ON]->(d:Service)
        RETURN d.name as name, d.type as type, d.tier as tier, r.criticality as criticality
        """
        with self.driver.session() as session:
            result = session.run(query, service_name=service_name)
            dependencies = [record.data() for record in result]
        return dependencies

    def get_upstream_dependencies(self, service_name: str):
        """Get upstream dependencies (services that call this service)"""
        query = """
        MATCH (s:Service)-[r:DEPENDS_ON]->(d:Service {name: $service_name})
        RETURN s.name as name, s.type as type, s.tier as tier, r.criticality as criticality
        """
        with self.driver.session() as session:
            result = session.run(query, service_name=service_name)
            dependencies = [record.data() for record in result]
        return dependencies

    def get_service_details(self, service_name: str):
        query = """
        MATCH (s:Service {name: $service_name})
        RETURN s.name as name, s.type as type, s.tier as tier
        """
        with self.driver.session() as session:
            result = session.run(query, service_name=service_name)
            record = result.single()
            return record.data() if record else None

neo4j_service = Neo4jService()
