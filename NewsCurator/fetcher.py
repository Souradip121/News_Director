import requests
import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Debug: Check if API key is loaded
if not PERPLEXITY_API_KEY:
    print("❌ ERROR: PERPLEXITY_API_KEY not found in environment variables")
    exit(1)

print(f"✅ API Key loaded: {PERPLEXITY_API_KEY[:10]}...{PERPLEXITY_API_KEY[-4:]}")

# --- Data Structures (Schema) ---

class NewsArticle(BaseModel):
    title: str = Field(description="The full headline of the news article.")
    story_summary: str = Field(description="A concise, one or two-sentence summary of the news story.")
    source_url: str = Field(description="The direct URL to the original article.")
    publication_date: str = Field(description="The date the article was published, in YYYY-MM-DD format.")
    source_name: str = Field(description="The name of the news publication, e.g., 'The Times of India'.")
    category: str = Field(description="The primary category of the news, e.g., 'Crime'.")

class NewsArticleList(BaseModel):
    articles: List[NewsArticle]

# --- Core Function ---

def fetch_news_from_perplexity() -> List[NewsArticle]:
    """
    Fetches a structured list of news articles from the Perplexity API.
    """
    print("Fetching news from Perplexity API...")
    headers = {
        "Authorization": f'Bearer {PERPLEXITY_API_KEY}',
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that extracts information about news stories and provides it in a structured JSON format."
            },
            {
                "role": "user",
                "content": "Provide a list of 25 distinct Indian crime news stories from the last month that could be adapted into a film or web series."
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": NewsArticleList.model_json_schema()}
        }
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        json_content = data["choices"][0]["message"]["content"]
        
        news_list = NewsArticleList.model_validate_json(json_content)
        print(f"Successfully fetched and validated {len(news_list.articles)} articles.")
        return news_list.articles
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response body: {response.text}")
        return []
    except Exception as err:
        print(f"An error occurred during fetch: {err}")
        return []
