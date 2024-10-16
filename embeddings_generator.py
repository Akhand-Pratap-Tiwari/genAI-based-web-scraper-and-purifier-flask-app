import google.generativeai as genai
import os
import sys
# Get the absolute path to the 'secrets' directory
custom_module_path = os.path.abspath(os.path.join('secrets'))
# Add the 'secrets' directory to the system path
sys.path.append(custom_module_path)
# Import the gemini_api_key module
import gemini_api_key as gemini_secs

# Configure the Google Generative AI library with the API key
genai.configure(api_key=gemini_secs.gemini_api_key)

def get_embeddings(text):
    """
    Generates embeddings for the given text using the Gemini API.

    Args:
        text: The text to generate embeddings for.

    Returns:
        The embeddings for the text, or None if an error occurred.
    """
    try:
        response = genai.embed_content(model="models/text-embedding-004", content=text, task_type="retrieval_document")
        return response['embedding']  # Return the embeddings directly
    except Exception as e:
        print(f"Error generating embeddings: {e}")  # Print error with details
        return None  # Return None on error
