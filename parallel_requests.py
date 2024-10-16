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
    payloads = [purified_article_json for purified_article_json in purified_articles_jsons if len(
        purified_article_json["embedding"]) != 0]

    # Limit the number of concurrent requests with a semaphore
    semaphore = asyncio.Semaphore(limit)

    # Run the event loop and execute the main function
    article_ids = asyncio.run(post_articles_get_ids_parallel(payloads))

    # print(purified_news_list)
    print("Total Articles: ", len(purified_articles_jsons))
    print("Articles with no embeddings: ", len(
        purified_articles_jsons) - len(payloads))
    print("Successfully posted articles: ", len(article_ids))
    print("Unsuccessfully posted articles:", len(payloads) - len(article_ids))

    return article_ids
