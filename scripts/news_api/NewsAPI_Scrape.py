# from collections import Counter, defaultdict
from HF_Classifier import classify_and_analyze_articles
from credentials import * # Local API key storage.
# from datetime import datetime, timedelta
from news_configs import *
from newsapi import NewsApiClient
# from tqdm import tqdm
# from transformers import pipeline
from wordcloud import WordCloud
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
import re
# import requests
# import seaborn as sns
# import time
from Viz import *

# NEWSAPI CONSTANTS
SEARCH_TIME = 30 # Number of days history to search
SOURCES = ['abc-news', 'ars-technica', 'associated-press', 'axios', 'bleacher-report', 'bloomberg', 'breitbart-news',
           'business-insider', 'buzzfeed', 'cbs-news', 'cnn', 'engadget', 'entertainment-weekly', 'espn', 'espn-cric-info',
           'fortune', 'fox-news', 'google-news', 'hacker-news', 'ign', 'mashable', 'medical-news-today', 'msnbc', 'mtv-news',
           'national-geographic', 'national-review', 'nbc-news', 'new-scientist', 'newsweek', 'new-york-magazine', 'politico',
           'polygon', 'recode', 'reddit-r-all', 'reuters', 'techradar', 'the-american-conservative', 'the-hill', 'the-huffington-post',
           'the-verge', 'the-wall-street-journal', 'the-washington-post', 'the-washington-times', 'time', 'usa-today', 'vice-news', 'wired']

