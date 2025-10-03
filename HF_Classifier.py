import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import time
from tqdm import tqdm
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


class PoliticalClassifier:
    def __init__(self, huggingface_token=None):
        """
        Initialize political classifier
        """
        self.hf_token = huggingface_token
        self.api_url = "https://api-inference.huggingface.co/models/bucketresearch/politicalBiasBERT"

        # Label mapping for the model outputs
        self.label_map = {
            'LABEL_0': 'Left',
            'LABEL_1': 'Center-Left',
            'LABEL_2': 'Center',
            'LABEL_3': 'Center-Right',
            'LABEL_4': 'Right'
        }

    def classify_text(self, text):
        """
        Classify text politically (left, right, neutral)
        """
        if not text or text.strip() == '':
            return None

        # Truncate text if too long (API limit)
        max_length = 500
        if len(text) > max_length:
            text = text[:max_length] + "..."

        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        payload = {"inputs": text}

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()

                # Parse the response (format can vary)
                if result and len(result) > 0:
                    # Sometimes it's a list of lists, sometimes just a list
                    classification = result[0][0] if isinstance(result[0], list) else result[0]

                    # Map the label to readable format
                    original_label = classification.get('label', '')
                    classification['label'] = self.label_map.get(original_label, original_label)

                    return classification
            elif response.status_code == 503:
                time.sleep(20)
                return self.classify_text(text)  # Retry
            else:
                print(f"API Error: Status {response.status_code}")

        except Exception as e:
            print(f"Classification error: {e}")

        return None

    def classify_articles(self, articles, delay=0.1):
        """
        Classify a list of articles that have already been fetched.
        """
        classified_data = []
        failed_count = 0

        for article in tqdm(articles, desc="Classifying"):
            # Combine title and description for classification
            text_to_classify = ""
            if article.get('title'):
                text_to_classify += article['title'] + " "
            if article.get('description'):
                text_to_classify += article['description']

            # Classify the text
            classification = self.classify_text(text_to_classify)

            if classification:
                classified_data.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'political_label': classification.get('label', 'Unknown'),
                    'confidence': classification.get('score', 0),
                    'text_classified': text_to_classify[:200]  # Store snippet
                })
            else:
                failed_count += 1

            # Rate limiting
            time.sleep(delay)

        if failed_count > 0:
            print(f"Failed to classify {failed_count} articles")

        df = pd.DataFrame(classified_data)
        print(f"✓ Successfully classified {len(df)} articles")

        return df


