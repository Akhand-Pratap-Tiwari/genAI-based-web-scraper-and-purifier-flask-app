# Suggested code may be subject to a license. Learn more: ~LicenseLog:420741354.
# Suggested code may be subject to a license. Learn more: ~LicenseLog:2787885186.
# Suggested code may be subject to a license. Learn more: ~LicenseLog:2172984445.
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List, Tuple, Callable

def get_website_soup(url):
    """Fetches the content of a website and parses it using BeautifulSoup.

    Args:
        url (str): The URL of the website to fetch.
    Returns:
        BeautifulSoup object: The parsed HTML content of the website.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching main page: {e}")
        return None

def get_article_text(article_url):
    """Fetches the content of an article and extracts its text using BeautifulSoup.

    Args:
        article_url (str): The URL of the article to fetch.
    Returns:
        str: The extracted text content of the article.
    """
    try:
        article_response = requests.get(article_url)
        article_response.raise_for_status()
        article_soup = BeautifulSoup(article_response.content, "html.parser")
        return article_soup.get_text()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article: {e}")
        return None
    
def thehackernews_links_extractor(soup) -> List[str]:
    """Extracts article links from the Hacker News website.

    Args:
        soup (BeautifulSoup object): The parsed HTML content of the website.
    Returns:
        List[str]: A list of article URLs.
    """
    article_links = soup.find_all("a", class_="story-link")
    article_links = [article["href"] for article in article_links]
    return article_links

def cybersecuritynews_links_extractor(soup) -> List[str]:
    """Extracts article links from the Cybersecurity News website.

    Args:
        soup (BeautifulSoup object): The parsed HTML content of the website.
    Returns:
        List[str]: A list of article URLs.
    """
    article_links = soup.find_all("div", {"class": "item-details"})
    article_links = [article.find("a") for article in article_links]
    return [article["href"] for article in article_links[1:12]]

def wired_links_extractor(soup) -> List[str]:
    """Extracts article links from the Wired website.

    Args:
        soup (BeautifulSoup object): The parsed HTML content of the website.
    Returns:
        List[str]: A list of article URLs.
    """
    article_links = soup.find_all("a", class_="summary-item__hed-link")[1:20]
    return ["https://www.wired.com" + article["href"] for article in article_links]

def news_scraper(website_name: str, url: str, article_link_scraper_func: Callable) -> List[str]:
    """Scrapes news articles from a given website.

    Returns a list of article texts, or a list containing an error message if the main page fetch fails.
    """
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

def get_raw_articles() -> List[str]:
    """Scrapes articles from multiple news websites.

    Returns a list of raw article texts.
    """
    news_websites = [
        ["thehackernews.com", "https://thehackernews.com/", thehackernews_links_extractor],
        ["cybersecuritynews.com", "https://cybersecuritynews.com/", cybersecuritynews_links_extractor],
        ["wired.com", "https://www.wired.com/category/security/", wired_links_extractor]
    ]

    raw_news_list = []

    for website_name, website_url, link_extractor_func in tqdm(news_websites, desc="Scraping Website"):
        try:
            scraped_raw_articles = news_scraper(website_name, website_url, link_extractor_func)
            raw_news_list.extend(scraped_raw_articles)
        except Exception as e:
            print(f"Error scraping {website_name}: {e}")
    return raw_news_list