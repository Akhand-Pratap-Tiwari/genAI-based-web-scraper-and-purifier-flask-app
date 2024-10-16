import cosmocloud_api_details as cosmo_secs
import os
import asyncio
import aiohttp
import logging
import sys

secrets_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(secrets_path)

headers = cosmo_secs.headers
url = cosmo_secs.url

async def post_article(session, url, headers, payload, semaphore):
    """
    Sends a POST request to the specified URL with the given payload.

    Args:
        session: The aiohttp ClientSession object.
        url: The target URL for the POST request.
        headers: The headers to include in the request.
        payload: The JSON data to send in the request body.
        semaphore: An asyncio Semaphore to limit concurrency.

    Returns:
        The article ID if the request is successful, otherwise None.
    """
    async with semaphore:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()  # Raise an error for non-200 HTTP codes
                article_id = await response.text()  # Assuming text format response
                return article_id
        except aiohttp.ClientError as e:
            logging.error(f"Request failed for payload {payload}: {e}")
            return None

async def post_articles_get_ids_parallel(payloads):
    """
    Posts multiple articles in parallel and retrieves their IDs.

    Args:
        payloads: A list of article payloads to be posted.

    Returns:
        A list of article IDs for successfully posted articles.
    """
    article_ids = []
    async with aiohttp.ClientSession() as session:
        # Create tasks for all requests
        tasks = [post_article(session, url, headers, payload, semaphore)
                 for payload in payloads]

        # Run tasks concurrently, limiting concurrency
        for task in asyncio.as_completed(tasks):
            article_id = await task
            if article_id is not None:
                article_ids.append(article_id)

    return article_ids

def post_articles_in_parallel(purified_articles_jsons, limit=1):
    """
    Posts a list of articles in parallel and prints statistics.

    Args:
        purified_articles_jsons: A list of article JSON data.
        limit: The maximum number of concurrent requests.

    Returns:
        A list of article IDs for successfully posted articles.
    """
    # Filter articles with embeddings
    payloads = [article for article in purified_articles_jsons if article.get("embedding")]

    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(limit)

    # Run the event loop and execute the main function
    article_ids = asyncio.run(post_articles_get_ids_parallel(payloads))

    # print(purified_news_list)
    len_paj = len(purified_articles_jsons)
    len_pylds = len(payloads)
    len_aids = len(article_ids)
    print("Total Articles: ", len_paj)
    print("Articles with no embeddings: ", len_paj - len_pylds)
    print("Successfully posted articles: ", len_aids)
    print("Unsuccessfully posted articles:", len_pylds - len_aids)

    return article_ids
