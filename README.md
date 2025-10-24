# AI Tak

A visually stunning, multi-page news and job portal for Artificial Intelligence news and jobs in India.

## Features
- Trending global AI news (live, summarized)
- Animated breaking news ticker
- News cards with summaries, tags, and links
- AI-themed, responsive UI (dark mode, gradients, animations)
- Job search for India, Karnataka, Maharashtra, Tamil Nadu, Telangana (dynamic links for LinkedIn, Naukri, Google Jobs)
- About page with sources and tech stack

## Tech Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: Python Flask
- AI Summarization: OpenRouter API
- News Source: NewsData.io or NewsAPI.org
- Ai Summarizer : OpenRouter API Key

## Setup Instructions
1. Clone/download this repo.
2. Install dependencies:
   ```bash
   pip install flask requests
   ```
3. Set up your API keys for NewsData.io/NewsAPI and OpenRouter in environment variables or a `.env` file.
4. Run the app:
   ```bash
   python app.py
   ```
5. Open http://localhost:5000 in your browser.

## Folder Structure
- `app.py` - Main Flask app
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JS, images
- `utils/` - Helper functions (API, summarization, caching)
- `.github/` - Copilot instructions

## Notes
- All news and job data is fetched live; fallback to sample data if API quota is exceeded.
- No scraping is used for jobs; only dynamic search links.

---

© 2025 AI Tak. For educational/demo use only.