class PoliticalAnalysisVisualizer:
    def __init__(self):
        """Initialize the visualizer with color schemes."""
        self.color_map = {
            'Left': '#0015BC',  # Blue
            'Center-Left': '#6495ED',  # Lighter blue
            'Center': '#808080',  # Gray
            'Center-Right': '#FFA500',  # Orange
            'Right': '#FF0000'  # Red
        }
        self.political_order = ['Left', 'Center-Left', 'Center', 'Center-Right', 'Right']

    def visualize_overall_distribution(self, df, keyword):
        """
        Create visualizations of overall political distribution.
        """
        if df.empty:
            print("No data to visualize!")
            return

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Political Classification Analysis: Homelessness', fontsize=16, fontweight='bold')

        # 1. Overall distribution pie chart
        ax1 = axes[0, 0]
        label_counts = df['political_label'].value_counts()
        colors = [self.color_map.get(label, '#CCCCCC') for label in label_counts.index]

        wedges, texts, autotexts = ax1.pie(label_counts.values,
                                           labels=label_counts.index,
                                           colors=colors,
                                           autopct='%1.1f%%',
                                           startangle=90)
        ax1.set_title('Overall Political Distribution', fontsize=12, fontweight='bold')

        # 2. Distribution bar chart with counts
        ax2 = axes[0, 1]
        ordered_counts = label_counts.reindex(self.political_order, fill_value=0)
        bars = ax2.bar(range(len(ordered_counts)), ordered_counts.values)

        for i, (label, count) in enumerate(zip(ordered_counts.index, ordered_counts.values)):
            bars[i].set_color(self.color_map.get(label, '#CCCCCC'))
            ax2.text(i, count + 0.5, str(count), ha='center', va='bottom')

        ax2.set_xticks(range(len(ordered_counts)))
        ax2.set_xticklabels(ordered_counts.index, rotation=45, ha='right')
        ax2.set_xlabel('Political Leaning')
        ax2.set_ylabel('Number of Articles')
        ax2.set_title('Article Count by Political Leaning', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # 3. Confidence distribution
        ax3 = axes[1, 0]
        for label in self.political_order:
            if label in df['political_label'].values:
                subset = df[df['political_label'] == label]['confidence']
                ax3.hist(subset, alpha=0.6, label=label,
                         color=self.color_map.get(label, '#CCCCCC'), bins=20)

        ax3.set_xlabel('Classification Confidence')
        ax3.set_ylabel('Number of Articles')
        ax3.set_title('Classification Confidence by Political Leaning', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)

        # 4. Timeline of political leanings
        ax4 = axes[1, 1]
        df['date'] = pd.to_datetime(df['published_at']).dt.date
        timeline_data = df.groupby(['date', 'political_label']).size().unstack(fill_value=0)

        # Reorder columns
        available_cols = [col for col in self.political_order if col in timeline_data.columns]
        timeline_data = timeline_data[available_cols]

        timeline_data.plot(kind='area', stacked=True, ax=ax4,
                           color=[self.color_map.get(col, '#CCCCCC') for col in timeline_data.columns],
                           alpha=0.7)

        ax4.set_xlabel('Date')
        ax4.set_ylabel('Number of Articles')
        ax4.set_title('Political Leaning Timeline', fontsize=12, fontweight='bold')
        ax4.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def visualize_by_source(self, df, keyword, top_n=15):
        """
        Visualize political leanings by news source.
        """
        if df.empty:
            print("No data to visualize!")
            return

        # Get top sources by article count
        top_sources = df['source'].value_counts().head(top_n).index
        df_top = df[df['source'].isin(top_sources)]

        # Create crosstab for analysis
        crosstab = pd.crosstab(df_top['source'], df_top['political_label'])

        # Reorder columns
        available_cols = [col for col in self.political_order if col in crosstab.columns]
        crosstab = crosstab[available_cols]

        # Sort by total articles
        crosstab = crosstab.loc[crosstab.sum(axis=1).sort_values(ascending=False).index]

        # Create visualizations
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))
        fig.suptitle(f'Political Classification by News Source: "{keyword}"',
                     fontsize=16, fontweight='bold')

        # 1. Stacked bar chart
        ax1 = axes[0]
        crosstab.plot(kind='barh', stacked=True, ax=ax1,
                      color=[self.color_map.get(col, '#CCCCCC') for col in crosstab.columns])

        ax1.set_xlabel('Number of Articles')
        ax1.set_ylabel('News Source')
        ax1.set_title(f'Top {top_n} Sources: Political Distribution', fontsize=12, fontweight='bold')
        ax1.legend(title='Political Leaning', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(axis='x', alpha=0.3)

        # 2. Heatmap showing percentages
        ax2 = axes[1]

        # Normalize by row to show percentages
        crosstab_pct = crosstab.div(crosstab.sum(axis=1), axis=0) * 100

        sns.heatmap(crosstab_pct, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
                    ax=ax2, cbar_kws={'label': 'Percentage (%)'})

        ax2.set_xlabel('Political Leaning')
        ax2.set_ylabel('News Source')
        ax2.set_title(f'Political Leaning Distribution (%) by Source', fontsize=12, fontweight='bold')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    def create_interactive_visualizations(self, df, keyword):
        """
        Create interactive visualizations using Plotly.
        """
        if df.empty:
            print("No data to visualize!")
            return

        # 1. Sunburst chart: Source -> Political Leaning
        source_political = df.groupby(['source', 'political_label']).size().reset_index(name='count')

        fig_sunburst = px.sunburst(
            source_political,
            path=['source', 'political_label'],
            values='count',
            title=f'Interactive: News Sources and Political Leanings for Homelessness',
            color='political_label',
            color_discrete_map=self.color_map
        )

        fig_sunburst.update_layout(height=600)
        fig_sunburst.show()

        # 2. Sankey diagram
        sources = df['source'].unique()[:20]  # Limit to top 20 sources for readability
        political_labels = df['political_label'].unique()

        # Filter df to only include top sources
        df_filtered = df[df['source'].isin(sources)]

        # Create node labels
        all_nodes = list(sources) + list(political_labels)
        node_indices = {node: i for i, node in enumerate(all_nodes)}

        # Create links
        link_data = df_filtered.groupby(['source', 'political_label']).size().reset_index(name='count')

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=['lightblue'] * len(sources) +
                      [self.color_map.get(label, 'gray') for label in political_labels]
            ),
            link=dict(
                source=[node_indices[source] for source in link_data['source']],
                target=[node_indices[label] for label in link_data['political_label']],
                value=link_data['count'],
                color='rgba(128, 128, 128, 0.2)'
            )
        )])

        fig_sankey.update_layout(
            title_text=f'Flow from News Sources to Political Classifications: "Homelessness"',
            font_size=10,
            height=600
        )
        fig_sankey.show()

    def generate_report(self, df, keyword):
        """
        Generate a detailed text report of the analysis.
        """
        if df.empty:
            print("No data to analyze!")
            return

        print("\n" + "=" * 60)
        print(f"POLITICAL CLASSIFICATION REPORT: 'Homelessness'")
        print("=" * 60)

        # Overall statistics
        print("\nOVERALL STATISTICS:")
        print(f"Total articles analyzed: {len(df)}")
        print(f"Average confidence score: {df['confidence'].mean():.2%}")
        print(f"Number of unique sources: {df['source'].nunique()}")

        # Political distribution
        print("\nPOLITICAL DISTRIBUTION:")
        distribution = df['political_label'].value_counts()
        for label, count in distribution.items():
            percentage = (count / len(df)) * 100
            print(f"  {label}: {count} articles ({percentage:.1f}%)")

        # Most common political leaning
        most_common = distribution.index[0]
        print(f"\nMost common leaning: {most_common} ({distribution[most_common]} articles)")

        # Source analysis
        print("\n📰 TOP SOURCES BY POLITICAL LEANING:")

        for leaning in self.political_order:
            if leaning in df['political_label'].values:
                subset = df[df['political_label'] == leaning]
                top_source = subset['source'].value_counts().head(3)

                if len(top_source) > 0:
                    print(f"\n{leaning}:")
                    for source, count in top_source.items():
                        print(f"  - {source}: {count} articles")

        # Confidence analysis
        print("\nCLASSIFICATION CONFIDENCE:")
        print(f"Highest confidence: {df['confidence'].max():.2%}")
        print(f"Lowest confidence: {df['confidence'].min():.2%}")
        print(f"Standard deviation: {df['confidence'].std():.2%}")

        # High confidence classifications
        high_conf = df[df['confidence'] > 0.9]
        print(f"\nArticles with >90% confidence: {len(high_conf)} ({len(high_conf) / len(df) * 100:.1f}%)")

        # Low confidence classifications
        low_conf = df[df['confidence'] < 0.6]
        print(f"Articles with <60% confidence: {len(low_conf)} ({len(low_conf) / len(df) * 100:.1f}%)")

        # Balance analysis
        print("\nPOLITICAL BALANCE ANALYSIS:")
        left_total = len(df[df['political_label'].isin(['Left', 'Center-Left'])])
        right_total = len(df[df['political_label'].isin(['Right', 'Center-Right'])])
        center_total = len(df[df['political_label'] == 'Center'])

        print(f"Left-leaning (Left + Center-Left): {left_total} ({left_total / len(df) * 100:.1f}%)")
        print(f"Right-leaning (Right + Center-Right): {right_total} ({right_total / len(df) * 100:.1f}%)")
        print(f"Center: {center_total} ({center_total / len(df) * 100:.1f}%)")

        if left_total > right_total * 1.5:
            print("Coverage appears LEFT-LEANING")
        elif right_total > left_total * 1.5:
            print("Coverage appears RIGHT-LEANING")
        else:
            print("Coverage appears RELATIVELY BALANCED")


