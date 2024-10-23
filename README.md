# Find the Shortest Path

A very simple (and honestly pretty solved question) is what is the shortest path between two stations on the New York City Subway?

Instead of using google or apple maps, I set out on an arduous journey to recreate one of those apps using Neo4j as the database layer of my application. 

**What was hard?** Getting the data, building the flask app, hosting it online.

**What was easy?** Using Neo4j as a database and running algorithms on top of the that database to calculate the shortest path. 

## Running this Demo

You have two basic options.

***Option 1: Just go to the website*** 

Go to my [website](https://www.corydonbaylor.com/examples/nyc/) and just view it there.

***Option 2: venv and python3*** 

Create a file called `.env` in the base of this repo after cloning and put in the credentials there. 

Then you can just run: 

```bash
python -m venv venv # create a venv
source venv/bin/activate
pip install -r requirements.txt
```

And finally,

```
python3 run.py
```

***Option 3: Docker***

If you would rather build a docker image:

```
docker build -t flask .  
docker run -p 5001:5001 flask
```

I am using port 5001 because of collisions I routinely get on macos. 

## Running Dijkstra's Shortest Path Algorithm

Once I had my data loaded into Neo4j, it was incredibly easy to create a projection and then run an algorithm against it. You can see how I loaded the data into Neo4j below. Maybe one day I will do a write up of the webscrapping and cleaning needed to get the data but that day is not today.

My data is set up where nodes are the subway stations, and the relationships are the lines that connect them. The relationships have a label of `CONNECTS_TO`. 

Here is how you create a projection (which we do on aura DS). 

```cypher
CALL gds.graph.project(
  'subway_graph',
  'Station',
  {
    CONNECTS_TO: {
      orientation: 'UNDIRECTED',
      properties: ['length']
    }
  }
)
```

And then in my python code, I used the driver to connect to my aura DS instance.

```python
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
```

I then created a function that would run a cypher query:

```python
def get_shortest_path(tx, start_station, end_station):
    query = """
    MATCH (start:Station {name: $start_name}), (end:Station {name: $end_name})
    CALL gds.shortestPath.dijkstra.stream('subway_graph', {
      sourceNode: id(start),
      targetNode: id(end),
      relationshipWeightProperty: 'length'
    })
    YIELD path
    RETURN [node in nodes(path) | {
      name: node.name,
      latitude: node.latitude,
      longitude: node.longitude
    }] AS stations
    """
    result = tx.run(query, start_name=start_station, end_name=end_station)
    return result.single()
```

Let's break down that cypher query:

- `MATCH (start:Station {name: $start_name}), (end:Station {name: $end_name})` &mdash; This line matches two nodes in the graph with the label 'Station'. It finds the start station using the parameter `$start_name` and the end station using `$end_name`.

- `CALL gds.shortestPath.dijkstra.stream('subway_graph', {...})` &mdash; This calls the Dijkstra's shortest path algorithm from the GDS library. It's run on the graph projection named 'subway_graph' that we created on our instance of Aura DS. 
  - `sourceNode: id(start)`  &mdash; The starting point of the path, using the ID of the start station.
  - `targetNode: id(end)` &mdash; The endpoint of the path, using the ID of the end station.
  - `relationshipWeightProperty: 'length'` &mdash; Uses a property named 'length' on the relationships to determine the weight (distance) between stations.

- `YIELD path` &mdash; This returns the path found by the algorithm.

- `RETURN [node in nodes(path) | {...}] AS stations`  &mdash; This creates a list comprehension over all nodes in the path. The result is returned as a dictionary which is used by python to plot stations on a leaflet map.

Ok now that we got our cypher query figured out. How do we make the results useful in our app?

```python
with driver.session() as session:
    result = session.read_transaction(get_shortest_path, start, end)

if result:
    return render_template('map.html', 
                           start_station=start, 
                           end_station=end, 
                           stations=result["stations"])
else:
    return render_template('map_index.html', error="No path found between the specified stations")
```

So what's this do?

- That first chunk actually calls our query and saves the results into a variable called `result`
- The `if/else` block passes the results of our query into a template which will then be used to populate a leaflet map, and if no path is found than to return an error

## Loading into Neo4j

Unforunately, I was not starting with a clean CSV. Instead, I scrapped my subway data&mdash; from [here](https://new.mta.info/maps/subway-line-maps) and [here](https://catalog.data.gov/dataset/mta-subway-stations)&mdash; and munged it into two csvs which looked something like the below:

**stations.csv**

| id   | name                   | lat       | Long       |
| ---- | ---------------------- | --------- | ---------- |
| 1    | Van Cortlandt Park-242 | 40.889248 | -73.898583 |
| 2    | 238 St                 | 40.884667 | -73.90087  |
| 3    | 231 St                 | 40.878856 | -73.904834 |

**lines.csv**

| from_station_id | from_station_name      | to_station_id | to_station_name    | line_name | stop_order | Distance |
| --------------- | ---------------------- | ------------- | ------------------ | --------- | ---------- | -------- |
| 1               | Van Cortlandt Park-242 | 2             | 238 St             | 1 Train   | 1          | 4        |
| 2               | 238 St                 | 3             | 231 St             | 1 Train   | 2          | 3        |
| 3               | 231 St                 | 4             | Marble Hill-225 St | 1 Train   | 3          | 1        |

I was able to quickly load it into Neo4j like so:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///stations.csv' AS row
CREATE (s:Station {
  id: toInteger(row.id),
  name: row.name,
  stopName: row['Stop Name'],
  borough: row.Borough,
  daytimeRoutes: row['Daytime Routes'],
  latitude: toFloat(row.Latitude),
  longitude: toFloat(row.Longitude),
  georeference: row.Georeference
})
```

```cypher
LOAD CSV WITH HEADERS FROM 'file:///lines.csv' AS row
MATCH (from:Station {id: toInteger(row.from_station_id)})
MATCH (to:Station {id: toInteger(row.to_station_id)})
MERGE (from)-[r1:CONNECTS_TO {
  lineName: row.line_name,
  stopOrder: toInteger(row.stop_order),
  length: toFloat(row.length)
}]->(to)
MERGE (to)-[r2:CONNECTS_TO {
  lineName: row.line_name,
  stopOrder: toInteger(row.stop_order),
  length: toFloat(row.length)
}]->(from)
```

