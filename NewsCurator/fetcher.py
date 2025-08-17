import requests
import os
import json
from typing import List, Any, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from serper_searcher import search_article_url

load_dotenv()

def extract_valid_json(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and returns only the valid JSON part from a response object.
    
    This function assumes that the response has a structure where the valid JSON
    is included in the 'content' field of the first choice's message, after the 
    closing "</think>" marker. Any markdown code fences (e.g. ```json) are stripped.

    Parameters:
        response (dict): The full API response object.

    Returns:
        dict: The parsed JSON object extracted from the content.
    
    Raises:
        ValueError: If no valid JSON can be parsed from the content.
    """
    # Navigate to the 'content' field; adjust if your structure differs.
    content = (
        response
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    
    # Find the index of the closing </think> tag.
    marker = "</think>"
    idx = content.rfind(marker)
    
    if idx == -1:
        # If marker not found, try parsing the entire content.
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError("No </think> marker found and content is not valid JSON") from e
    
    # Extract the substring after the marker.
    json_str = content[idx + len(marker):].strip()
    
    # Remove markdown code fence markers if present.
    if json_str.startswith("```json"):
        json_str = json_str[len("```json"):].strip()
    if json_str.startswith("```"):
        json_str = json_str[3:].strip()
    if json_str.endswith("```"):
        json_str = json_str[:-3].strip()
    
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse valid JSON from response content") from e

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
    publication_date: str = Field(description="The date the article was published, in YYYY-MM-DD format.")
    source_name: str = Field(description="The name of the news publication, e.g., 'The Times of India'.")
    category: str = Field(description="The primary category of the news, e.g., 'Crime'.")

class NewsArticleWithUrl(BaseModel):
    title: str = Field(description="The full headline of the news article.")
    story_summary: str = Field(description="A concise, one or two-sentence summary of the news story.")
    source_url: str = Field(description="The direct URL to the original article.")
    publication_date: str = Field(description="The date the article was published, in YYYY-MM-DD format.")
    source_name: str = Field(description="The name of the news publication, e.g., 'The Times of India'.")
    category: str = Field(description="The primary category of the news, e.g., 'Crime'.")

class NewsArticleList(BaseModel):
    articles: List[NewsArticle]

# --- Core Function ---

def fetch_news_from_perplexity() -> List[NewsArticleWithUrl]:
    """
    Fetches a structured list of news articles from the Perplexity API and enriches them with URLs from Serper.
    """
    print("Fetching news from Perplexity API...")
    
    prompt_content = (
        "Find 10 individual Indian crime news articles from the last month that could be adapted into a film or web series. "
        "Provide the title, a 5 line short summary, the publication date, and the source name for each article. "
        "Focus on accuracy and real news stories."
    )

    headers = {
        "Authorization": f'Bearer {PERPLEXITY_API_KEY}',
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a factual data retrieval assistant. Your primary goal is accuracy. Provide real news stories with exact titles and publication details."
            },
            {
                "role": "user",
                "content": prompt_content
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
        
        # Extract valid JSON using the new function
        json_data = extract_valid_json(data)
        
        news_list = NewsArticleList.model_validate(json_data)
        print(f"Successfully fetched {len(news_list.articles)} articles from Perplexity.")
        
        # Now search for URLs using Serper
        enriched_articles = []
        for article in news_list.articles:
            print(f"Searching URL for: {article.title[:50]}...")
            url = search_article_url(article.title, article.source_name)
            
            enriched_article = NewsArticleWithUrl(
                title=article.title,
                story_summary=article.story_summary,
                source_url=url or "URL not found",
                publication_date=article.publication_date,
                source_name=article.source_name,
                category=article.category
            )
            enriched_articles.append(enriched_article)
        
        print(f"Successfully enriched {len(enriched_articles)} articles with URLs.")
        return enriched_articles
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response body: {response.text}")
        return []
    except Exception as err:
        print(f"An error occurred during fetch: {err}")
        return []