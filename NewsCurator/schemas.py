from typing import List
from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    title: str = Field(description="The full headline of the news article.")
    story_summary: str = Field(description="A concise, one or two-sentence summary of the news story.")
    publication_date: str = Field(description="The date the article was published, in YYYY-MM-DD format.")
    category: str = Field(description="The primary category of the news, e.g., 'Crime'.")

class NewsArticleWithUrl(BaseModel):
    title: str = Field(description="The full headline of the news article.")
    story_summary: str = Field(description="A concise, one or two-sentence summary of the news story.")
    source_url: str = Field(description="The direct URL to the original article.")
    publication_date: str = Field(description="The date the article was published, in YYYY-MM-DD format.")
    category: str = Field(description="The primary category of the news, e.g., 'Crime'.")

class NewsArticleList(BaseModel):
    articles: List[NewsArticle]
