# Suggested code may be subject to a license. Learn more: ~LicenseLog:420741354.
# Suggested code may be subject to a license. Learn more: ~LicenseLog:2787885186.
# Suggested code may be subject to a license. Learn more: ~LicenseLog:2172984445.
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
    
def thehackernews_links_extractor(soup):
    article_links = soup.find_all("a", class_="story-link")
    article_links = [article["href"] for article in article_links]
    return article_links

def cybersecuritynews_links_extractor(soup):
    article_links = soup.find_all("div", {"class": "item-details"})
    article_links = [article.find("a") for article in article_links]
    article_links = article_links[1:12]
    article_links = [article["href"] for article in article_links]
    return article_links

def wired_links_extractor(soup):
    articles_links = soup.find_all("a", class_="summary-item__hed-link")
    articles_links = articles_links[1:20]
    articles_links = ["https://www.wired.com" + article["href"] for article in articles_links]
    return articles_links

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
    news_websites = [
        ["thehackernews.com", "https://thehackernews.com/", thehackernews_links_extractor],
        ["cybersecuritynews.com", "https://cybersecuritynews.com/", cybersecuritynews_links_extractor],
        ["wired.com", "https://www.wired.com/category/security/", wired_links_extractor]
    ]

    raw_news_list = []

    for website_name, website_url, link_extractor_func in news_websites:
        try:
            scraped_raw_articles = news_scraper(website_name, website_url, link_extractor_func)
            raw_news_list.extend(scraped_raw_articles)
        except Exception as e:
            print(f"Error scraping {website_url}: {e}")
    
    print("No. of articles scraped: ", len(raw_news_list))
    return raw_news_list