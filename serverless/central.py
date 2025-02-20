from dotenv import load_dotenv
from graphdatascience.session import GdsSessions, AuraAPICredentials, DbmsConnectionInfo, AlgorithmCategory
from datetime import timedelta
import pandas as pd
import os

# Load environment variables from .env file
load_dotenv()

# Aura API Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")


print("###################")
print(CLIENT_ID)
print("###################")


# Neo4j Database Connection Info
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Create a new GdsSessions object using credentials from .env
sessions = GdsSessions(api_credentials=AuraAPICredentials(CLIENT_ID, CLIENT_SECRET, TENANT_ID))

name = "my-new-session"
memory = sessions.estimate(
    node_count=475,
    relationship_count=1400,
    algorithm_categories=[AlgorithmCategory.CENTRALITY, AlgorithmCategory.NODE_EMBEDDING],
)

# Create DB connection info using credentials from .env
# this 
db_connection_info = DbmsConnectionInfo(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Create or retrieve a session
gds = sessions.get_or_create(
    session_name=name,
    memory=memory,
    db_connection=db_connection_info, # this is checking for a bolt server currently
    ttl=timedelta(hours=5),
)

print("PRINTING NEW SESSIONS")
print(sessions.list())



G, result = gds.graph.project(
    graph_name="stations-graph",
    query="""
    CALL {
        MATCH (from:Station)
        OPTIONAL MATCH (from)-[r:CONNECTS_TO]->(to:Station)
        RETURN from AS source, r AS rel, to AS target,
               {latitude: coalesce(from.latitude, 0), longitude: coalesce(from.longitude, 0)} AS sourceNodeProperties,
               {latitude: coalesce(to.latitude, 0), longitude: coalesce(to.longitude, 0)} AS targetNodeProperties
    }
    RETURN gds.graph.project.remote(source, target, {
      sourceNodeProperties: sourceNodeProperties,
      targetNodeProperties: targetNodeProperties,
      sourceNodeLabels: labels(source),
      targetNodeLabels: labels(target),
      relationshipType: type(rel),
      relationshipProperties: apoc.map.removeKey(properties(rel), 'lineName')  // Exclude unsupported String property
    })
    """
)


#gds.pageRank.mutate(G, mutateProperty="pr")

gds.pageRank.write(G, writeProperty="pr")

sessions.delete(session_name="my-new-session")

print("SESSION SHOULD BE DEAD")
print(sessions.list())
