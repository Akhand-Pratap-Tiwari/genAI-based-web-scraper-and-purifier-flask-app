from purifier import get_purified_articles
import os
from scraper import get_raw_articles
from flask import Flask
import logging
import sys
import json
from embeddings_generator import get_embeddings
from parallel_requests import post_articles_in_parallel

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)


app = Flask(__name__)

# Set up basic logging to help track errors
logging.basicConfig(level=logging.INFO)

def run_scraper():
    print("run_scraper...")
    raw_articles = get_raw_articles()
    return raw_articles


def run_chunkifier(raw_articles):
    print("run_chunkifier...")
    raw_articles_chunks = []
    n = len(raw_articles)
    i = 0
    while (i <= n-1):
        if i+2 <= n-1:
            raw_articles_chunks.append(raw_articles[i:i+3])
        else:
            raw_articles_chunks.append(raw_articles[i:])
        i += 3
    return raw_articles_chunks


def dechunkifier(chunkified_jsons):
    print("dechunkifier...")
    purified_articles_json = {
        "list_of_news": []
    }
    for news_list_json in chunkified_jsons:
        purified_articles_json["list_of_news"].extend(
            news_list_json["list_of_news"])
    return purified_articles_json


def run_purifier(raw_articles_chunks):
    print("run_purifier...")
    purified_articles_chunkified_jsons = []
    currResponseTxt = ""
    chat_session = None
    for raw_article_chunk in raw_articles_chunks:
        try:
            response, chat_session = get_purified_articles(raw_article_chunk, chat_session)
            currResponseTxt = response.text
            purified_article_json_chunk = json.loads(currResponseTxt)
            purified_articles_chunkified_jsons.append(purified_article_json_chunk)
        except Exception as e:
            print(f"Error: ", e, f"with article chunk: {currResponseTxt[0:20]}")
            continue

    purified_articles_json = dechunkifier(purified_articles_chunkified_jsons)
    return purified_articles_json


@app.route("/")
def coordinator():
    print("coordinator...")
    raw_articles_list = run_scraper()
    raw_articles_list_chunkified = run_chunkifier(raw_articles_list)
    print("Length of raw_articles_list_chunkified", len(raw_articles_list_chunkified))
    for chunk in raw_articles_list_chunkified:
        print("Length of chunk: ", len(chunk))
    purified_articles_json = run_purifier(raw_articles_list_chunkified)
    
    print("json_len", len(purified_articles_json))
    print("final_news_len", len(purified_articles_json["list_of_news"]))

    for article_json in purified_articles_json["list_of_news"]:
        embedding = get_embeddings(article_json["description"])
        if(embedding is not None):
            article_json["embedding"] = embedding
        else:
            article_json["embedding"] = []

    purified_articles_json = purified_articles_json["list_of_news"] 
    
    with open('purified_articles.json', 'w') as f:
        json.dump(purified_articles_json, f)
        # name = os.environ.get("NAME", "World")
        # return f"Hello {name}!"
    
    post_articles_in_parallel(purified_articles_json, 2)


if __name__ == "__main__":
    coordinator()
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