def classify_and_analyze_articles(articles, keyword, huggingface_token=None,
                                  visualize=True, export=True):

    # Initialize classifier
    print("Initializing political classifier...")
    classifier = PoliticalClassifier(huggingface_token)

    # Classify articles
    df = classifier.classify_articles(articles)

    if df.empty:
        print("No articles could be classified!")
        return df

    # Initialize visualizer
    visualizer = PoliticalAnalysisVisualizer()

    # Generate report
    visualizer.generate_report(df, keyword)

    # Create visualizations if requested
    if visualize:
        visualizer.visualize_overall_distribution(df, keyword)
        visualizer.visualize_by_source(df, keyword)

    # # Export results if requested
    # if export:
    #     export_choice = input("\nExport results to CSV/Excel? (y/n): ").strip().lower()
    #     if export_choice == 'y':
    #         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    #         filename = f"political_analysis_{keyword.replace(' ', '_')}_{timestamp}"
	#
    #         # Export to CSV
    #         df.to_csv(f"{filename}.csv", index=False)
    #         print(f"✓ Results exported to {filename}.csv")
	#
    #         # Export to Excel with multiple sheets
    #         with pd.ExcelWriter(f"{filename}.xlsx", engine='openpyxl') as writer:
    #             df.to_excel(writer, sheet_name='All Articles', index=False)
	#
    #             # Summary sheets
    #             df['political_label'].value_counts().to_frame().to_excel(
    #                 writer, sheet_name='Political Summary'
    #             )
    #             df.groupby('source')['political_label'].value_counts().unstack(fill_value=0).to_excel(
    #                 writer, sheet_name='Source Summary'
    #             )

    return df