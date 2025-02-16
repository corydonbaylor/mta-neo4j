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
db_connection_info = DbmsConnectionInfo(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Create or retrieve a session
gds = sessions.get_or_create(
    session_name=name,
    memory=memory,
    db_connection=db_connection_info,
    ttl=timedelta(hours=5),
)

print("PRINTING NEW SESSIONS")
print(sessions.list())

# Load Cora dataset (example)
CORA_CONTENT = "https://data.neo4j.com/cora/cora.content"
CORA_CITES = "https://data.neo4j.com/cora/cora.cites"

content = pd.read_csv(CORA_CONTENT, header=None)
cites = pd.read_csv(CORA_CITES, header=None)

SUBJECT_TO_ID = {
    "Neural_Networks": 0,
    "Rule_Learning": 1,
    "Reinforcement_Learning": 2,
    "Probabilistic_Methods": 3,
    "Theory": 4,
    "Genetic_Algorithms": 5,
    "Case_Based": 6,
}

nodes = pd.DataFrame().assign(
    nodeId=content[0],
    labels="Paper",
    subject=content[1].replace(SUBJECT_TO_ID),
    features=content.iloc[:, 2:].apply(list, axis=1),
)

dir_relationships = pd.DataFrame().assign(sourceNodeId=cites[0], targetNodeId=cites[1], relationshipType="CITES")
inv_relationships = pd.DataFrame().assign(sourceNodeId=cites[1], targetNodeId=cites[0], relationshipType="CITES")

relationships = pd.concat([dir_relationships, inv_relationships]).drop_duplicates()

G = gds.graph.construct("cora-graph", nodes, relationships)
print("PRINTING GRAPHS")
print(gds.graph.list())
print("############################")

gds.graph.nodeProperties.stream(G, ["subject"]).head(10)


###