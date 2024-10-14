import os
from scraper import get_raw_articles
from flask import Flask
import asyncio
import aiohttp
import logging
import sys 

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)

import cosmocloud_api_details as cosmo_secs
from purifier import get_purified_articles
 
app = Flask(__name__)

# Set up basic logging to help track errors
logging.basicConfig(level=logging.INFO)

headersList = {
 "environmentId": cosmo_secs.environmentId,
 "projectId": cosmo_secs.projectId,
}

postURL = "https://free-ap-south-1.cosmocloud.io/development/api/articles_raw"

# if __name__ == "__main__":
#     raw_news_list = start_scraper()
#     payloads = [{'raw_article': article} for article in raw_news_list]
#     # print("Raw article size: ", len(raw_news_list))
    

#     # Create a semaphore (limit the number of concurrent requests)
#     # Limit the number of concurrent requests with a semaphore
#     semaphore = asyncio.Semaphore(3)  # Adjust the limit based on your needs

#     async def fetch_article_data(session, url, headers, payload):
#         async with semaphore:
#             try:
#                 async with session.post(url, json=payload, headers=headers) as response:
#                     response.raise_for_status()  # Raise an error for non-200 HTTP codes
#                     purified_data = await response.text()  # Assuming text format response
#                     return purified_data
#             except aiohttp.ClientError as e:
#                 logging.error(f"Request failed for payload {payload}: {e}")
#                 return None

#     async def main():
#         purified_news_list = []
#         async with aiohttp.ClientSession() as session:
#             # Create tasks for all requests
#             tasks = [fetch_article_data(session, postURL, headersList, payload) for payload in payloads]

#             # Run tasks concurrently, limiting concurrency
#             for task in asyncio.as_completed(tasks):
#                 purified_data = await task
#                 if purified_data is not None:
#                     purified_news_list.append(purified_data)

#         return purified_news_list

#     # Run the event loop and execute the main function
#     purified_news_list = asyncio.run(main())

#     print(purified_news_list)
#     print("purified size: ", len(purified_news_list))
#     print("Raw article size: ", len(payloads))


import json
@app.route("/")
def run_scraper():
  print("Loading...")
  raw_articels = get_raw_articles()
  raw_articels_chunks = []
  n = len(raw_articels)
  for i in range(n):
    if i+4 <= n-1:
      raw_articels_chunks.append(raw_articels[i:i+5])
    else:
      raw_articels_chunks.append(raw_articels[i:])
    i += 5

  purified_articles = []
  
  for raw_article_chunk in raw_articels_chunks:
    purified_articles.append(get_purified_articles(raw_article_chunk))
  
  # get_purified_articles(raw_articels)
  # print(purified_articles)
  with open('purified_articles.json', 'w') as f:
    print(purified_articles[0])
    for purified_article in purified_articles:
      json.dump(purified_article, f)
  
  # name = os.environ.get("NAME", "World")
  # return f"Hello {name}!"

if __name__ == "__main__":
  run_scraper()
  # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))