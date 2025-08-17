# News Director - Semantic Search System

A sophisticated news analysis and semantic search system that leverages AI technologies to process, analyze, and search through news content using vector embeddings and natural language processing.

## 🚀 Project Overview

News Director is an intelligent news processing system that combines semantic search capabilities with AI-powered content analysis. The system ingests news articles, processes them through semantic understanding, and provides advanced search functionality using vector embeddings stored in Pinecone vector database.

## 🛠️ Technology Stack

### Core Technologies

- **Vector Database**: Pinecone - For storing and querying semantic embeddings
- **AI/ML Platform**: Azure OpenAI Service (GPT-4o model)
- **Semantic Search**: Vector similarity search using embeddings
- **Language Processing**: Natural Language Processing for content analysis

### Services & APIs

- **Pinecone Vector Database**: Hosts semantic embeddings for news content
- **Azure OpenAI**: Provides language model capabilities for content understanding and generation
- **GPT-4o Model**: Latest OpenAI model for advanced text processing

## 🏗️ Architecture & Flow

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

- Node.js (v16 or higher)
- Azure OpenAI Service account
- Pinecone account and API key
- Git

### Environment Configuration

1. Clone the repository:

```bash
git clone <repository-url>
cd News_Director
```

2. Navigate to the SemanticSearcher directory:

```bash
cd SemanticSearcher
```

3. Install dependencies:

```bash
npm install
```

4. Configure environment variables by updating `.env` file:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST=your_pinecone_host_url

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Required Services Setup

#### Pinecone Setup

1. Create a Pinecone account at [pinecone.io](https://pinecone.io)
2. Create a new index with appropriate dimensions
3. Note your API key and host URL

#### Azure OpenAI Setup

1. Create an Azure OpenAI resource in Azure Portal
2. Deploy the GPT-4o model
3. Obtain your API key and endpoint URL

## 🚀 How to Run

### SemanticSearcher Component

1. Navigate to the SemanticSearcher directory:

```bash
cd SemanticSearcher
```

2. Start the semantic search service:

```bash
npm start
```

### Development Mode

```bash
npm run dev
```

### Running Tests

```bash
npm test
```

## 📁 Project Structure

```
News_Director/
├── SemanticSearcher/           # Core semantic search functionality
│   ├── .env                   # Environment configuration
│   ├── package.json           # Dependencies and scripts
│   ├── src/                   # Source code
│   └── ...
├── README.md                  # This file
└── ...
```

## 🔍 Features

- **Semantic Search**: Advanced vector-based search using contextual understanding
- **AI-Powered Analysis**: GPT-4o integration for intelligent content processing
- **Scalable Vector Storage**: Pinecone database for efficient similarity matching
- **News Content Processing**: Specialized handling of news articles and content
- **Real-time Search**: Fast query processing and result retrieval

## 🔐 Security & Configuration

- API keys are stored securely in environment variables
- Azure OpenAI provides enterprise-grade security
- Pinecone offers secure vector storage with access controls

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
