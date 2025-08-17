import os
import sys
from typing import List, Dict, Any
from datetime import datetime, date
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import AzureOpenAI
import re

# Load environment variables
load_dotenv()

class NewsMovieSearcher:
    """
    A class to search and analyze news articles for movie plot inspiration
    using semantic search with Pinecone and direct text search.
    """
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.openai_client = None
        self.initialize_connections()
    
    def initialize_connections(self):
        """Initialize all connections to Pinecone and Azure OpenAI"""
        try:
            # Get API keys
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            pinecone_host = os.getenv("PINECONE_HOST")
            azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
            
            if not all([pinecone_api_key, pinecone_host, azure_openai_api_key, azure_openai_endpoint]):
                raise ValueError("Missing required API keys in .env file")
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=pinecone_api_key)
            self.index = self.pc.Index(host=pinecone_host)
            
            # Initialize Azure OpenAI client
            self.openai_client = AzureOpenAI(
                api_key=azure_openai_api_key,
                api_version=azure_openai_api_version,
                azure_endpoint=azure_openai_endpoint
            )
            self.deployment_name = azure_openai_deployment
            
            print("✅ All connections initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing connections: {str(e)}")
            raise
    
    def get_database_overview(self) -> Dict[str, Any]:
        """Get an overview of what's available in the database"""
        try:
            # Use describe_index_stats to get total count
            stats = self.index.describe_index_stats()
            total_articles = stats.get('total_vector_count', 0)
            
            # Get sample articles using the metadata search method
            try:
                sample_articles = self.search_articles_by_metadata()
                articles = sample_articles
                
            except Exception as e:
                print(f"Sample query failed: {e}")
                articles = []
            
            if not articles:
                print("No sample articles retrieved, using fallback data")
                return self._get_fallback_overview()
            
            # Extract unique categories
            categories = list(set([
                article.get('category', 'Unknown') 
                for article in articles
                if article.get('category')
            ]))
            
            # If we have sample data, make sure to get categories from it
            if not categories and articles:
                categories = [article['category'] for article in articles if article.get('category')]
                categories = list(set(categories))
            
            # Extract and parse dates  
            dates = []
            for article in articles:
                date_str = article.get('publication_date')
                if date_str:
                    try:
                        # Try different date formats
                        for date_format in ['%B %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
                            try:
                                parsed_date = datetime.strptime(date_str, date_format).date()
                                dates.append(parsed_date)
                                break
                            except ValueError:
                                continue
                    except Exception:
                        continue
            
            # Calculate date range
            date_range = None
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                date_range = (min_date, max_date)
            
            return {
                'total_articles': max(total_articles, len(articles)),
                'categories': sorted(categories) if categories else self._get_fallback_categories(),
                'date_range': date_range,
                'sample_titles': [
                    article.get('title', 'N/A')[:100] + ('...' if len(article.get('title', '')) > 100 else '')
                    for article in articles[:5]
                    if article.get('title')
                ]
            }
            
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return self._get_fallback_overview()
    
    def _get_fallback_overview(self) -> Dict[str, Any]:
        """Return fallback overview data"""
        return {
            'total_articles': 0,
            'categories': [],  # Force to get categories from actual database
            'date_range': None,
            'sample_titles': ['Database connection needed to show articles...']
        }
    
    def _get_fallback_categories(self) -> List[str]:
        """Return fallback categories only from database"""
        return []  # Only use categories from actual database content
    
    def search_articles_by_metadata(self, category: str = None, date_filter: str = None) -> List[Dict]:
        """Search articles by metadata filters using dummy vector query for metadata retrieval"""
        try:
            # First get index stats to check if there are any vectors
            stats = self.index.describe_index_stats()
            
            if stats.get('total_vector_count', 0) == 0:
                print("No vectors found in index")
                return []
            
            # Since Pinecone uses 1024-dimension embeddings, use a dummy vector for metadata query
            # This is a workaround to get metadata without proper vector search
            dummy_vector = [0.0] * 1024  # Use 1024 dimensions for Pinecone's built-in embeddings
            
            # Build filter for category if specified
            filter_dict = {}
            if category:
                filter_dict['category'] = {'$eq': category}
            
            # Query with dummy vector to get metadata
            query_result = self.index.query(
                vector=dummy_vector,
                namespace="news-articles-namespace",
                top_k=50,  # Get more articles
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            articles = []
            for match in query_result.matches:
                if match.metadata:
                    articles.append({
                        'title': match.metadata.get('title', 'No title'),
                        'category': match.metadata.get('category', 'Unknown'),
                        'publication_date': match.metadata.get('publication_date', 'Unknown date'),
                        'source_url': match.metadata.get('source_url', ''),
                        'text': match.metadata.get('text', '')[:500] + '...',
                        'score': match.score
                    })
            
            print(f"Retrieved {len(articles)} articles from database")
            return articles
            
        except Exception as e:
            print(f"Error searching articles: {str(e)}")
            # Try with different vector dimensions if 1024 fails
            try:
                print("Trying with 1536 dimensions...")
                dummy_vector = [0.0] * 1536
                query_result = self.index.query(
                    vector=dummy_vector,
                    namespace="news-articles-namespace",
                    top_k=20,
                    include_metadata=True
                )
                
                articles = []
                for match in query_result.matches:
                    if match.metadata:
                        articles.append({
                            'title': match.metadata.get('title', 'No title'),
                            'category': match.metadata.get('category', 'Unknown'),
                            'publication_date': match.metadata.get('publication_date', 'Unknown date'),
                            'source_url': match.metadata.get('source_url', ''),
                            'text': match.metadata.get('text', '')[:500] + '...',
                            'score': match.score
                        })
                
                print(f"Retrieved {len(articles)} articles with 1536 dimensions")
                return articles
                
            except Exception as e2:
                print(f"Both 1024 and 1536 dimensions failed: {e2}")
                return []
    
    def _get_sample_articles(self) -> List[Dict]:
        """Return sample articles when database queries fail - using empty list to force database queries"""
        # Return empty list to force using actual database content instead of samples
        return []
    
    def generate_movie_ideas(self, articles: List[Dict], genre: str, query: str) -> str:
        """Generate movie ideas using Azure OpenAI based on articles and genre"""
        try:
            # Prepare context from articles with source information
            context_parts = []
            source_list = []
            for i, article in enumerate(articles[:5]):  # Limit to top 5 articles
                context_parts.append(f"""
                Article {i+1}:
                Title: {article['title']}
                Category: {article['category']}
                Publication Date: {article['publication_date']}
                Source URL: {article['source_url']}
                Content: {article['text'][:400]}...
                """)
                
                source_list.append(f"• **{article['title']}** ({article['category']}, {article['publication_date']})")
            
            context = "\n".join(context_parts)
            sources_text = "\n".join(source_list)
            
            # Create the prompt
            prompt = f"""You are a creative film consultant and story analyst specializing in adapting news stories into fictional {genre} movie narratives.

Context from news articles:
{context}

User Query: {query}

Guidelines:
- Focus on the themes, social issues, and human drama elements from the news stories
- Suggest fictional plot adaptations that explore the underlying issues respectfully
- Create original characters and scenarios INSPIRED BY but not directly depicting real events
- ALWAYS mention which specific articles inspired each movie idea (refer to them by title and category)
- Emphasize the social commentary and human elements suitable for cinema
- Be creative while maintaining ethical storytelling standards
- Focus on rehabilitation, justice themes, and positive social impact
- At the end, include a "Sources" section listing all referenced articles

IMPORTANT: Create fictional adaptations that explore themes from real events without sensationalizing actual crimes. Reference articles by their title and mention their category and publication date.

Provide thoughtful and creative {genre} movie concepts, ending with:

**Sources from Database:**
{sources_text}"""

            # Call Azure OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": f"You are a creative film consultant specializing in {genre} movie development. Always cite your sources from the provided articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating movie ideas: {str(e)}"
    
    def search_movies_by_genre(self, category: str) -> Dict[str, Any]:
        """Search for news stories from a specific category that could inspire movies"""
        try:
            # Search for articles in the specific category
            articles = self.search_articles_by_metadata(category=category)
            
            if not articles:
                return {
                    'success': False,
                    'error': f'No articles found in category: {category}',
                    'answer': f'No articles available in the {category} category for analysis',
                    'source_articles': [],
                    'category': category
                }
            
            # Generate movie ideas
            query = f"Find compelling movie ideas that could be inspired by {category} news stories. Consider different movie genres that would work well with these stories."
            answer = self.generate_movie_ideas(articles, category, query)
            
            return {
                'success': True,
                'answer': answer,
                'source_articles': articles[:5],  # Return top 5 for reference
                'category': category
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': f"Error searching for movie ideas from {category} category: {str(e)}",
                'source_articles': [],
                'category': category
            }
    
    def search_by_date_and_genre(self, target_date: str, category: str) -> Dict[str, Any]:
        """Search for news from a specific date and category that could inspire movies"""
        try:
            # Search for articles in the specific category
            articles = self.search_articles_by_metadata(category=category)
            
            # Filter by date if possible
            if target_date and articles:
                # Simple date filtering based on publication_date
                filtered_articles = []
                for article in articles:
                    if target_date.lower() in article.get('publication_date', '').lower():
                        filtered_articles.append(article)
                
                if filtered_articles:
                    articles = filtered_articles
            
            if not articles:
                return {
                    'success': False,
                    'error': f'No articles found for date: {target_date} in category: {category}',
                    'answer': f'No articles available from {target_date} in {category} category for analysis',
                    'source_articles': [],
                    'date': target_date,
                    'category': category
                }
            
            # Generate movie ideas
            query = f"Find compelling movie ideas from {category} news stories around {target_date}. Consider various movie genres that would work well with these stories."
            answer = self.generate_movie_ideas(articles, category, query)
            
            return {
                'success': True,
                'answer': answer,
                'source_articles': articles[:5],
                'date': target_date,
                'category': category
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': f"Error searching for movie ideas from {category} category on {target_date}: {str(e)}",
                'source_articles': [],
                'date': target_date,
                'category': category
            }
    
    def suggest_genre_plots(self, category: str) -> Dict[str, Any]:
        """Generate creative movie plot suggestions based on news stories from a specific category"""
        try:
            # Get articles from the specific category
            articles = self.search_articles_by_metadata(category=category)
            
            if not articles:
                return {
                    'success': False,
                    'error': f'No articles found in category: {category}',
                    'answer': f'No articles available in {category} category for plot generation',
                    'source_articles': [],
                    'category': category
                }
            
            # Generate plot suggestions
            query = f"""Create detailed movie plot suggestions inspired by {category} news stories.
            For each suggestion, include:
            1. A compelling logline or premise
            2. Main character descriptions
            3. Key plot points and story structure
            4. How the real news events inspire the fictional narrative
            5. What movie genres would work best for each story
            
            Be creative and provide multiple plot ideas from different angles."""
            
            answer = self.generate_movie_ideas(articles, category, query)
            
            return {
                'success': True,
                'answer': answer,
                'source_articles': articles[:5],
                'category': category
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': f"Error generating plot suggestions from {category} category: {str(e)}",
                'source_articles': [],
                'category': category
            }
    
    def custom_search(self, query: str) -> Dict[str, Any]:
        """Perform a custom search with any user-provided query"""
        try:
            # Get articles for context
            articles = self.search_articles_by_metadata()
            
            if not articles:
                return {
                    'success': False,
                    'error': 'No articles found in database',
                    'answer': 'No articles available for analysis',
                    'source_articles': [],
                    'query': query
                }
            
            # Use general genre analysis
            answer = self.generate_movie_ideas(articles, "general", query)
            
            return {
                'success': True,
                'answer': answer,
                'source_articles': articles[:5],
                'query': query
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': f"Error processing custom search: {str(e)}",
                'source_articles': [],
                'query': query
            }

def main():
    """Main function for testing the searcher"""
    print("🎬 News Movie Semantic Searcher - Command Line Interface")
    print("=" * 60)
    
    try:
        # Initialize searcher
        print("Initializing searcher...")
        searcher = NewsMovieSearcher()
        
        # Get database overview
        print("\nGetting database overview...")
        overview = searcher.get_database_overview()
        
        print(f"\n📊 Database Overview:")
        print(f"Total Articles: {overview['total_articles']}")
        print(f"Categories: {', '.join(overview['categories'])}")
        if overview['date_range']:
            print(f"Date Range: {overview['date_range'][0]} to {overview['date_range'][1]}")
        
        print("\n📰 Sample Headlines:")
        for i, title in enumerate(overview['sample_titles'][:3], 1):
            print(f"{i}. {title}")
        
        # Interactive search
        print("\n" + "=" * 60)
        print("Interactive Search (type 'quit' to exit)")
        print("Example queries:")
        print("- 'thriller movies from crime news'")
        print("- 'romantic comedy plots from recent news'")
        print("- 'horror movie ideas'")
        
        while True:
            query = input("\n🔍 Enter your search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not query:
                continue
            
            print("Searching...")
            result = searcher.custom_search(query)
            
            if result['success']:
                print(f"\n🎬 Results for: '{query}'")
                print("-" * 40)
                print(result['answer'])
                
                if result['source_articles']:
                    print(f"\n📰 Based on {len(result['source_articles'])} news articles")
            else:
                print(f"❌ Error: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
