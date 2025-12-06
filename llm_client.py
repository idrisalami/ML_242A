"""
LLM client module using Google's Gemini Flash model.
"""

import google.generativeai as genai
import time

# Configure the API key
# Note: In a production environment, it is safer to use os.environ.get("GOOGLE_API_KEY")
API_KEY = "AIzaSyA4BOepHGCFg150uLGCVshYXqawqVQKeV4"
genai.configure(api_key=API_KEY)

def call_llm(prompt: str) -> str:
    """
    Call Google's Gemini Flash model with the given prompt.
    
    Args:
        prompt: The formatted prompt string to send to the LLM
    
    Returns:
        The LLM's response as a string
        
    Raises:
        Exception: If the API call fails
    """
    try:
        # Use gemini-2.5-flash as requested
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Check if response was blocked or empty
        if not response.parts:
            if response.prompt_feedback:
                 raise ValueError(f"LLM response blocked: {response.prompt_feedback}")
            raise ValueError("LLM returned empty response")
            
        return response.text
        
    except Exception as e:
        # Simple retry logic could be added here if needed, 
        # but for now we propagate the error so the main loop handles it
        raise RuntimeError(f"Gemini API call failed: {str(e)}") from e
