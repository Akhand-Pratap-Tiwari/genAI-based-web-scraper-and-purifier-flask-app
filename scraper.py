def thehackernews_parser(url):
    raw_news_list = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("a", class_="story-link")
        for article in articles:
            try:
                article_url = article["href"]
                article_response = requests.get(article_url)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, "html.parser")
                raw_news_list.append(article_soup.get_text())
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
    return raw_news_list

def cybersecuritynews_parser(url):
    raw_news_list = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("div", {"class": "item-details"})
        articles = [article.find("a") for article in articles]
        articles = articles[1:12]

        for article in articles:
            try:
                article_url = article["href"]
                article_response = requests.get(article_url)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, "html.parser")
                raw_news_list.append(article_soup.get_text())
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
    return raw_news_list

def wired_parser(url):
    raw_news_list = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("a", class_="summary-item__hed-link")
        articles = articles[1:20]
        for article in articles:
            try:
                article_url = article["href"]
                article_response = requests.get("https://www.wired.com" + article_url)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, "html.parser")
                raw_news_list.append(article_soup.get_text())
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
    return raw_news_list
