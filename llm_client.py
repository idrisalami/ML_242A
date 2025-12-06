"""
LLM client module using OpenAI's ChatGPT.
"""

from openai import OpenAI
import time
import random
import os

# Configure the API key from environment variable
# Set OPENAI_API_KEY environment variable before running
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running the pipeline.")

client = OpenAI(api_key=API_KEY)

def call_llm(prompt: str, retries: int = 5, initial_delay: float = 2.0) -> str:
    """
    Call OpenAI's ChatGPT model with the given prompt.
    Includes retry logic for rate limits.
    
    Args:
        prompt: The formatted prompt string to send to the LLM
        retries: Number of retries for rate limit errors
        initial_delay: Initial delay in seconds for backoff
    
    Returns:
        The LLM's response as a string
        
    Raises:
        Exception: If the API call fails
    """
    delay = initial_delay
    
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini for speed and cost efficiency
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},  # Force JSON output
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_str = str(e).lower()
            # Check for rate limit or server errors
            if "429" in error_str or "500" in error_str or "503" in error_str:
                if attempt < retries:
                    sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"OpenAI error {e}. Retrying in {sleep_time:.2f}s... (Attempt {attempt+1}/{retries})")
                    time.sleep(sleep_time)
                    continue
            
            # Raise for other errors or if retries exhausted
            raise RuntimeError(f"OpenAI API call failed: {str(e)}") from e
