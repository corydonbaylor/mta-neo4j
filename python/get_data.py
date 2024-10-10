import subways as sw 
import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL of the webpage you want to scrape
url = "https://new.mta.info/maps/subway-line-maps"

# Send a GET request to the URL
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# finds all the links 
links = sw.find_links(soup)

# empty list where all the data will go
all_df = []

for link in links:
    # for each link, get the soup
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # then get the train number
    service = sw.extract_train_name(soup)
    print(service)

    # create the table
    df = sw.create_tables(soup, service)
    all_df.append(df)

# put all the data in one df
final = pd.concat(all_df, ignore_index=True)
# save as a csv
final.to_csv('subway_data.csv', index=False)
