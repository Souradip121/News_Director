import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_API_URL = "https://google.serper.dev/search"

def search_article_url(title: str) -> Optional[str]:
    """
    Search for the actual URL of a news article using Serper API.
    
    Args:
        title (str): The headline of the news article
    
    Returns:
        Optional[str]: The URL of the article if found, None otherwise
    """
    if not SERPER_API_KEY:
        print("❌ ERROR: SERPER_API_KEY not found in environment variables")
        return None
    
    # Try multiple search strategies
    search_queries = [
        f'"{title}"',  # Exact title match
        f'"{title[:50]}" India crime news',  # Truncated title with context
        f'{title} India news',  # Title with India context
    ]
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    for query in search_queries:
        payload = {
            "q": query,
            "num": 10,  # Get more results
            "gl": "in",  # Focus on India
            "hl": "en"   # English language
        }
        
        try:
            response = requests.post(SERPER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Check organic results
            organic_results = data.get("organic", [])
            
            # Filter for news websites and relevant URLs
            for result in organic_results:
                url = result.get("link", "")
                title_match = result.get("title", "").lower()
                
                # Check if it's from a news website
                if any(domain in url.lower() for domain in [
                    "timesofindia", "hindustantimes", "thehindu", "indianexpress", 
                    "ndtv", "news18", "indiatoday", "scroll", "thewire", "deccanherald",
                    "tribuneindia", "business-standard", "livemint", "outlookindia"
                ]):
                    return url
                
                # If no news site found, return first result that looks relevant
                if "crime" in title_match or "police" in title_match or "arrest" in title_match:
                    return url
            
            # If we found any results, return the first one
            if organic_results:
                return organic_results[0].get("link")
                
        except requests.exceptions.RequestException as e:
            print(f"Error searching with query '{query}': {e}")
            continue
    
    return None
