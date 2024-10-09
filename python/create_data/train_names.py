def extract_train_name(soup):
    # Find the h1 tag within the div with class "mta-page-title"
    h1_tag = soup.find('div', class_='mta-page-title').find('h1')

    # Extract the text from the span within the h1 tag
    if h1_tag:
        span_tag = h1_tag.find('span')
        if span_tag:
            text = span_tag.text.strip()
            # Extract the train name (assuming it's always the first two words)
            train_name = ' '.join(text.split()[:2])

            # shuttle stuff needs to get fixed
            if train_name == "Line maps":
                train_name = "Shuttles"

            return train_name
        else:
            return "Span tag not found within h1"
    else:
        return "H1 tag not found"