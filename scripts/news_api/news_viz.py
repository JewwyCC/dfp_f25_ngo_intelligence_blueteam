import pandas as pd
import plotly.graph_objects as go
import numpy as np
from news_configs import *
from wordcloud import WordCloud


class Visualizations:

    def __init__(self, df, keyword):
        """
        Initialize with classified articles DataFrame.
        """
        self.articles_data = None
        self.df = df.copy()
        self.keyword = keyword

        # Prepare temporal data
        # self.df['date'] = pd.to_datetime(self.df['date']).dt.date
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce', utc=True)


    def analyze_sources(self, articles):
        """
        Analyze articles by source and create a DataFrame with statistics.
        """

        # Extract source information
        sources = []
        for article in articles:
            source_name = article['source']
            date = article['date']
            title = article['title']
            url = article['url']

            sources.append({
                'source_name': source_name,
                'date': date,
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


    def plot_comparison_horizontal(self, summary_df, top_n=20):
        """
        Create a horizontal bar chart for better readability of source names.
        """

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


    def generate_wordcloud(self, text):
        """
        Generate and display a word cloud from the text.
        """

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
        plt.title(f'Word Cloud for US News Articles on Homelessness\nfrom the Last 30 Days', fontsize=WC_TITLE_FONT_SIZE, fontweight='bold', pad=WC_TITLE_PADDING)
        plt.axis('off')
        plt.tight_layout(pad=WC_LAYOUT_PADDING)
        plt.show()

        return wordcloud

    def pie_chart(self, df):
        """
        Generate pie chart of political classification from dataframe.
        """
        plt.figure(figsize=(8, 8))

        label_counts = df['leaning'].value_counts()

        # Create a color mapping dictionary
        color_map = {
            'LEFT': '#013364',  # Blue for left
            'CENTER': '#cbcaca',  # Gray for center
            'RIGHT': '#d30b0d'  # Red for right
        }

        # Map colors to the actual labels in the data
        colors = [color_map[label] for label in label_counts.index]

        plt.pie(label_counts.values,
                labels=label_counts.index,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90)

        plt.title('Media Article by Political Leaning', fontsize=12, fontweight='bold')
        plt.show()


class PoliticalAnalysisVisualizer:

    def __init__(self):
        """Initialize the visualizer with color schemes."""
        self.color_map = {
            'LEFT': '#013364',  # Blue for left
            'CENTER': '#cbcaca',  # Gray for center
            'RIGHT': '#d30b0d'  # Red for right
        }
        self.political_order = ['Left', 'Center', 'Right']


    def political_timeline(self, df):
        """
        Fixed version: Creates timeline with 3 lines (left, center, right).
        """
        # Prepare data
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        df = df[df['date'].notna()]
        df['date_day'] = df['date'].dt.date

        # Group articles by date and political classification.
        daily_counts = df.groupby(['date_day', 'leaning']).size().reset_index(name='count')
        timeline_data = daily_counts.pivot(index='date_day', columns='leaning', values='count')
        timeline_data = timeline_data.fillna(0)

        # Plot figure.
        plt.figure(figsize=(14, 7))

        # Plot each line with different colors
        if 'LEFT' in timeline_data.columns:
            plt.plot(timeline_data.index, timeline_data['LEFT'],
                     marker='o', linewidth=2, color='#3366CC', label='LEFT')

        if 'CENTER' in timeline_data.columns:
            plt.plot(timeline_data.index, timeline_data['CENTER'],
                     marker='s', linewidth=2, color='#808080', label='CENTER')

        if 'RIGHT' in timeline_data.columns:
            plt.plot(timeline_data.index, timeline_data['RIGHT'],
                     marker='^', linewidth=2, color='#CC3333', label='RIGHT')

        plt.xlabel('Date')
        plt.ylabel('Number of Articles')
        plt.title('Political Leaning Timeline')
        plt.legend(title='Political Leaning')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


    def visualize_by_source(self, df, top_n=25):
        """
        Visualize political leanings by news source.
        """

        # Get top sources by article count
        top_sources = df['source'].value_counts().head(top_n).index
        df_top = df[df['source'].isin(top_sources)]

        # Create crosstab for analysis
        crosstab = pd.crosstab(df_top['source'], df_top['leaning'])

        # Reorder columns
        available_cols = [col for col in self.political_order if col in crosstab.columns]
        crosstab = crosstab[available_cols]

        # Sort by total articles
        crosstab = crosstab.loc[crosstab.sum(axis=1).sort_values(ascending=False).index]

        # Create visualizations
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))
        fig.suptitle(f'Political Classification by News Source: Homelessness',
                     fontsize=16, fontweight='bold')


    def create_interactive_visualizations(self, df):
        """
        Create interactive visualizations using Plotly.
        """
       # Sankey diagram
        sources = df['source'].unique()[:20]  # Limit to top 20 sources for readability
        political_labels = df['leaning'].unique()

        # Filter df to only include top sources
        df_filtered = df[df['source'].isin(sources)]

        # Create node labels
        all_nodes = list(sources) + list(political_labels)
        node_indices = {node: i for i, node in enumerate(all_nodes)}

        # Create links
        link_data = df_filtered.groupby(['source', 'leaning']).size().reset_index(name='count')

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=['purple'] * len(sources) +
                      [self.color_map.get(label, self.color_map[label]) for label in political_labels]
            ),
            link=dict(
                source=[node_indices[source] for source in link_data['source']],
                target=[node_indices[label] for label in link_data['leaning']],
                value=link_data['count'],
                color='rgba(128, 128, 128, 0.2)'
            )
        )])

        fig_sankey.update_layout(
            title_text=f'Flow from News Sources to Political Classifications: "Homelessness"',
            font_size=10,
            height=600
        )
        # fig_sankey.show()
        fig_sankey.write_html('sankey_diagram.html', auto_open=False)