import os
import asyncio
import aiohttp
import sys
from tqdm import tqdm

secrets_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(secrets_path)
import cosmocloud_api_details as cosmo_secs

headers = cosmo_secs.headers
url = cosmo_secs.url

async def post_article(session, url, headers, payload, semaphore, timeout=60):
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
            async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
                response.raise_for_status()  # Raise an error for non-200 HTTP codes
                article_id = await response.text()  # Assuming text format response
                return article_id
        except Exception as e:
            print(f"Request failed for payload: {payload['headline']}: {e}")
            return None

async def run_async_posting(payloads, semaphore, timeout=60):
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
        # print()
        tasks = []
        for payload in tqdm(payloads, desc="Constructing Async Tasks"):
            tasks.append(post_article(session, url, headers, payload, semaphore, timeout))

        # Run tasks concurrently, limiting concurrency
        for task in tqdm(asyncio.as_completed(tasks), desc="Running Async Tasks"):
            article_id = await task
            if article_id is not None:
                article_ids.append(article_id)

    return article_ids

def post_articles_in_parallel(purified_articles_jsons, limit=1, timeout=60):
    """
    Posts a list of articles in parallel and prints statistics.

    Args:
        purified_articles_jsons: A list of article JSON data.
        limit: The maximum number of concurrent requests.

    Returns:
        A list of article IDs for successfully posted articles.
    """
    # Filter articles with embeddings
    payloads = []
    for article_json in tqdm(purified_articles_jsons, desc="Constructing Payloads"):
        if article_json.get("embedding"):
            payloads.append(article_json)

    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(limit)

    # Run the event loop and execute the main function
    article_ids = asyncio.run(run_async_posting(payloads, semaphore, timeout))

    # print(purified_news_list)
    len_paj = len(purified_articles_jsons)
    len_pylds = len(payloads)
    len_aids = len(article_ids)

    print("Total Articles: ", len_paj)
    print("Successfully posted articles: ", len_aids)
    print("Articles with no embeddings (not considered for posting): ", len_paj - len_pylds)
    print("Unsuccessfully posted articles (articles posting attempted but failed): ", len_pylds - len_aids)

    return article_ids
