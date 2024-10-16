import cosmocloud_api_details as cosmo_secs
import os
import asyncio
import aiohttp
import logging
import sys

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)

headersList = {
    "environmentId": cosmo_secs.environmentId,
    "projectId": cosmo_secs.projectId,
}

postURL = "https://free-ap-south-1.cosmocloud.io/development/api/articles_raw"

def post_articles_in_parallel(purified_articles_jsons):
    payloads = [purified_article_json for purified_article_json in purified_articles_jsons if len(purified_article_json["embedding"]) != 0]
    # print("Raw article size: ", len(raw_news_list))


    # Create a semaphore (limit the number of concurrent requests)
    # Limit the number of concurrent requests with a semaphore
    semaphore = asyncio.Semaphore(1)  # Adjust the limit based on your needs

    async def fetch_article_data(session, url, headers, payload):
        async with semaphore:
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    response.raise_for_status()  # Raise an error for non-200 HTTP codes
                    purified_data = await response.text()  # Assuming text format response
                    return purified_data
            except aiohttp.ClientError as e:
                logging.error(f"Request failed for payload {payload}: {e}")
                return None

    async def main():
        purified_news_list = []
        async with aiohttp.ClientSession() as session:
            # Create tasks for all requests
            tasks = [fetch_article_data(session, postURL, headersList, payload) for payload in payloads]

            # Run tasks concurrently, limiting concurrency
            for task in asyncio.as_completed(tasks):
                purified_data = await task
                if purified_data is not None:
                    purified_news_list.append(purified_data)

        return purified_news_list

    # Run the event loop and execute the main function
    purified_news_list = asyncio.run(main())

    # print(purified_news_list)
    print("purified size: ", len(purified_news_list))
    print("Raw article size: ", len(payloads))
