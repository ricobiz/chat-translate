import os
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def call_openrouter(text: str, target_lang: str) -> dict:
    """
    Call OpenRouter API to translate text.
    
    Args:
        text: The text to translate
        target_lang: The target language for translation
    
    Returns:
        dict with keys: detected_lang, normalized_text, translated_text
    
    Raises:
        Exception on API failure
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise Exception("OPENROUTER_API_KEY environment variable not set")
    
    # Mask API key in logs
    masked_key = api_key[:8] + "..." if len(api_key) > 8 else "..."
    logger.info(f"Calling OpenRouter API with key: {masked_key}")
    logger.info(f"Text length: {len(text)} chars, target_lang: {target_lang}")
    
    system_prompt = f"You are a translation assistant. Detect the source language (even if written in Latin script). Normalize the text to its natural form. Translate to {target_lang}. Return JSON with: detected_lang, normalized_text, translated_text."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        result = response.json()
        
        # Extract content from response
        if "choices" not in result or len(result["choices"]) == 0:
            raise Exception("Invalid response format: no choices in response")
        
        content = result["choices"][0]["message"]["content"]
        logger.info(f"Received response, content length: {len(content)} chars")
        
        # Parse JSON from the response content
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON response: {content}")
        
        # Validate required fields
        required_fields = ["detected_lang", "normalized_text", "translated_text"]
        for field in required_fields:
            if field not in parsed:
                raise Exception(f"Missing required field in response: {field}")
        
        return parsed
        
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise Exception(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
