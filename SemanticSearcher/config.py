"""
Configuration settings for the News to Movie Semantic Searcher
"""

import os
from typing import List, Dict, Any

class Config:
    """Configuration class for the semantic searcher application"""
    
    # Database settings
    NAMESPACE = "news-articles-namespace"
    TOTAL_ARTICLES = 120  # Fallback number if database query fails
    
    # Search settings
    DEFAULT_SEARCH_RESULTS = 8  # Number of articles to retrieve for context
    MAX_DISPLAY_ARTICLES = 5   # Maximum articles to show in UI
    
    # Movie genres available for search - will be populated dynamically from database
    POPULAR_GENRES = []
    
    # Streamlit UI settings
    PAGE_CONFIG = {
        "page_title": "News Movie Semantic Searcher",
        "page_icon": "🎬",
        "layout": "wide"
    }
    
    # Azure OpenAI settings
    LLM_TEMPERATURE = 0.7
    AZURE_OPENAI_MODEL = "gpt-4o"
    AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
    
    # Database fallback categories - will be populated dynamically
    FALLBACK_CATEGORIES = []
    
    # Sample queries for user guidance - generic examples
    SAMPLE_QUERIES = {
        "genre_search": [
            "thriller movies from available news categories",
            "drama films from recent news stories",
            "action movies from current events",
            "horror plots from mysterious news"
        ],
        "date_genre_search": [
            "movies from specific date ranges",
            "genre films from monthly news",
            "plot ideas from weekly stories",
            "adaptations from dated articles"
        ],
        "plot_suggestions": [
            "creative plot suggestions",
            "movie adaptation ideas",
            "film concepts from news",
            "screenplay inspiration"
        ]
    }
    
    # Custom prompts for different search types
    PROMPTS = {
        "genre_search": """
        You are a creative film consultant analyzing news stories for {genre} movie potential.
        
        Context: {context}
        Query: {question}
        
        Focus on:
        - Stories with dramatic tension suitable for {genre} films
        - Character archetypes that fit the genre
        - Plot structures that would work in {genre} movies
        - Specific adaptation suggestions
        
        Be creative but respectful when adapting real events.
        """,
        
        "plot_generation": """
        You are a Hollywood screenwriter creating {genre} movie plots from news inspiration.
        
        Context: {context}
        Query: {question}
        
        For each plot suggestion, include:
        1. Compelling logline (1-2 sentences)
        2. Main characters and their motivations
        3. Three-act structure outline
        4. How the real news events inspire the story
        5. What makes it work as a {genre} film
        
        Generate 2-3 detailed plot ideas.
        """,
        
        "date_search": """
        You are analyzing news from {date} for {genre} movie adaptation potential.
        
        Context: {context}
        Query: {question}
        
        Focus specifically on:
        - Stories published around {date}
        - How these specific events could inspire {genre} narratives
        - Time-sensitive elements that add urgency to plots
        - Real-world context that enhances the story
        
        Provide detailed adaptation suggestions.
        """
    }
    
    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """Get API keys from environment variables"""
        return {
            "pinecone_api_key": os.getenv("PINECONE_API_KEY"),
            "pinecone_host": os.getenv("PINECONE_HOST"),
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        api_keys = cls.get_api_keys()
        missing_keys = [k for k, v in api_keys.items() if not v]
        
        if missing_keys:
            print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
            return False
        
        return True
    
    @classmethod
    def get_genre_suggestions(cls) -> List[str]:
        """Get list of suggested genres for user interface from database"""
        return cls.get_database_categories()
    
    @classmethod
    def get_sample_queries_for_tab(cls, tab_name: str) -> List[str]:
        """Get sample queries for a specific UI tab"""
        return cls.SAMPLE_QUERIES.get(tab_name, [])
    
    @classmethod
    def get_database_categories(cls) -> List[str]:
        """Get categories from the database dynamically"""
        try:
            from searcher import NewsMovieSearcher
            searcher = NewsMovieSearcher()
            overview = searcher.get_database_overview()
            return overview.get('categories', cls.FALLBACK_CATEGORIES)
        except Exception as e:
            print(f"Warning: Could not fetch categories from database: {e}")
            return cls.FALLBACK_CATEGORIES

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Configuration for development environment"""
    DEBUG = True
    LLM_TEMPERATURE = 0.8  # More creative for development
    DEFAULT_SEARCH_RESULTS = 5  # Fewer results for faster testing

class ProductionConfig(Config):
    """Configuration for production environment"""
    DEBUG = False
    LLM_TEMPERATURE = 0.7  # Balanced creativity and consistency
    DEFAULT_SEARCH_RESULTS = 8  # More comprehensive results

# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development").lower()
if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
