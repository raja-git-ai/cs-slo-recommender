from fastapi import APIRouter
from src.backend.services.neo4j_service import neo4j_service
from src.backend.models import ServiceGraph, ServiceNode, Dependency

router = APIRouter()

@router.get("/graph", response_model=ServiceGraph)
async def get_graph():
    # Fetch all nodes and relationships for visualization
    query = """
    MATCH (s:Service)-[r:DEPENDS_ON]->(t:Service)
    RETURN s.name as source, t.name as target, r.criticality as criticality,
           s.type as source_type, s.tier as source_tier,
           t.type as target_type, t.tier as target_tier
    """
    
    # We also need to get nodes that might not have relationships (though in our gen data all do)
    # But for a robust graph, let's just get unique nodes from the rels for now or do two queries.
    
    # Let's do two queries to be safe
    nodes_query = "MATCH (n:Service) RETURN n.name as name, n.type as type, n.tier as tier"
    
    with neo4j_service.driver.session() as session:
        nodes_result = session.run(nodes_query)
        nodes = [ServiceNode(**record.data()) for record in nodes_result]
        
        rels_result = session.run(query)
        edges = []
        for record in rels_result:
            edges.append(Dependency(
                source=record["source"], 
                target=record["target"], 
                criticality=record["criticality"]
            ))
            
    return ServiceGraph(nodes=nodes, edges=edges)
