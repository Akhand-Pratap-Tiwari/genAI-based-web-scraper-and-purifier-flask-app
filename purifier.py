import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import sys

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)

import gemini_api_key as gemini_secs 
# gemini_api_key = os.environ["GEMINI_API_KEY"]
gemini_api_key = gemini_secs.gemini_api_key

genai.configure(api_key=gemini_api_key)

# Create the model
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

prompt = "Following is a list of cybersecurity news extracted in a raw html format from a website. Your task is to extract only the useful content i.e., cybersecurity news from it. Perform following operations on it:\n1- Remove all the redundant non-human-readable/illegible characters from it like: \"\\n\", \"\\t\", \"\\u00xyz\" etc.\n2- Remove all the promotional content like: \"All rights reserved\", \"Subscribe\", \"Follow my page\", etc.\n3- There are multiple news it. Extract and list them separately.\n4- For each of the purified and extracted news define following:\n a- headline: 1 liner Headline/Highlight of the news.\n   b- summary: 2 liner summary of the news that uniquely defines the incident.\n   c- description: The actual description of the news, shorten/summarized such that it remains strictly less than 8000 bytes. \n   d- date: The date at which the incident occurred. If not found then return NULL. \n5- Finally return the output in the json format.\n\nFollowing is the list of raw html news:\n"


def get_purified_articles(raw_articels):
    chat_session = model.start_chat()
    response = chat_session.send_message(prompt + str(raw_articels))
    return response

# print(response.text)