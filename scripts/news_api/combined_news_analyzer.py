import json
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from news_configs import *
from newsapi import NewsApiClient
from typing import List, Dict
from urllib.parse import urljoin

class CombinedNewsAnalyzer:
    """
    Combines NPR web scraping with NewsAPI results for comprehensive news analysis
    """

    def __init__(self, newsapi_key: str, delay: float = DELAY):
        """
        Initialize the combined analyzer
        """
        self.newsapi_key = newsapi_key
        self.newsapi = NewsApiClient(api_key=newsapi_key)
        self.combined_articles = []
        self.npr_articles = []
        self.newsapi_articles = []

        # NPR scraping
        self.base_url = "https://www.npr.org"
        self.delay = delay
        self.search_base = "https://www.npr.org/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })

    def fetch_newsapi_articles(self, keyword: list = KEYWORDS_DEFAULT, days_back: int = SEARCH_TIME, page_size: int = MAX_PAGES) -> List[Dict]:
        """
        Fetch articles from NewsAPI
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        query = ' OR '.join(keyword)  # Converts list to query string with logical OR separator between keywords
        sourcelist = ', '.join(SOURCES)  # Converts US news source list to string with comma separator

        # Get articles from US news sources containing any of the search term keywords.
        # Error handling for time zone issue where 30 days sometimes throws error for searching too far back for free plan.
        for days in [30, 29]:
            try:
                # Search for articles
                response = self.newsapi.get_everything(
                    q=query,
                    language='en',
                    sources=sourcelist,  # Limits to US news sources
                    from_param=from_date.strftime('%Y-%m-%d'),
                    to=to_date.strftime('%Y-%m-%d'),
                    page_size=min(page_size, MAX_PAGES),  # NewsAPI max is 100
                    sort_by='relevancy'
                )

                if response['status'] == 'ok':
                    articles = response['articles']

                    # Standardize article format
                    standardized = []
                    for article in articles:
                        standardized.append({
                            'source': article.get('source', {}).get('name', 'NewsAPI'),
                            'title': article.get('title', ''),
                            'text': self._combine_text(
                                article.get('title', ''),
                                article.get('description', ''),
                                article.get('content', '')
                            ),
                            'url': article.get('url', ''),
                            'date': article.get('publishedAt', ''),
                            'author': article.get('author', 'Unknown'),
                            'api_source': 'newsapi'
                        })

                    self.newsapi_articles = standardized
                    return standardized

                else:
                    print(f"Error fetching articles: {response.get('message', 'Unknown error')}")
                    return []

            except Exception as e:
                if 'too far' in str(e).lower() and days > 29:
                    from_date = to_date - timedelta(
                        days=(SEARCH_TIME - 1))  # Adjust to 29 days during weird time zone window
                    continue
                else:
                    print(f"Exception occurred while fetching articles: {str(e)}")
                    return []


    def scrape_npr_articles(self, keyword: str = NPR_KEYWORD, days_back: int = SEARCH_TIME) -> List[Dict]:
        """
        Scrape articles from NPR website
        """

        all_articles = []

        # Method 1: Use NPR's search functionality
        search_articles = self._search_method(keyword)
        all_articles.extend(search_articles)

        # Method 2: Check main news sections
        section_articles = self._section_method(keyword)
        all_articles.extend(section_articles)

        # Remove duplicates based on URL
        unique_articles = []
        seen_urls = set()
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        # Fetch full content for each article
        final_articles = []
        for i, article in enumerate(unique_articles, 1):

            # Fetch full content
            content_data = self._fetch_article_content(article['url'])

            if content_data['word_count'] > 100:  # Only keep substantial articles
                article['text'] = content_data['content']
                article['date'] = content_data['date']
                article['word_count'] = content_data['word_count']
                article['author'] = content_data['author']

                final_articles.append(article)

            time.sleep(self.delay)

        self.articles_collected = final_articles
        return final_articles


    def _search_method(self, keyword: str) -> List[Dict]:
        """
        Method 1: Use NPR's search page
        """
        articles = []

        for page in range(1, MAX_PAGES + 1):
            try:
                # NPR search URL with pagination
                params = {
                    'query': keyword,
                    'page': page
                }

                response = self.session.get(self.search_base, params=params, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # NPR search results structure
                # Look for search result containers
                search_results = soup.find_all('article', class_='item')

                if not search_results:
                    # Alternative: look for h2 tags with class "title"
                    search_results = soup.find_all('h2', class_='title')

                if not search_results:
                    # Another pattern: divs with search-result class
                    search_results = soup.find_all('div', class_=re.compile('search-result|story-text'))

                for result in search_results:
                    # Extract article link and title
                    link_elem = result.find('a', href=True)
                    if not link_elem:
                        # Try parent element
                        parent = result.find_parent()
                        if parent:
                            link_elem = parent.find('a', href=True)

                    if link_elem:
                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = urljoin(self.base_url, url)

                        # Get title
                        title = link_elem.get_text(strip=True)
                        if not title:
                            title_elem = result.find(['h1', 'h2', 'h3', 'h4'])
                            title = title_elem.get_text(strip=True) if title_elem else "Untitled"

                        # Get teaser/summary if available
                        teaser = ""
                        teaser_elem = result.find('p', class_='teaser')
                        if teaser_elem:
                            teaser = teaser_elem.get_text(strip=True)

                        articles.append({
                            'title': title,
                            'url': url,
                            'teaser': teaser,
                            'source': 'search'
                        })

                # Check if there are more pages
                next_link = soup.find('a', {'class': 'next'}) or soup.find('a', string=re.compile('Next'))
                if not next_link and page == 1 and len(search_results) == 0:
                    break

            except Exception as e:
                print(f"  Error on search page {page}: {e}")
                break

            time.sleep(self.delay)

        return articles


    def _section_method(self, keyword: str) -> List[Dict]:
        """
        Method 2: Check main NPR news sections
        """
        articles = []

        sections = [
            '/sections/news/',
            '/sections/politics/',
            '/sections/health/',
            '/sections/science/',
            '/sections/technology/',
            '/sections/business/',
            '/sections/world/',
            '/sections/national/'
        ]

        for section in sections:
            try:
                url = urljoin(self.base_url, section)

                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find article containers in sections
                article_items = soup.find_all('article', class_='item')

                if not article_items:
                    # Alternative: look for divs with article info
                    article_items = soup.find_all('div', class_=re.compile('article|story'))

                for item in article_items:
                    # Check if keyword appears in the article preview
                    item_text = item.get_text(strip=True).lower()
                    if keyword in item_text:
                        # Extract article details
                        link_elem = item.find('a', href=True)
                        if link_elem:
                            article_url = link_elem['href']
                            if not article_url.startswith('http'):
                                article_url = urljoin(self.base_url, article_url)

                            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                            title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)

                            articles.append({
                                'title': title,
                                'url': article_url,
                                'source': f'section_{section}'
                            })

                time.sleep(0.5)

            except Exception as e:
                print(f"  Error checking section {section}: {e}")

        return articles


    def _fetch_article_content(self, url: str) -> Dict:
        """
        Fetch and extract the full content of an NPR article
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts and styles
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()

            # Extract article content
            content = ""

            # NPR article body selectors
            selectors = [
                'div.storytext',
                'div[class*="story-text"]',
                'div.transcript',
                'article[class*="story"]',
                'div#storytext',
                'div.story-wrap',
                'main article'
            ]

            for selector in selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                        break

            # Fallback: get all paragraphs
            if not content:
                all_paragraphs = soup.find_all('p')
                content_paragraphs = [
                    p.get_text(strip=True) for p in all_paragraphs
                    if len(p.get_text(strip=True)) > 50
                ]
                if content_paragraphs:
                    content = ' '.join(content_paragraphs)

            # Extract date
            date = None
            date_elem = soup.find('time')
            if date_elem:
                date = date_elem.get('datetime', date_elem.get_text(strip=True))
            else:
                # Look for date in meta tags
                meta_date = soup.find('meta', {'property': 'article:published_time'})
                if meta_date:
                    date = meta_date.get('content', '')

            # Extract author
            author = None
            author_elem = soup.find('span', class_='byline__name')
            if not author_elem:
                author_elem = soup.find('p', class_='byline')
            if author_elem:
                author = author_elem.get_text(strip=True)

            return {
                'content': content,
                'date': date,
                'author': author,
                'word_count': len(content.split()) if content else 0
            }

        except Exception as e:
            print(f"    Error fetching article: {e}")
            return {'content': '', 'date': None, 'author': None, 'word_count': 0}

    def _combine_text(self, *texts) -> str:
        """
        Combine multiple text fields into one
        """

        combined = ' '.join(filter(None, texts))
        # Remove HTML tags if present
        combined = re.sub('<.*?>', '', combined)

        return combined.strip()

    def combine_sources(self, keywords: list = KEYWORDS_DEFAULT, days_back: int = SEARCH_TIME) -> List[Dict]:
        """
        Fetch and combine articles from both NPR and NewsAPI
        """

        # Fetch from both sources.
        newsapi_articles = self.fetch_newsapi_articles(keywords, days_back)
        npr_articles = self.scrape_npr_articles(NPR_KEYWORD, days_back)

        # Combine all articles.
        self.combined_articles = newsapi_articles + npr_articles

        return self.combined_articles

    def all_text(self, articles: List[Dict]) -> str:
        """
        Generate word cloud from combined sources
        """

        # Combine all text
        all_text = ' '.join([article['text'] for article in self.combined_articles])

        # Clean text
        all_text = re.sub(r'[^\w\s]', ' ', all_text.lower())
        all_text = re.sub(r'\s+', ' ', all_text)

        return all_text


    def save_combined_data(self, filename: str = 'combined_articles.json'):
        """
        Save combined article data to JSON
        """
        output_data = {
            'metadata': {
                'total_articles': len(self.combined_articles),
                'newsapi_count': len(self.newsapi_articles),
                'npr_count': len(self.npr_articles),
                'generated_at': datetime.now().isoformat()
            },
            'articles': self.combined_articles
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✓ Combined data saved to: {filename}")
