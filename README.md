# News Director - Semantic Search System

A sophisticated news analysis and semantic search system that leverages AI technologies to process, analyze, and search through news content using vector embeddings and natural language processing.

## 🚀 Project Overview

News Director is an intelligent news processing system that combines semantic search capabilities with AI-powered content analysis. The system ingests news articles, processes them through semantic understanding, and provides advanced search functionality using vector embeddings stored in Pinecone vector database.

## 🛠️ Technology Stack

### Core Technologies

- **Vector Database**: Pinecone with Llama-text-embed-v2 embeddings
- **AI/ML Platform**: Azure OpenAI Service (GPT-4o model)
- **Semantic Search**: Vector similarity search using integrated embeddings
- **Web Interface**: Streamlit for interactive user experience
- **Content Processing**: Perplexity API for enhanced understanding

### Services & APIs

- **Pinecone Vector Database**: Hosts semantic embeddings with integrated Llama-text-embed-v2 model
- **Azure OpenAI**: Provides language model capabilities (GPT-4o) for content generation and analysis
- **Perplexity API**: Enhanced content understanding and processing
- **Serper API**: URL searching based on news headlines
- **Streamlit**: Modern web framework for the user interface

## 🏗️ Architecture & Flow

### System Architecture Overview

The News Director system consists of two main components working in tandem:

