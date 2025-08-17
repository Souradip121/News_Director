from fetcher import fetch_news_from_perplexity

def main():
    """
    Main function to orchestrate the news fetching and uploading process.
    """
    print("--- Starting News Curation and Upsert Process ---")
    
    # Fetch the data from Perplexity and upload to Pinecone month by month
    fetch_news_from_perplexity()
    
    print("--- Process Finished ---")

if __name__ == "__main__":
    main()
    
    
    print("--- Process Finished ---")

