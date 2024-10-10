import pandas as pd
import csv

# Read the CSV file
df = pd.read_csv('subway_data.csv')

# Create a dictionary to store unique station IDs
station_ids = {}
current_id = 1

# Create a list to store the processed data for lines
lines_data = []

# Process the data
for index, row in df.iterrows():
    service = row['service']
    station = row['station']
    stop = row['stop']
    
    # Assign a unique ID to each station if it doesn't have one
    if station not in station_ids:
        station_ids[station] = current_id
        current_id += 1
    
    # Add the line data
    if stop > 0:  # We don't add a connection for the first stop
        prev_station = df.loc[index - 1, 'station']
        lines_data.append({
            'from_station_id': station_ids[prev_station],
            'from_station_name': prev_station,
            'to_station_id': station_ids[station],
            'to_station_name': station,
            'line_name': service,
            'stop_order': stop
        })

# Create stations CSV
with open('stations.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name'])
    for station, id in station_ids.items():
        writer.writerow([id, station])

# Create lines CSV
with open('lines.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['from_station_id', 'from_station_name', 'to_station_id', 'to_station_name', 'line_name', 'stop_order'])
    for line in lines_data:
        writer.writerow([
            line['from_station_id'],
            line['from_station_name'],
            line['to_station_id'],
            line['to_station_name'],
            line['line_name'],
            line['stop_order']
        ])

print("Processing complete. Check 'stations.csv' and 'lines.csv' for the results.")