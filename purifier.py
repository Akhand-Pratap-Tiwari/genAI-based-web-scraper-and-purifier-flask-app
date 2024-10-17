# Suggested code may be subject to a license. Learn more: ~LicenseLog:312977066.
import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import sys
# Get the absolute path to the 'secrets' directory
secrets_path = os.path.abspath(os.path.join('secrets'))
# Add the 'secrets' directory to the system path
sys.path.append(secrets_path)
# Import the gemini_api_key module
import gemini_api_details as gemini_secs
# Configure the Google Generative AI library with the API key
genai.configure(api_key=gemini_secs.gemini_api_key)

# Create the model
# This configuration defines the behavior of the Gemini model.
# Parameters like temperature, top_p, and top_k control the creativity and randomness of the output.
# max_output_tokens limits the length of the generated text.
# response_schema enforces a specific JSON structure for the model's output.
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
    required = ["list_of_news"],
    properties = {
      "list_of_news": content.Schema(
        type = content.Type.ARRAY,
        items = content.Schema(
          type = content.Type.OBJECT,
          enum = [],
          required = ["headline", "summary", "description"],
          properties = {
            "headline": content.Schema(
              type = content.Type.STRING,
            ),
            "summary": content.Schema(
              type = content.Type.STRING,
            ),
            "description": content.Schema(
              type = content.Type.STRING,
            ),
            "date": content.Schema(
              type = content.Type.STRING,
            ),
          },
        ),
      ),
    },
  ),
  "response_mime_type": "application/json",
}

# Initialize the GenerativeModel instance
# model_name specifies the Gemini model to use (gemini-1.5-flash in this case).
# safety_settings configure the model's safety filters to mitigate harmful content.
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH
    }
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Define the prompt for the model
# This prompt instructs the model to extract and purify cybersecurity news from raw HTML content.
# It specifies the desired format and operations to perform on the input.
prompt = "Following is a list of cybersecurity news extracted in a raw html format from a website. Your task is to extract only the useful content i.e., cybersecurity news from it. Perform following operations on it:\n1- Remove all the redundant non-human-readable/illegible characters from it like: \"\\n\", \"\\t\", \"\\u00xyz\" etc.\n2- Remove all the promotional content like: \"All rights reserved\", \"Subscribe\", \"Follow my page\", etc.\n3- There are multiple news it. Extract and list them separately.\n4- For each of the purified and extracted news define following:\n a- headline: 1 liner Headline/Highlight of the news.\n   b- summary: 2 liner summary of the news that uniquely defines the incident.\n   c- description: The description of the news compressed/explained in less than 1500 words. \n   d- date: The date at which the incident occurred. If not found then return NULL.\n5- Also don't list or remove any promotional article/news from the list.\n6- Finally return the output in the json format.\nFollowing is the list of raw html news:\n"

# Function to get purified articles from raw HTML using the Gemini model
def get_purified_articles(raw_articels, chat_session):
    """
    Purifies raw HTML articles using the Gemini model.
    
    Args:
        raw_articels: The raw HTML content containing cybersecurity news.
        chat_session: An existing chat session with the Gemini model (optional).
    Returns:
        A tuple containing the model's response and the chat session.
    """
    if chat_session is None:
        chat_session = model.start_chat()  # Start a new chat session if none is provided
    response = chat_session.send_message(prompt + str(raw_articels))  # Send the prompt and raw articles to the model
    return response, chat_session  # Return the response and the chat session

# print(response.text)