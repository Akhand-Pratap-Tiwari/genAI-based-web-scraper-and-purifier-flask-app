from purifier import get_purified_articles
import os
from scraper import get_raw_articles
from flask import Flask
import logging
import sys
import json
from embeddings_generator import get_embeddings
from parallel_requests import post_articles_in_parallel
from tqdm import tqdm

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)


app = Flask(__name__)

# Set up basic logging to help track errors
logging.basicConfig(level=logging.INFO)

def run_scraper():
    print("Running Scraper...")
    raw_articles = get_raw_articles()
    return raw_articles

def chunkify(raw_articles, chunk_size=3):
    print("Running Chunkifier...")
    raw_articles_chunks = []
    n = len(raw_articles)
    for i in tqdm(range(0, n, chunk_size), desc="Constructing Raw Articles Chunks"):
        if i+chunk_size <= n:
            raw_articles_chunks.append(raw_articles[i:i+chunk_size])
        else:
            raw_articles_chunks.append(raw_articles[i:])
    return raw_articles_chunks

def dechunkify(chunkified_jsons):
    print("Running De-chunkifier...")
    purified_articles_json = {
        "list_of_news": []
    }
    for news_list_json in tqdm(chunkified_jsons, desc="Merging Purified Articles"):
        purified_articles_json["list_of_news"].extend(
            news_list_json["list_of_news"])
    return purified_articles_json


def run_purifier(raw_articles_chunks):
    print("Running Purifier...")
    purified_articles_chunkified_jsons = []
    currResponseTxt = ""
    chat_session = None
    for raw_article_chunk in tqdm(raw_articles_chunks, desc="Running Purifier on Chunks"):
        try:
            response, chat_session = get_purified_articles(raw_article_chunk, chat_session)
            currResponseTxt = response.text
            purified_article_json_chunk = json.loads(currResponseTxt)
            purified_articles_chunkified_jsons.append(purified_article_json_chunk)
        except Exception as e:
            print(f"Error: ", e, f"with article chunk: {currResponseTxt[0:30]}")
            continue

    return purified_articles_json

def generate_embeddings(purified_articles_jsons):
    print("Running Embeddings Generator...")
    for article_json in tqdm(purified_articles_jsons, desc="Generating Embeddings"):
        embedding = get_embeddings(article_json["description"])
        if(embedding is not None):
            article_json["embedding"] = embedding
        else:
            article_json["embedding"] = []
    return purified_articles_jsons

@app.route("/")
def coordinator():
    print("Running Coordinator...")
    
    # Get raw articles list
    raw_articles_list = run_scraper()
    print("No. of raw articles scraped: ", len(raw_articles_list))

    # Make it into chunks of 3 to process in batch
    # Reduces the number of requests to gemini API
    raw_articles_list_chunkified = chunkify(raw_articles_list, 3)
    print("Length of raw_articles_list_chunkified", len(raw_articles_list_chunkified))
    chunk_lengths = [len(chunk) for chunk in raw_articles_list_chunkified]
    print("Individual chunk lengths:", chunk_lengths)

    # Run Purifier to extract the required info in json format using gemini API
    # Return news in chunks to be merged later
    purified_articles_json_chunkified = run_purifier(raw_articles_list_chunkified)

    # Run dechunkifier to merge the json chunks into single list
    purified_articles_jsons = dechunkify(purified_articles_json_chunkified)
    purified_articles_jsons = purified_articles_jsons["list_of_news"]
    print("Number of Purified Artciles: ", len(purified_articles_jsons))

    # Generate embeddings for each article
    purified_articles_jsons = generate_embeddings(purified_articles_jsons)
    
    # Dump the final news list into a file
    with open('purified_articles.json', 'w') as f:
        json.dump(purified_articles_jsons, f)
    
    # Post all the news concurrently to the database
    post_articles_in_parallel(purified_articles_jsons, 2)


if __name__ == "__main__":
    coordinator()
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
