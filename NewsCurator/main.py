from fetcher import fetch_news_from_perplexity
from pinecone_uploader import upsert_articles_to_pinecone

def main():
    """
    Main function to orchestrate the news fetching and uploading process.
    """
    print("--- Starting News Curation and Upsert Process ---")
    

    
    # Fetch the data from Perplexity
    news_articles = fetch_news_from_perplexity()

    # If data was fetched successfully, store it in Pinecone
    if news_articles:
        upsert_articles_to_pinecone(news_articles)
    
    print("--- Process Finished ---")

if __name__ == "__main__":
    main()
