import logging
from flask import Flask, render_template, request, jsonify
from typing import Any, List, Dict
from utils.news import fetch_ai_news, summarize_text
import random
from config import Config

logging.basicConfig(level=logging.INFO, filename=Config.LOG_FILE, format='%(asctime)s %(levelname)s %(message)s')
app = Flask(__name__)

def process_news_items(news_items: List[Dict], page: int = None) -> List[Dict]:
    """Helper function to process news items and generate summaries."""
    summarized_news = []
    for idx, item in enumerate(news_items[:8]):
        try:
            text = item.get('description') or item.get('content', '')
            summary = summarize_text(text) if text else ''
        except Exception as e:
            logging.error(f"Summarization failed for item {idx} on page {page or 'unknown'}: {e}")
            summary = (item.get('description') or item.get('content', '') or '')[:120] + '...'
        
        summarized_news.append({
            'title': item.get('title', ''),
            'summary': summary,
            'date': item.get('publishedAt', '')[:10],
            'tags': '',
            'class': item.get('source', {}).get('name', '') if isinstance(item.get('source'), dict) else '',
            'image': item.get('image', ''),
            'link': item.get('url', '')
        })
    return summarized_news

@app.route('/')
def home() -> Any:
    MAX_GNEWS_PAGE = 10
    page = random.randint(1, MAX_GNEWS_PAGE)
    try:
        news_items = fetch_ai_news(page=page)
        logging.debug(f"Fetched {len(news_items)} news items for page {page}")
        summarized_news = process_news_items(news_items, page)
        logging.debug(f"Processed {len(summarized_news)} news items")
        return render_template('index.html', news=summarized_news, initial_page=page)
    except Exception as e:
        logging.error(f"Error in home route: {e}")
        return render_template('index.html', news=[], initial_page=1)

# Infinite scroll API endpoint
@app.route('/api/news')
def api_news():
    try:
        page = int(request.args.get('page', 1))
        news_items = fetch_ai_news(page=page)
        summarized_news = process_news_items(news_items, page)
        return jsonify(summarized_news)
    except ValueError:
        logging.error("Invalid page parameter")
        return jsonify({'error': 'Invalid page parameter'}), 400
    except Exception as e:
        logging.error(f"Error fetching news for page {page}: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500

@app.route('/api/breaking-news')
def breaking_news() -> Any:
    try:
        news_items = fetch_ai_news(page=1)
        breaking_news = [item.get('title', '') for item in news_items[:5]]
        ticker = ' | '.join(breaking_news)
        return jsonify({'ticker': ticker})
    except Exception as e:
        logging.error(f"Error fetching breaking news: {e}")
        return jsonify({'ticker': 'Failed to load breaking news'}), 500

@app.route('/jobs', methods=['GET', 'POST'])
def jobs() -> Any:
    return render_template('jobs.html')

@app.route('/about')
def about() -> Any:
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
