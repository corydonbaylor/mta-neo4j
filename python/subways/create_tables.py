import pandas as pd

def create_tables(soup, train):
    # Find all tables with the specified class
    tables = soup.find_all('table', class_='mta-table-bordered')

    # List to store DataFrames for each table
    dfs = []

    for table in tables:
        # Find the nearest preceding h2 tag with class 'mta-text-4xl'
        table_name = table.find_previous('h2', class_='mta-text-4xl').text.strip()

        # Assign borough abbreviation based on table name
        if "Brooklyn" in table_name:
            borough = "Bk"
        elif "Queens" in table_name:
            borough = "Q"
        elif "Manhattan" in table_name:
            borough = "M"
        elif "Bronx" in table_name:
            borough = "Bx"
        else:
            borough = table_name

        # Extract column names
        columns = [th.text.strip() for th in table.find('thead').find_all('th')]

        # Extract data from the table
        data = []
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]
            data.append(row_data)

        # Create a DataFrame for this table
        df = pd.DataFrame(data, columns=columns)
        df.columns = ['station', 'entrance', 'platform', 'transfers', 'other']
        
        # Add the borough abbreviation as a new column
        df['borough'] = borough
        
        dfs.append(df)

    # Concatenate all DataFrames
    result_df = pd.concat(dfs, ignore_index=True)

    # Adding in the name of the service
    result_df['service'] = train
    result_df['stop'] = range(len(result_df))

    # Reorder columns to include borough
    result_df = result_df[["service", "station", "stop", "borough"]]

    print(result_df.columns.tolist())

    return result_df