class NewsAPIScraper:
    def __init__(self, api_key):
        """
        Initialize the NewsAPI client with API key.
        """
        self.newsapi = NewsApiClient(api_key=api_key)

    def fetch_articles(self, keywords=KEYWORDS_DEFAULT, language='en', page_size=MAX_PAGES):
        """
        Fetch articles from NewsAPI for the given keywords from the last {SEARCH_TIME} days.
        """

        # Calculate date range based on SEARCH_TIME.
        to_date = datetime.now()
        from_date = to_date - timedelta(days=SEARCH_TIME)

        query = ' OR '.join(keywords) # Converts list to query string with logical OR separator between keywords
        sourcelist = ', '.join(SOURCES) # Converts US news source list to string with comma separator

        # Get articles from US news sources containing any of the search term keywords.
        # Error handling for time zone issue where 30 days sometimes throws error for searching too far back for free plan.
        for days in [30, 29]:
            try:
                # Search for articles
                response = self.newsapi.get_everything(
                    q=query,
                    language=language,
                    sources=sourcelist, # Limits to US news sources
                    from_param=from_date.strftime('%Y-%m-%d'),
                    to=to_date.strftime('%Y-%m-%d'),
                    page_size=min(page_size, MAX_PAGES),  # NewsAPI max is 100
                    sort_by='relevancy'
                )

                if response['status'] == 'ok':
                    return response['articles']
                else:
                    print(f"Error fetching articles: {response.get('message', 'Unknown error')}")
                    return []

            except Exception as e:
                if 'too far' in str(e).lower() and days > 29:
                    from_date = to_date - timedelta(days=(SEARCH_TIME - 1)) # Adjust to 29 days during weird time zone window
                    continue
                else:
                    print(f"Exception occurred while fetching articles: {str(e)}")
                    return []

    def extract_article_text(self, articles):
        """
        Extract text from articles (title, description, and content).
        """
        all_text = []

        for article in articles:
            # Add title
            if article.get('title'):
                all_text.append(article['title'])

            # Add description
            if article.get('description'):
                all_text.append(article['description'])

            # Add content
            if article.get('content'):
                # Remove [+chars] if present
                content = re.sub(r'\[\+\d+ chars\]', '', article['content'])
                all_text.append(content)

        # Combine all text
        combined_text = ' '.join(all_text)

        # Basic cleaning
        combined_text = re.sub(r'https?://\S+', '', combined_text)  # Remove URLs
        combined_text = re.sub(r'[^\w\s]', ' ', combined_text)  # Remove special characters
        combined_text = re.sub(r'\s+', ' ', combined_text)  # Remove extra whitespace

        return combined_text

    def generate_wordcloud(self, text):
        """
        Generate and display a word cloud from the text.
        """
        if not text.strip():
            print("No text to generate word cloud from!")
            return None

        # Create custom stopwords list
        stopwords = set(STOPWORDS)

        # Generate word cloud
        wordcloud = WordCloud(
            width=WC_WIDTH,
            height=WC_HEIGHT,
            background_color=WC_BG_COLOR,
            stopwords=stopwords,
            collocations=False,
            max_words=MAX_WORDS,
            colormap=CMAP,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(text)

        # Display the word cloud
        plt.figure(figsize=(WC_WIDTH / 100, WC_HEIGHT / 100))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(f'Word Cloud for US News Articles on Homelessness\nfrom the Last {SEARCH_TIME} Days', fontsize=WC_TITLE_FONT_SIZE, fontweight='bold', pad=WC_TITLE_PADDING)
        plt.axis('off')
        plt.tight_layout(pad=WC_LAYOUT_PADDING)
        plt.show()

        return wordcloud

    def save_wordcloud(self, wordcloud, filename):
        """
        Save the word cloud to a file.
        """
        if wordcloud:
            wordcloud.to_file(filename)
            print(f"Word cloud saved to {filename}")

    def analyze_sources(self, articles):
        """
        Analyze articles by source and create a DataFrame with statistics.
        """
        if not articles:
            print("No articles to analyze!")
            return pd.DataFrame()

        # Extract source information
        sources = []
        for article in articles:
            if article.get('source'):
                source_name = article['source'].get('name', 'Unknown')
                source_id = article['source'].get('id', 'unknown')
                published_at = article.get('publishedAt', '')
                title = article.get('title', '')
                url = article.get('url', '')

                sources.append({
                    'source_name': source_name,
                    'source_id': source_id,
                    'published_at': published_at,
                    'title': title,
                    'url': url
                })

        # Create DataFrame
        df = pd.DataFrame(sources)

        # Store for later use
        self.articles_data = df

        # Create summary statistics
        source_counts = df['source_name'].value_counts()

        summary_df = pd.DataFrame({
            'Source': source_counts.index,
            'Article Count': source_counts.values,
            'Percentage': (source_counts.values / len(df) * 100).round(2)
        })

        return summary_df

    def plot_timeline(self, top_n=5):
        """
        Create a stacked area timeline showing article publication over time by top sources.
        """
        if self.articles_data.empty:
            print('No data to plot!')
            return

        df = self.articles_data.copy()

        # Convert published_at to datetime
        df['published_at'] = pd.to_datetime(df['published_at'])
        df['date'] = df['published_at'].dt.date

        # Get top sources
        top_sources = df['source_name'].value_counts().head(top_n).index

        # Filter for top sources
        df_top = df[df['source_name'].isin(top_sources)]

        # Create pivot table for plotting
        timeline_data = df_top.groupby(['date', 'source_name']).size().reset_index(name='count')
        pivot_df = timeline_data.pivot(index='date', columns='source_name', values='count').fillna(0)

        # Plot stacked area chart
        ax = pivot_df.plot(kind='area', stacked=True, alpha=0.7, figsize=(14, 6))

        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Articles', fontsize=12, fontweight='bold')
        plt.title(f'Article Publication Timeline by Top {top_n} Sources for Homelessness',
                  fontsize=14, fontweight='bold')
        plt.legend(title='News Source', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Looks better than vertical.
    def plot_comparison_horizontal(self, summary_df, top_n=20):
        """
        Create a horizontal bar chart for better readability of source names.
        """
        if summary_df.empty:
            print('No data to plot!')
            return

        # Get top sources
        top_sources = summary_df.head(top_n)

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create horizontal bars
        y_pos = np.arange(len(top_sources))
        bars = ax.barh(y_pos, top_sources['Article Count'])

        # Color bars with gradient
        colors = CMAP(np.linspace(0.3, 0.9, len(top_sources)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        # Customize the plot
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_sources['Source'])
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('Number of Articles', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} News Sources for Homelessness\n(Last {SEARCH_TIME} Days)',
                     fontsize=14, fontweight='bold')

        # Add value labels
        for i, (count, pct) in enumerate(zip(top_sources['Article Count'],
                                             top_sources['Percentage'])):
            ax.text(count + 0.5, i, f'{count}',
                    va='center', fontsize=9)

        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.show()

    def get_source_statistics(self, summary_df):
        """
        Calculate and display source statistics.
        """
        if summary_df.empty:
            print('No data to analyze!')
            return {}

        stats = {
            'total_sources': len(summary_df),
            'total_articles': summary_df['Article Count'].sum(),
            'avg_articles_per_source': summary_df['Article Count'].mean(),
            'median_articles_per_source': summary_df['Article Count'].median(),
            'std_articles_per_source': summary_df['Article Count'].std(),
            'top_source': summary_df.iloc[0]['Source'],
            'top_source_count': summary_df.iloc[0]['Article Count'],
            'top_source_percentage': summary_df.iloc[0]['Percentage']
        }

        # Sources contributing to 50% of content
        cumsum = summary_df['Percentage'].cumsum()
        sources_for_50_pct = len(cumsum[cumsum <= 50]) + 1
        stats['sources_for_50_pct_coverage'] = sources_for_50_pct

        # Sources with only 1 article
        single_article_sources = len(summary_df[summary_df['Article Count'] == 1])
        stats['single_article_sources'] = single_article_sources

        return stats

    def export_results(self, summary_df, filename=None):
        """
        Export the analysis results to .csv
        """
        if summary_df.empty:
            print('No data to export!')
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'news_sources_{timestamp}'

        # Export to CSV
        csv_file = f'{filename}.csv'
        summary_df.to_csv(csv_file, index=False)
        print(f'Results exported to {csv_file}')


def main():

    api_key = NEWSAPI_KEY  # Imported from local file credentials.py.

    # Create scraper instance
    scrape = NewsAPIScraper(api_key)

    # Fetch articles
    articles = scrape.fetch_articles()

    if not articles:
        print('No articles found!')
        return

    # Extract text from articles
    text = scrape.extract_article_text(articles)

    # Generate word cloud
    wordcloud = scrape.generate_wordcloud(text)

    # # Optionally save the word cloud
    # save_option = input('\nSave word cloud to file? (y/n): ').strip().lower()
    # if save_option == 'y':
    #     filename = f'news_wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png'
    #     scrape.save_wordcloud(wordcloud, filename)

    summary_df = scrape.analyze_sources(articles)
    stats = scrape.get_source_statistics(summary_df)

    # for key, value in stats.items():
    #     print(f'{key.replace('_', ' ').title()}: {value}')

    # Create visualizations

    # Horizontal bar chart
    scrape.plot_comparison_horizontal(summary_df, top_n=20)

    # # Timeline
    # scrape.plot_timeline(top_n=10)

    # # Export results
    # export_option = input('\nExport results to CSV? (y/n): ').strip().lower()
    # if export_option == 'y':
    #     scrape.export_results(summary_df)

    # Political classification

    class_df = classify_and_analyze_articles(articles, 'homelessness', HUGGINGFACE_TOKEN, visualize=False)
    safe_visualize_temporal_patterns(class_df, 'homelessness')

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Political Classification Analysis: "Homelessness"', fontsize=16, fontweight='bold')

    # 1. Overall distribution pie chart
    ax1 = axes[0, 0]
    label_counts = class_df['political_label'].value_counts()
    predefined_colors = ['#013364', '#cbcaca','#d30b0d']
    colors = [predefined_colors[label] for label in label_counts.index]

    wedges, texts, autotexts = ax1.pie(label_counts.values,
                                       labels=label_counts.index,
                                       colors=colors,
                                       autopct='%1.1f%%',
                                       startangle=90)
    ax1.set_title('Overall Political Distribution', fontsize=12, fontweight='bold')


if __name__ == '__main__':
    main()