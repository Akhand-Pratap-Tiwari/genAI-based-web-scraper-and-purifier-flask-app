from purifier import get_purified_articles
import os
from scraper import get_raw_articles
from flask import Flask, jsonify
import logging
import sys
import json
from embeddings_generator import get_embeddings
from parallel_requests import post_articles_in_parallel
from tqdm import tqdm
import datetime

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
    """
    Splits a list of raw articles into smaller chunks for batch processing.

    Args:
        raw_articles (list): List of raw articles.
        chunk_size (int, optional): The desired size of each chunk. Defaults to 3.

    Returns:
        list: A list of article chunks, where each chunk is a sublist of raw_articles.
    """
    print("Running Chunkifier...")
    raw_articles_chunks = []  # Initialize an empty list to store the chunks
    n = len(raw_articles)  # Get the total number of raw articles
    # Iterate through the raw articles with a step of chunk_size
    for i in tqdm(range(0, n, chunk_size), desc="Constructing Raw Articles Chunks"):
        raw_articles_chunks.append(raw_articles[i:i + chunk_size])  # Append a chunk to the list
    # Return the list of chunks
    return raw_articles_chunks

def dechunkify(chunkified_jsons):
    """
    Combines the chunkified JSONs back into a single JSON structure.

    Args:
        chunkified_jsons (list): List of JSON objects, each containing a list of news articles.

    Returns:
        dict: A single JSON object containing all the news articles.
    """
    print("Running De-chunkifier...")
    # Initialize an empty JSON structure to store all the articles
    purified_articles_json = {"list_of_news": []}
    # Iterate through each chunk and extend the main list with the articles from the chunk
    for news_list_json in tqdm(chunkified_jsons, desc="Merging Purified Articles"):
        purified_articles_json["list_of_news"].extend(news_list_json["list_of_news"])
    return purified_articles_json


def run_purifier(raw_articles_chunks):
    """
    Purifies raw articles using the get_purified_articles function.

    Args:
        raw_articles_chunks (list): List of raw article chunks.

    Returns:
        list: List of purified article JSON chunks.
    """
    print("Running Purifier...")
    purified_articles_chunkified_jsons = []
    current_response_text = ""  # Store the current response text for error handling
    chat_session = None  # Initialize chat session for potential use in get_purified_articles
    
    # Iterate through each chunk of raw articles
    for raw_article_chunk in tqdm(raw_articles_chunks, desc="Running Purifier on Chunks"):
        try:
            # Call get_purified_articles to process the chunk
            response, chat_session = get_purified_articles(raw_article_chunk, chat_session)
            current_response_text = response.text  # Store the response text
            # Convert the response text to JSON
            purified_article_json_chunk = json.loads(current_response_text) 
            # Append the purified JSON chunk to the list
            purified_articles_chunkified_jsons.append(purified_article_json_chunk)
        except Exception as e:
            print(f"Error: {e} with article chunk: {current_response_text[0:30]}") 
            continue  # Skip to the next chunk if an error occurs

    return purified_articles_chunkified_jsons

def generate_embeddings(purified_articles_jsons):
    """
    Generates embeddings for each article description using the get_embeddings function.

    Args:
        purified_articles_jsons (list): List of purified article JSON objects.

    Returns:
        list: List of purified article JSON objects with embeddings added.
    """
    print("Running Embeddings Generator...")
    unembedded_count = 0
    for article_json in tqdm(purified_articles_jsons, desc="Generating Embeddings"):
        # Get the embedding for the article description
        embedding = get_embeddings(article_json["description"])
        # Add the embedding to the article JSON
        article_json["embedding"] = embedding if embedding is not None else []  
        # Increment unembedded count if embedding generation failed
        unembedded_count += 1 if embedding is None else 0  
    print("Unsuccessful embeddings:", unembedded_count)
    print("Successful embeddings:", len(purified_articles_jsons) - unembedded_count)
    print("Total articles:", len(purified_articles_jsons))
    return purified_articles_jsons

@app.route("/start_coordinator", methods=["POST"])
def coordinator():
    """
    Main function to orchestrate the scraping, purifying, embedding, and posting of news articles.
    """
    print("Running Coordinator...")
    
    # 1. Scrape raw articles from the news website
    raw_articles_list = run_scraper()
    print("No. of raw articles scraped: ", len(raw_articles_list))

    # 2. Chunk the raw articles for batch processing to reduce API calls
    raw_articles_list_chunkified = chunkify(raw_articles_list, 3)
    print("Length of raw_articles_list_chunkified: ", len(raw_articles_list_chunkified))
    chunk_lengths = [len(chunk) for chunk in raw_articles_list_chunkified]
    print("Individual chunk lengths:", chunk_lengths)

    # 3. Purify the articles using the Gemini API to extract relevant information
    #    This step returns the purified articles in chunks.
    purified_articles_json_chunkified = run_purifier(raw_articles_list_chunkified)

    # 4. De-chunkify the purified articles to combine them into a single list
    purified_articles_jsons = dechunkify(purified_articles_json_chunkified)
    purified_articles_jsons = purified_articles_jsons["list_of_news"]
    print("Number of Purified Artciles: ", len(purified_articles_jsons))

    # 5. Generate embeddings for each purified article for semantic search
    purified_articles_jsons = generate_embeddings(purified_articles_jsons)
    
    # 6. Save the purified articles with embeddings to a JSON file
    # This is for debugging and caching purposes
    with open('purified_articles.json', 'w') as f:
        json.dump(purified_articles_jsons, f)
    
    # 7. Post the articles to the database in parallel for faster processing
    #    returns article_ids for successfully posted news articles
    post_articles_in_parallel(purified_articles_jsons, 2, 60)

    response = {
        'message': 'Scraping job done.',
        'job_timestamp': datetime.datetime.now()  # Optional job ID
    }

    return jsonify(response), 202




if __name__ == "__main__":
    # coordinator()
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
