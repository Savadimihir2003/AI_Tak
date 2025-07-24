import requests
import os
import logging
import time
import concurrent.futures
from typing import List, Dict, Any, Optional
from config import Config
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import aiohttp
import asyncio

# Configure logging
logger = logging.getLogger("news")
handler = logging.FileHandler(Config.LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure requests session with retries and connection pooling
session = requests.Session()
retries = Retry(
    total=Config.MAX_RETRIES,
    backoff_factor=Config.BACKOFF_FACTOR,
    status_forcelist=Config.RETRY_STATUS_CODES
)
adapter = HTTPAdapter(
    max_retries=retries,
    pool_connections=20,
    pool_maxsize=20
)
session.mount('https://', adapter)

# Initialize cache with pre-warming capability
_news_cache: Dict[str, Dict] = {}
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=Config.SUMMARIZE_BATCH_SIZE)

def get_cached_news(page: int) -> Optional[List[Dict[str, Any]]]:
    """Get news from cache if still valid."""
    cache_key = f"{Config.NEWS_CACHE_PREFIX}{page}"
    if cache_key in _news_cache:
        cached = _news_cache[cache_key]
        if time.time() - cached['timestamp'] < Config.CACHE_TIMEOUT:
            logger.debug(f"Returning cached news for page {page}")
            return cached['data']
    return None

def cache_news(page: int, data: List[Dict[str, Any]]) -> None:
    """Cache news data with timestamp."""
    cache_key = f"{Config.NEWS_CACHE_PREFIX}{page}"
    _news_cache[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }

def fetch_ai_news(page: int = 1) -> List[Dict[str, Any]]:
    """Fetch AI news from GNews API with caching and error handling."""
    # Try cache first
    cached_news = get_cached_news(page)
    if cached_news is not None:
        return cached_news

    # Validate API key
    if not Config.GNEWS_API_KEY:
        logger.error("GNews API key is not configured")
        return []

    params = {
        'q': 'artificial intelligence',
        'lang': 'en',
        'apikey': Config.GNEWS_API_KEY,
        'n': 10,  # Number of results per page
        'page': page
    }

    try:
        resp = session.get(Config.GNEWS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if not isinstance(data, dict):
            logger.error(f"Unexpected API response format: {data}")
            return []
            
        articles = data.get('articles', [])
        
        if articles:  # Only cache successful responses with articles
            cache_news(page, articles)
            logger.info(f"Fetched {len(articles)} news articles from GNews API (page {page}).")
        else:
            logger.warning(f"No articles found for page {page}")
            
        return articles
    except requests.exceptions.RequestException as e:
        logger.error(f"GNews API request error: {str(e)}")
        return []
    except ValueError as e:
        logger.error(f"GNews API response parsing error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_ai_news: {str(e)}")
        return []

async def _summarize_text_async(input_text: str, max_retries: int = 2) -> str:
    """Summarize text using OpenRouter API with retries - async implementation."""
    if not input_text:
        return ""
        
    if not Config.OPENROUTER_API_KEY:
        logger.error("OpenRouter API key is not configured")
        return get_fallback_summary(input_text)

    headers = {
        'Authorization': f'Bearer {Config.OPENROUTER_API_KEY}',
        'HTTP-Referer': 'https://aitak.news',
        'X-Title': 'AI Tak News',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'openai/gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': 'You are a professional news summarizer. Create a concise summary in 2-3 sentences.'
            },
            {
                'role': 'user',
                'content': f'Please summarize: {input_text}'
            }
        ]
    }

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('choices') and result['choices'][0].get('message'):
                            summary = result['choices'][0]['message'].get('content', '')
                            return summary if summary else get_fallback_summary(input_text)
                    logger.error(f"Failed to get summary (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to summarize text after {max_retries} attempts: {str(e)}")
                break
            continue

    return get_fallback_summary(input_text)

def get_fallback_summary(text: Optional[str]) -> str:
    """Get a fallback summary when API calls fail."""
    if not text:
        return ""
    try:
        return f"{text[:120]}..." if len(text) > 120 else text
    except (TypeError, AttributeError):
        return ""

def summarize_text(text: str, max_retries: int = 2) -> str:
    """Synchronous wrapper for async text summarization."""
    if not text:
        return ""
        
    try:
        summary = asyncio.run(_summarize_text_async(text, max_retries))
        return summary if summary else get_fallback_summary(text)
    except Exception as e:
        logger.error(f"Error in summarize_text: {str(e)}")
        return get_fallback_summary(text)

async def _summarize_batch_async(input_texts: List[str], max_retries: int = 2) -> List[str]:
    """Batch summarize texts asynchronously."""
    if not input_texts:
        return []
        
    tasks = []
    results = []
    
    async with aiohttp.ClientSession() as session:
        for text in input_texts:
            if not text:
                results.append("")
                continue
            tasks.append(_summarize_text_async(text, max_retries))
            
        try:
            if tasks:
                summaries = await asyncio.gather(*tasks, return_exceptions=True)
                for summary, text in zip(summaries, input_texts):
                    if isinstance(summary, str) and summary:
                        results.append(summary)
                    else:
                        results.append(get_fallback_summary(text))
        except Exception as e:
            logger.error(f"Error in _summarize_batch_async: {str(e)}")
            results = [get_fallback_summary(t) for t in input_texts]
    
    return results

def summarize_batch(texts: List[str], max_retries: int = 2) -> List[str]:
    """Batch summarize multiple texts efficiently."""
    if not texts:
        return []
    try:
        return asyncio.run(_summarize_batch_async(texts, max_retries))
    except Exception as e:
        logger.error(f"Error in summarize_batch: {str(e)}")
        return [get_fallback_summary(t) for t in texts]