#### 1. News Curation Pipeline
![News Curation Architecture](https://github.com/user-attachments/assets/1234567890abcdef1234567890abcdef12345678)

The first component handles the data ingestion and processing:
- **News Curator**: Collects news stories from various sources
- **Perplexity Integration**: Uses Perplexity API for enhanced content understanding  
- **Serper API**: Searches URLs based on news headlines for comprehensive coverage
- **Pinecone Storage**: Stores processed content as vector embeddings using Llama-text-embed-v2

#### 2. Semantic Search & AI Analysis
![Semantic Search Architecture](https://github.com/user-attachments/assets/abcdef1234567890abcdef1234567890abcdef12)

The second component provides the user-facing search and analysis:
- **Pinecone Vector DB**: Retrieves relevant content using semantic similarity
- **Azure OpenAI Integration**: Powers intelligent analysis and content generation
- **Streamlit Interface**: Provides an intuitive web interface for user interactions
- **User Community**: Enables collaborative exploration of news-to-movie adaptations

```
News Content → Preprocessing → Embedding Generation → Vector Storage (Pinecone)
                                                            ↓
User Query → Query Processing → Semantic Search → Relevant Results ← AI Analysis (Azure OpenAI)
```

### Data Flow

1. **Content Ingestion**: News articles are collected and preprocessed
2. **Embedding Generation**: Text content is converted to vector embeddings using Azure OpenAI
3. **Vector Storage**: Embeddings are stored in Pinecone vector database for efficient similarity search
4. **Query Processing**: User queries are processed and converted to embeddings
5. **Semantic Search**: Similar content is retrieved using vector similarity matching
6. **AI Enhancement**: Results are enhanced using GPT-4o for better context and analysis

## 🔧 Setup & Installation

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service account
- Pinecone account and API key
- Perplexity API access
- Serper API key
- Git

### Environment Configuration

1. Clone the repository:

```bash
git clone <repository-url>
cd News_Director
```

2. Set up the News Curation Pipeline:

```bash
cd NewsCurator
python -m venv myenv
# Windows
myenv\Scripts\activate
# Linux/Mac
source myenv/bin/activate

pip install -r requirements.txt
```

3. Set up the Semantic Searcher:

```bash
cd ../SemanticSearcher
pip install -r requirements.txt
```

4. Configure environment variables by creating separate `.env` files in each directory:

> **Important**: Each component requires its own `.env` file with different API keys. Use the provided example files as templates.

#### NewsCurator Environment Setup
Copy the example file and configure your API keys:

```bash
cd NewsCurator
cp .env.example .env
# Edit .env file with your actual API keys
```

The `NewsCurator/.env` should contain:
- **PERPLEXITY_API_KEY**: For enhanced content processing
- **PINECONE_API_KEY**: For vector database storage
- **PINECONE_HOST**: Your Pinecone index URL
- **SERPER_API_KEY**: For URL search functionality

#### SemanticSearcher Environment Setup
Copy the example file and configure your API keys:

```bash
cd SemanticSearcher  
cp .env.example .env
# Edit .env file with your actual API keys
```

The `SemanticSearcher/.env` should contain:
- **PINECONE_API_KEY**: Same as NewsCurator (shared database)
- **PINECONE_HOST**: Same as NewsCurator (shared database)  
- **AZURE_OPENAI_API_KEY**: For AI-powered analysis
- **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI endpoint
- **AZURE_OPENAI_DEPLOYMENT**: Model deployment name (typically "gpt-4o")
- **AZURE_OPENAI_API_VERSION**: API version (recommended: "2024-12-01-preview")

> **Security Note**: Never commit actual `.env` files to version control. The `.env.example` files are provided as templates only.

### Required Services Setup

#### Pinecone Setup

1. Create a Pinecone account at [pinecone.io](https://pinecone.io)
2. Create a new index with integrated Llama-text-embed-v2 model
3. Configure the namespace as "news-articles-namespace"
4. Note your API key and host URL

#### Azure OpenAI Setup

1. Create an Azure OpenAI resource in Azure Portal
2. Deploy the GPT-4o model
3. Optionally deploy text-embedding models if using manual embeddings
4. Obtain your API key and endpoint URL

#### Additional API Setup

1. **Perplexity API**: Sign up at [perplexity.ai](https://perplexity.ai) for content processing
2. **Serper API**: Get your API key from [serper.dev](https://serper.dev) for URL searching

## 🚀 How to Run

### 1. News Curation Pipeline

First, collect and process news content:

```bash
cd NewsCurator
# Activate virtual environment
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac

# Run the news collection and upload process
python main.py
```

### 2. Semantic Search Interface

Launch the interactive web interface:

```bash
cd SemanticSearcher

# Start the Streamlit application
streamlit run app.py
```

### 3. Testing Connections

Verify your setup:

```bash
cd SemanticSearcher
python test_connection.py
```

### Development Mode

For development and testing:

```bash
# Test individual components
python searcher.py  # Direct searcher testing
python -c "from searcher import NewsMovieSearcher; s = NewsMovieSearcher()"  # Quick test
```

## 📁 Project Structure

```
News_Director/
├── NewsCurator/               # News collection and processing pipeline
│   ├── fetcher.py            # News content fetching functionality
│   ├── main.py               # Main execution script
│   ├── pinecone_uploader.py  # Vector database upload logic
│   ├── serper_searcher.py    # Serper API integration
│   ├── schemas.py            # Data schemas and validation
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment configuration template
│   ├── .env                  # Your actual environment variables (not in git)
│   └── myenv/                # Virtual environment
├── SemanticSearcher/          # Semantic search and AI analysis
│   ├── app.py                # Streamlit web application
│   ├── searcher.py           # Core search functionality
│   ├── config.py             # Configuration management
│   ├── requirements.txt      # Python dependencies
│   ├── test_connection.py    # Connection testing utilities
│   ├── .env.example          # Environment configuration template
│   └── .env                  # Your actual environment variables (not in git)
├── README.md                 # Project documentation
└── LICENSE                   # License information
```

## 🔍 Features

### News Curation Pipeline
- **Automated News Collection**: Fetches news from multiple sources
- **Enhanced Content Processing**: Uses Perplexity API for deeper understanding
- **URL Discovery**: Serper integration for finding relevant source URLs
- **Vector Embedding**: Automatic conversion to embeddings using Llama-text-embed-v2

### Semantic Search & Analysis
- **Movie Plot Generation**: AI-powered movie ideas from news stories
- **Category-Based Search**: Filter by news categories for targeted inspiration
- **Date-Range Filtering**: Search news from specific time periods
- **Custom Queries**: Natural language search for specific themes
- **Interactive Web Interface**: User-friendly Streamlit application

### Technical Features
- **Semantic Search**: Advanced vector-based search using contextual understanding
- **AI-Powered Analysis**: GPT-4o integration for creative content generation
- **Scalable Vector Storage**: Pinecone database with integrated embeddings
- **Real-time Processing**: Fast query processing and result retrieval
- **Dark Mode Support**: Responsive UI with theme compatibility

## 🔐 Security & Configuration

### Environment Variables Security
- **Never commit `.env` files**: Actual API keys should never be in version control
- **Use `.env.example` templates**: Copy and rename to `.env` for each component
- **Component-specific configurations**: Each directory has its own `.env` file with required APIs only
- **API key rotation**: Regularly rotate API keys for enhanced security

### Service Security Features
- **Azure OpenAI**: Enterprise-grade security with role-based access controls
- **Pinecone**: Secure vector storage with API key authentication and VPC support
- **Perplexity API**: Secure content processing with rate limiting
- **Serper API**: Protected search functionality with API quotas

### Best Practices
1. Keep API keys confidential and rotate them regularly
2. Use different API keys for development and production environments  
3. Monitor API usage and set up billing alerts
4. Implement proper error handling for API failures
5. Use environment-specific `.env` files for different deployment stages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## 🆘 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all environment variables are correctly set
2. **Connection Issues**: Verify network connectivity to Azure and Pinecone services
3. **Model Deployment**: Confirm GPT-4o model is properly deployed in Azure OpenAI

### Support

For support and questions, please [create an issue](link-to-issues) or contact the development team.

---

**Note**: This project requires active Azure OpenAI and Pinecone subscriptions. Ensure you have proper access and billing configured for these services.
