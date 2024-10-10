import pandas as pd
def create_tables(soup, train):
    # Find all tables with the specified class
    tables = soup.find_all('table', class_='mta-table-bordered')

    # List to store DataFrames for each table
    dfs = []

    for table in tables:
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
        df.columns = ['station', 'entrace', 'platform', 'transfers', 'other']
        dfs.append(df)

    # Concatenate all DataFrames
    result_df = pd.concat(dfs, ignore_index=True)
    print(result_df.columns.tolist())


    # adding in the name of the service
    result_df['service'] = train
    result_df = result_df[["service", "station"]]
    result_df['stop'] = range(len(result_df))


    print(result_df.columns.tolist())

    return result_df