import os

class Config:
    # API keys and endpoints
    GNEWS_API_KEY: str = os.getenv('GNEWS_API_KEY', '')
    GNEWS_API_URL: str = 'https://gnews.io/api/v4/search'
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    OPENROUTER_API_URL: str = 'https://openrouter.ai/api/v1/chat/completions'
    CACHE_TIMEOUT: int = 900  # 15 minutes
    LOG_FILE: str = 'app.log'
    MAX_RETRIES: int = 2
    BACKOFF_FACTOR: float = 0.5
    RETRY_STATUS_CODES: list = [500, 502, 503, 504]
    NEWS_CACHE_PREFIX: str = 'news_page_'
    SUMMARIZE_BATCH_SIZE: int = 3  # Number of articles to summarize in parallel
    MAX_SUMMARY_TIME: int = 10  # Maximum time to wait for summarization in seconds
