import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any
from searcher import NewsMovieSearcher

# Page configuration
st.set_page_config(
    page_title="🎬 News to Movie Semantic Searcher",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    /* Styling for markdown content */
    .stMarkdown {
        line-height: 1.6;
    }
    
    /* Styling for headers in markdown */
    h1, h2, h3, h4 {
        color: #2E86AB;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_searcher():
    """Initialize the news searcher with caching"""
    try:
        return NewsMovieSearcher()
    except Exception as e:
        st.error(f"Failed to initialize searcher: {str(e)}")
        return None

def display_article_cards(articles: List[Dict]):
    """Display articles as cards"""
    for i, article in enumerate(articles):
        with st.container():
            source_url = article.get('source_url', '')
            source_link = f'<p><strong>Source:</strong> <a href="{source_url}" target="_blank">View Original Article</a></p>' if source_url and source_url != 'URL not found' else ''
            
            st.markdown(f"""
            <div class="article-card">
                <h4>📰 {article.get('title', 'No title')}</h4>
                <p><strong>Category:</strong> {article.get('category', 'Unknown')} | 
                   <strong>Date:</strong> {article.get('publication_date', 'Unknown')}</p>
                <p>{article.get('text', 'No summary available')}</p>
                {source_link}
            </div>
            """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎬 News to Movie Semantic Searcher</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Transform news stories into compelling movie ideas using AI-powered semantic search!</p>', unsafe_allow_html=True)
    
    # Initialize searcher
    searcher = initialize_searcher()
    if not searcher:
        st.error("Unable to initialize the searcher. Please check your configuration.")
        return
    
    # Get database overview
    with st.spinner("Loading database overview..."):
        overview = searcher.get_database_overview()
    
    # Sidebar with database info
    with st.sidebar:
        st.markdown("## 📊 Database Overview")
        if overview['total_articles'] > 0:
            category_text = ', '.join(overview['categories']) if overview['categories'] else 'Loading categories...'
            date_text = f"{overview['date_range'][0]} to {overview['date_range'][1]}" if overview['date_range'] else 'Loading dates...'
            
            st.success(f"""
            **Total Articles:** {overview['total_articles']}
            
            **News Categories in Database:**
            {category_text}
            
            **Date Range:** 
            {date_text}
            """)
        else:
            st.warning("Unable to connect to database. Please check your configuration.")
        
        st.markdown("## 🎭 Available Categories for Movie Ideas")
        st.markdown("*These are the news categories available in the database:*")
        if overview['categories']:
            # Show database categories as clickable options
            st.write(", ".join(overview['categories']))
        else:
            st.write("Loading categories...")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 Category Search", "📅 Date + Category", "💡 Plot Suggestions", "🔍 Custom Search"])
    
    with tab1:
        st.markdown("### Find Movies by Category")
        st.markdown("Search for news stories from specific categories that could inspire movies.")
        st.info("💡 **Note:** Select a news category from the database and the AI will suggest how stories from that category could inspire compelling movies.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            available_categories = overview['categories'] if overview['categories'] else ['Loading...']
            genre = st.selectbox(
                "Select a news category:",
                available_categories
            )
        with col2:
            search_btn1 = st.button("🔍 Search", key="genre_search")
        
        if search_btn1:
            with st.spinner(f"Searching for {genre} movie ideas..."):
                result = searcher.search_movies_by_genre(genre)
            
            if result['success']:
                st.markdown(f"### 🎬 {genre} Movie Ideas")
                # Display the answer with proper markdown formatting
                st.markdown(result["answer"])
                
                if result.get('source_articles'):
                    st.markdown("### 📰 Source Articles")
                    display_article_cards(result['source_articles'])
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with tab2:
        st.markdown("### Movies from Specific Date + Category")
        st.markdown("Find news from a particular date and category that could inspire movies.")
        st.info("💡 **Note:** Enter a date to filter news articles, then select a category to see adaptation ideas.")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            target_date = st.text_input(
                "Enter date (e.g., 'January 2024', 'March 15, 2024'):",
                placeholder="January 2024"
            )
        with col2:
            available_categories2 = overview['categories'] if overview['categories'] else ['Loading...']
            genre2 = st.selectbox(
                "Select category:",
                available_categories2,
                key="genre2"
            )
        with col3:
            search_btn2 = st.button("🔍 Search", key="date_genre_search")
        
        if search_btn2 and target_date:
            with st.spinner(f"Searching for {genre2} movies from {target_date}..."):
                result = searcher.search_by_date_and_genre(target_date, genre2)
            
            if result['success']:
                st.markdown(f"### 🎬 {genre2} Movies from {target_date}")
                # Display the answer with proper markdown formatting
                st.markdown(result["answer"])
                
                if result.get('source_articles'):
                    st.markdown("### 📰 Source Articles")
                    display_article_cards(result['source_articles'])
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
        elif search_btn2 and not target_date:
            st.warning("Please enter a date to search.")
    
    with tab3:
        st.markdown("### Generate Plot Suggestions")
        st.markdown("Get creative movie plot ideas based on specific news categories.")
        st.info("💡 **Note:** Select a news category to get detailed plot suggestions inspired by stories from that category.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            available_categories3 = overview['categories'] if overview['categories'] else ['Loading...']
            genre3 = st.selectbox(
                "Choose category for plot suggestions:",
                available_categories3,
                key="genre3"
            )
        with col2:
            search_btn3 = st.button("💡 Generate", key="plot_suggestions")
        
        if search_btn3:
            with st.spinner(f"Generating {genre3} plot suggestions..."):
                result = searcher.suggest_genre_plots(genre3)
            
            if result['success']:
                st.markdown(f"### 💡 {genre3} Plot Suggestions")
                # Display the answer with proper markdown formatting
                st.markdown(result["answer"])
                
                if result.get('source_articles'):
                    st.markdown("### 📰 Inspiring Articles")
                    display_article_cards(result['source_articles'])
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with tab4:
        st.markdown("### Custom Search")
        st.markdown("Enter your own query to search for movie-related insights from news.")
        
        # Example queries
        st.markdown("**Example queries:**")
        st.markdown("""
        - "thriller movies based on cybercrime news"
        - "romantic comedies from entertainment industry stories"
        - "horror plots inspired by mysterious disappearances"
        - "action movies from sports injuries and comebacks"
        """)
        
        custom_query = st.text_area(
            "Enter your search query:",
            placeholder="e.g., thriller movies based on recent crime news",
            height=100
        )
        
        search_btn4 = st.button("🔍 Search", key="custom_search")
        
        if search_btn4 and custom_query:
            with st.spinner("Processing your search..."):
                result = searcher.custom_search(custom_query)
            
            if result['success']:
                st.markdown("### 🎬 Search Results")
                # Display the answer with proper markdown formatting
                st.markdown(result["answer"])
                
                if result.get('source_articles'):
                    st.markdown("### 📰 Source Articles")
                    display_article_cards(result['source_articles'])
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
        elif search_btn4 and not custom_query:
            st.warning("Please enter a search query.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        🎬 News to Movie Semantic Searcher | Transform today's headlines into tomorrow's blockbusters!
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
