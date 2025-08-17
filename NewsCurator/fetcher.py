import requests
import os
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Any, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from serper_searcher import search_article_url
from schemas import NewsArticle, NewsArticleWithUrl, NewsArticleList

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

# --- Core Function ---

def fetch_news_from_perplexity() -> List[NewsArticleWithUrl]:
    """
    Fetches a structured list of news articles from the Perplexity API for the previous 12 months
    and enriches them with URLs from Serper. Uploads to Pinecone after each month.
    """
    # Import here to avoid circular import
    from pinecone_uploader import upsert_articles_to_pinecone
    
    print("Fetching news from Perplexity API for previous 12 months...")
    
    # Current date reference
    current_date = datetime(2025, 8, 17)
    total_articles_processed = 0
    
    # Loop through previous 12 months (1 year)
    for month_offset in range(1, 13):
        # Calculate the target month
        target_month = current_date - relativedelta(months=month_offset)
        
        # Calculate start and end dates for the month
        start_date = target_month.replace(day=1)
        # Get last day of the month
        if target_month.month == 12:
            next_month = target_month.replace(year=target_month.year + 1, month=1, day=1)
        else:
            next_month = target_month.replace(month=target_month.month + 1, day=1)
        end_date = next_month - timedelta(days=1)
        
        # Format dates for API (MM/DD/YYYY format required by Perplexity)
        start_date_str = f"{start_date.month}/{start_date.day}/{start_date.year}"
        end_date_str = f"{end_date.month}/{end_date.day}/{end_date.year}"
        
        print(f"Fetching 10 articles from {target_month.strftime('%B %Y')} ({start_date_str} to {end_date_str})...")
        
        prompt_content = (
            f"Find exactly 10 individual Indian crime news articles that could be adapted into a film or web series. "
            "Provide the title, a detailed 5 line summary, the publication date, and the category for each article. "
            "Focus on accuracy and real news stories from major Indian news sources."
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
                    "content": f"You are a factual data retrieval assistant specializing in Indian crime news from {target_month.strftime('%B %Y')}. Your primary goal is accuracy. Provide exactly 10 real news stories with exact titles and publication details from that specific month."
                },
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": NewsArticleList.model_json_schema()}
            },
            "search_after_date_filter": start_date_str,
            "search_before_date_filter": end_date_str
        }

        try:
            response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract valid JSON using the new function
            json_data = extract_valid_json(data)
            
            news_list = NewsArticleList.model_validate(json_data)
            print(f"Successfully fetched {len(news_list.articles)} articles from {target_month.strftime('%B %Y')}.")
            
            # Search for URLs using Serper for this month's articles
            month_enriched_articles = []
            for article in news_list.articles:
                print(f"Searching URL for: {article.title[:50]}...")
                url = search_article_url(article.title)
                
                enriched_article = NewsArticleWithUrl(
                    title=article.title,
                    story_summary=article.story_summary,
                    source_url=url or "URL not found",
                    publication_date=article.publication_date,
                    category=article.category
                )
                month_enriched_articles.append(enriched_article)
            
            # Upload this month's articles to Pinecone immediately
            if month_enriched_articles:
                print(f"Uploading {len(month_enriched_articles)} articles from {target_month.strftime('%B %Y')} to Pinecone...")
                upsert_articles_to_pinecone(month_enriched_articles)
                total_articles_processed += len(month_enriched_articles)
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {target_month.strftime('%B %Y')}: {http_err}")
            continue
        except Exception as err:
            print(f"An error occurred during fetch for {target_month.strftime('%B %Y')}: {err}")
            continue
    
    print(f"Successfully processed and uploaded {total_articles_processed} total articles from 12 months.")
    return []  # Return empty list since we're uploading as we go