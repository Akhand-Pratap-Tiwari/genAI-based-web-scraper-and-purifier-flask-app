import requests
from bs4 import BeautifulSoup

def get_website_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
        return None

def get_article_text(article_url):
    try:
        article_response = requests.get(article_url)
        article_response.raise_for_status()
        article_soup = BeautifulSoup(article_response.content, "html.parser")
        return article_soup.get_text()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article: {e}")
        return None
    
def thehackernews_parser(soup):
    articles = soup.find_all("a", class_="story-link")
    articles = [article["href"] for article in articles]
    return articles

def cybersecuritynews_parser(soup):
    articles = soup.find_all("div", {"class": "item-details"})
    articles = [article.find("a") for article in articles]
    articles = articles[1:12]
    articles = [article["href"] for article in articles]
    return articles

def wired_parser(soup):
    articles = soup.find_all("a", class_="summary-item__hed-link")
    articles = articles[1:20]
    articles = ["https://www.wired.com" + article["href"] for article in articles]
    return articles

def news_scraper(website_name, url, article_link_scraper_func):
    raw_news_list = []
    try:
        soup = get_website_soup(url)
        if(soup is None):
            raw_news_list = [f"{website_name} returned None"]
            return raw_news_list

        article_url_list = article_link_scraper_func(soup)

        for article_url in article_url_list:
            try:
                raw_news_list.append(get_article_text(article_url))
            except requests.exceptions.RequestException as e:
                print(f"Error fetching article: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
    return raw_news_list

def get_raw_articles():
    news_websites = {
        "thehackernews.com": ["https://thehackernews.com/", thehackernews_parser],
        "cybersecuritynews.com": ["https://cybersecuritynews.com/", cybersecuritynews_parser],
        "wired.com": ["https://www.wired.com/category/security/", wired_parser]
    }

    raw_news_list = []

    for website_name, url_and_parser_func in news_websites.items():
        try:
            temp = news_scraper(website_name, url_and_parser_func[0], url_and_parser_func[1])
            # print("Length temp: ", len(temp))
            raw_news_list.extend(temp)
        except Exception as e:
            print(f"Error scraping {url_and_parser_func[0]}: {e}")
    
    # print(raw_news_list)
    return raw_news_list