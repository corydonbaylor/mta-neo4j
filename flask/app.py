from flask import Flask, request, render_template
from neo4j import GraphDatabase
from fuzzywuzzy import process

app = Flask(__name__)

# Neo4j connection details
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def load_stations_from_file(filename='stations.txt'):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]

all_stations = load_stations_from_file()

def get_shortest_path(tx, start_station, end_station):
    query = """
    MATCH (start:Station {name: $start_name}), (end:Station {name: $end_name})
    CALL gds.shortestPath.dijkstra.stream('subway_graph', {
      sourceNode: id(start),
      targetNode: id(end),
      relationshipWeightProperty: 'length'
    })
    YIELD path
    RETURN [node in nodes(path) | node.name] AS stations,
           [rel in relationships(path) | type(rel)] AS lines,
           reduce(s = 0, r in relationships(path) | s + r.length) AS totalDistance
    """
    result = tx.run(query, start_name=start_station, end_name=end_station)
    return result.single()

def get_station_suggestions(input_name, limit=5):
    return process.extract(input_name, all_stations, limit=limit)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shortest_path', methods=['GET'])
def shortest_path():
    start = request.args.get('start')
    end = request.args.get('end')
    
    if not start or not end:
        return render_template('index.html', error="Please provide both start and end stations")

    if start not in all_stations:
        start_suggestions = get_station_suggestions(start)
        return render_template('index.html', error=f"Start station '{start}' not found", start_suggestions=start_suggestions)
    
    if end not in all_stations:
        end_suggestions = get_station_suggestions(end)
        return render_template('index.html', error=f"End station '{end}' not found", end_suggestions=end_suggestions)
    
    with driver.session() as session:
        result = session.read_transaction(get_shortest_path, start, end)
    
    if result:
        return render_template('index.html', result={
            "stations": result["stations"],
            "lines": result["lines"],
            "total_distance": result["totalDistance"]
        })
    else:
        return render_template('index.html', error="No path found between the specified stations")

if __name__ == '__main__':
    app.run(debug=True, port=5001)