def find_links(soup):
    # Find all <a> tags (which represent hyperlinks)
    links = soup.find_all('a')

    # empty list for cleaned lines
    subways = []

    # Extract and print only the links that start with the desired prefix
    for link in links:
        href = link.get('href')
        if href:
            # Check if it's a relative URL and prepend the base URL if necessary
            if href.startswith('/'):
                href = f"https://new.mta.info{href}"
            
            # Check if the link starts with the desired prefix
            if href.startswith("https://new.mta.info/maps/subway-line-maps/"):
                subways.append(href)
    return subways