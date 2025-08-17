import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = "https://google.serper.dev/search"

def search_article_url(title: str, source_name: str) -> Optional[str]:
    """
    Search for the actual URL of a news article using Serper API.
    
    Args:
        title (str): The headline of the news article
        source_name (str): The name of the news publication
    
    Returns:
        Optional[str]: The URL of the article if found, None otherwise
    """
    if not SERPER_API_KEY:
        print("❌ ERROR: SERPER_API_KEY not found in environment variables")
        return None
    
    # Construct search query
    search_query = f'"{title}" site:{get_site_domain(source_name)}'
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": search_query,
        "num": 3  # Get top 3 results
    }
    
    try:
        response = requests.post(SERPER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract the first organic result URL
        organic_results = data.get("organic", [])
        if organic_results:
            return organic_results[0].get("link")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching for article URL: {e}")
        return None

def get_site_domain(source_name: str) -> str:
    """
    Map source names to their website domains.
    
    Args:
        source_name (str): The name of the news publication
    
    Returns:
        str: The domain to search on
    """
    domain_mapping = {
        "The Times of India": "timesofindia.indiatimes.com",
        "Hindustan Times": "hindustantimes.com",
        "The Hindu": "thehindu.com",
        "Indian Express": "indianexpress.com",
        "NDTV": "ndtv.com",
        "CNN-News18": "news18.com",
        "Republic World": "republicworld.com",
        "India Today": "indiatoday.in",
        "The Wire": "thewire.in",
        "Scroll.in": "scroll.in"
    }
    
    # Return specific domain if found, otherwise use a generic search
    return domain_mapping.get(source_name, "")
