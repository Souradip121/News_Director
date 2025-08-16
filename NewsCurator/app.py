import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

response = requests.post(
    'https://api.perplexity.ai/chat/completions',
    headers={
        'Authorization': f'Bearer {os.getenv("PERPLEXITY_API_KEY")}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'sonar',
        'messages': [
            {
                'role': 'user',
                'content': '10 news stories that can made into a film or web series.'
            }
        ],
        'search_domain_filter': ['timesofindia.indiatimes.com'],
        'search_recency_filter': 'month'
    }
)

print(response.json())