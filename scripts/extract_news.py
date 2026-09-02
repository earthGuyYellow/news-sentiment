import os
import requests
import feedparser
import psycopg2
from pydantic import BaseModel
from datetime import datetime
from time import mktime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# 1. Schema definition for tech articles
class STEMArticle(BaseModel):
    article_id: str
    title: str
    source: str
    url: str
    published_at: datetime
    summary: str
    sentiment_score: float


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_DB_HOST", "postgres"),
        port=os.getenv("WAREHOUSE_DB_PORT", "5432"),
        dbname=os.getenv("WAREHOUSE_DB_NAME", "stem_warehouse"),
        user=os.getenv("WAREHOUSE_DB_USER", "airflow"),
        password=os.getenv("WAREHOUSE_DB_PASSWORD", "airflow"),
    )


def init_staging_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE SCHEMA IF NOT EXISTS staging;
        CREATE TABLE IF NOT EXISTS staging.raw_stem_articles (
            article_id VARCHAR(255) PRIMARY KEY,
            title TEXT NOT NULL,
            source VARCHAR(100) NOT NULL,
            url TEXT NOT NULL,
            published_at TIMESTAMP NOT NULL,
            summary TEXT,
            sentiment_score NUMERIC(5,4),
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


# 2. Fetch from RSS Feeds (TechCrunch, Wired, Ars Technica)
def fetch_rss_tech_news(analyzer):
    rss_feeds = [
        {"source": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {
            "source": "Ars Technica",
            "url": "https://feeds.arstechnica.com/arstechnica/index",
        },
        {
            "source": "Wired Tech",
            "url": "https://www.wired.com/feed/category/business/latest/rss",
        },
    ]

    clean_articles = []
    for feed_info in rss_feeds:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:10]:
                text_to_analyze = f"{entry.title}. {entry.get('summary', '')}"
                sentiment = analyzer.polarity_scores(text_to_analyze)["compound"]

                # Parse RSS timestamp safely
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                else:
                    pub_date = datetime.utcnow()

                article_id = f"rss_{hash(entry.link)}"

                clean_articles.append(
                    STEMArticle(
                        article_id=str(article_id),
                        title=entry.title,
                        source=feed_info["source"],
                        url=entry.link,
                        published_at=pub_date,
                        summary=entry.get("summary", "")[:500],
                        sentiment_score=sentiment,
                    )
                )
        except Exception as e:
            print(f"Error fetching RSS from {feed_info['source']}: {e}")

    return clean_articles


# 3. Optional: Fetch from NewsAPI for specific Tech Giants
def fetch_newsapi_tech_news(analyzer, api_key: str):
    if not api_key or api_key == "your_actual_newsapi_key_here":
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": '("NVIDIA" OR "OpenAI" OR "Apple AI" OR "Microsoft AI" OR "Google Gemini" OR "Meta AI" OR "Anthropic" OR "Artificial Intelligence" OR "Local AI")',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": api_key,
    }

    clean_articles = []
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("articles", []):
                text_to_analyze = f"{item['title']}. {item.get('description', '')}"
                sentiment = analyzer.polarity_scores(text_to_analyze)["compound"]

                article_id = f"newsapi_{hash(item['url'])}"
                clean_articles.append(
                    STEMArticle(
                        article_id=str(article_id),
                        title=item["title"],
                        source=item["source"]["name"],
                        url=item["url"],
                        published_at=item["publishedAt"],
                        summary=item.get("description", "") or "",
                        sentiment_score=sentiment,
                    )
                )
    except Exception as e:
        print(f"Error fetching NewsAPI tech news: {e}")

    return clean_articles


def fetch_and_stage_news():
    analyzer = SentimentIntensityAnalyzer()
    newsapi_key = os.getenv("NEWSAPI_KEY", "")

    articles = fetch_rss_tech_news(analyzer) + fetch_newsapi_tech_news(
        analyzer, newsapi_key
    )

    conn = get_db_connection()
    cur = conn.cursor()
    upsert_query = """
        INSERT INTO staging.raw_stem_articles 
        (article_id, title, source, url, published_at, summary, sentiment_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (article_id) DO UPDATE SET
            title = EXCLUDED.title,
            summary = EXCLUDED.summary,
            sentiment_score = EXCLUDED.sentiment_score,
            ingested_at = CURRENT_TIMESTAMP;
    """

    for a in articles:
        cur.execute(
            upsert_query,
            (
                a.article_id,
                a.title,
                a.source,
                a.url,
                a.published_at,
                a.summary,
                a.sentiment_score,
            ),
        )

    conn.commit()
    print(f"Successfully staged {len(articles)} tech articles.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    init_staging_table()
    fetch_and_stage_news()
