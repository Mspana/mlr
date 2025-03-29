import os
import json
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def encode_image(image_path):
    """
    Encode an image file to base64 for API transmission
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path):
    """
    Send an image to Google Gemini API for analysis
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: JSON response with extracted text and issues
    """
    try:
        # Create the prompt for analysis
        prompt = """
        You are analyzing a promotional document.  
        - Extract all text from this image.  
        - Check for **spelling and grammar issues**.  
        - Identify **formatting errors** (e.g., incorrect brand usage, missing disclaimers).  
        - Return results in structured JSON format:
          {
            "text_extracted": "...",
            "spelling_grammar_issues": [{"text": "wrongly spelled word", "suggestion": "correct spelling"}],
            "formatting_issues": [{"text": "BrandX should be BrandX™", "suggestion": "Use BrandX™"}]
          }
        """
        
        # Generate content using the model
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=[
                prompt,
                {"inline_data": {"mime_type": "image/jpeg", "data": encode_image(image_path)}}
            ]
        )
        
        # Extract the JSON from the response
        response_text = response.text
        
        # Sometimes the API returns the JSON with markdown code blocks, so we need to clean it
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        # Parse the JSON response
        result = json.loads(response_text)
        
        return result
    
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        # Return a default structure in case of error
        return {
            "text_extracted": "",
            "spelling_grammar_issues": [],
            "formatting_issues": [],
            "error": str(e)
        } 