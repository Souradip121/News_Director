import os
import uuid
from typing import List
from pinecone import Pinecone
from fetcher import NewsArticle # Import the schema from fetcher.py
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = os.getenv("PINECONE_HOST")

# --- Core Function ---

def upsert_articles_to_pinecone(articles: List[NewsArticle]):
    """
    Connects to Pinecone and upserts the fetched articles.
    """
    if not articles:
        print("No articles to upsert. Exiting.")
        return

    print(f"Connecting to Pinecone index at host: {PINECONE_HOST}...")
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(host=PINECONE_HOST)

        records_to_upsert = []
        for article in articles:
            # IMPORTANT: The key for the text to be embedded ('story_summary' here)
            # must match the 'field_map' you configured in your Pinecone index settings.
            record = {
                "_id": str(uuid.uuid4()),  # Generate a unique ID for each record
                "text": article.story_summary,
            }
            
            # Add metadata fields, filtering out None values
            metadata = {
                "title": article.title,
                "publication_date": article.publication_date,
                "source_name": article.source_name,
                "category": article.category
            }
            
            # Only add source_url if it's not None
            if article.source_url is not None:
                metadata["source_url"] = article.source_url
            
            # Add all non-None metadata to the record
            record.update(metadata)
            records_to_upsert.append(record)
        
        print(f"Upserting {len(records_to_upsert)} records to Pinecone...")
        # Using a namespace is good practice for organizing data
        index.upsert_records(
            "news-articles-namespace",
            records_to_upsert
        )
        print("Upsert complete!")

    except Exception as err:
        print(f"An error occurred during Pinecone upsert: {err}")
