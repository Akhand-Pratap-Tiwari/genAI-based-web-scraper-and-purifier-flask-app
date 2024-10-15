import google.generativeai as genai
import os
import sys

custom_module_path = os.path.abspath(os.path.join('secrets'))
sys.path.append(custom_module_path)

import gemini_api_key as gemini_secs

gemini_api_key = gemini_secs.gemini_api_key

genai.configure(api_key=gemini_api_key)

def get_embeddings(text):
    response = {}
    try:
        response = genai.embed_content(model="models/text-embedding-004", content=text,task_type="retrieval_document")
    except Exception as e:
        print(e)
        return None
    else:
        return response['embedding']
