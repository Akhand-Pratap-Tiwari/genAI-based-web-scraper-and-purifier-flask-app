## Flask API Service Starter

This is a minimal Flask API service starter based on [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).

## Getting Started

Server should run automatically when starting a workspace. To run manually, run:
```sh
./devserver.sh
```

## What this do?
This flask app does following in order:
- Scrap raw content from several cybersecurity websites.
- Purify the raw content using Gemini API.
- Write the purified content to MongoDB using Cosmocloud API and to the local JSON file as well.

## File and Folder Descriptions:
- `.idx` contains `dev.nix` file that defines the state of Google IDX workspace.
- `.vscode` contains `settings.json` file that has some formatting settings for the code.
- `secrets` contains following two files:
  - `cosmocloud_api_details.py` which has deatils related to the cosmocloud api service.
  - `gemini_api_details.py` which has details related to the gemini api service.
- `devserver.sh` contains server startup code.
- `embeddings_generator.py` contains code to generate embeddings for a given text.
- `main.py` contains the main runner code and flask api code.
- `parallel_requests.py` contains the code to post the purified articles to cosmocloud concurrently.
- `purifier.py` contains the code to purify the raw document using gemini API.
- `scraper.py` contains the code to scrape the cybersecurity websites and return the list of raw content.

## How to run:
- First set up your MongoDB and Cosmocloud connection.
- During Cosmocloud setup use the following schema:
  ```
  {
	  "description": "STRING",
	  "headline": "STRING",
	  "summary": "STRING",
	  "date": "STRING",
	  "embedding": [2.0, 3.0, -4.5]
  }
  ```
  Notice that `embedding` field is List of floats
- Get the api details for Cosmocloud and Gemini API.
- Put the api details into the appropriate files as described in previous section (make sure to not make them public).
- Install all requirements mentioned in `requirements.txt`
- Run `main.py`.
- Now, send a POST request to `http://your_flask_app_address:your_port/start_coordinator`
- Server will start working and you can see the stats on the server cmd.
- Purified articles will be generated and written locally on a json while the same are also written to MongoDB.

## How to run on Google IDX:
- Open IDX and Fork this repo.
- Rebuild the environment if necessary.
- Now, follow the same steps as mentioned in previous section.

### NOTE: On IDX you might want to use virtual environment for pip packages installation.
