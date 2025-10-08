from combined_news_analyzer import *
from news_credentials import *
from news_viz import * # Data visualizations
from NewsPoliticalClassifier import * # Classify articles

def main():

    loading_dict ={
        'Wordcloud': False,
        'Outlet Article Count': False,
        'Political Pie Chart': False,
        'Political Timeline': False,
        'Media Outlet Political Classification': False
    }

    news_loading_status = False

    ### Fetch articles ###

    # Initialize scraper.
    scrape = CombinedNewsAnalyzer(newsapi_key=NEWSAPI_KEY)

    # Fetch and combine articles from NewsAPI and NPR, and combine.
    combined_articles: list[dict] = scrape.combine_sources()
    print(combined_articles)

    # Update NPR labels.
    search_string = 'section_/sections/'
    npr = 'NPR'

    for article in combined_articles:
        if search_string in article['source']:
            article['source'] = npr

    # Output article data.
    scrape.save_combined_data('combined_articles.json')

    # Initialize classifier.
    classifier = PoliticalLeaningClassifier()

    # Classify all articles.
    classified_articles: list[dict] = classifier.classify_batch(combined_articles)

    # Convert classified articles to DataFrame.
    class_df = pd.DataFrame(classified_articles)

    class_df.to_csv('classified.csv', index=False)


    ### Create visualizations ###

    # Initialize visualizer.
    viz = Visualizations(class_df, 'homelessness')

    # Get summary stats
    summary_df = viz.analyze_sources(classified_articles)

    # Generate word cloud
    text = scrape.all_text(combined_articles)
    wordcloud = viz.generate_wordcloud(text)
    loading_dict['Wordcloud'] = True
    #
    # Horizontal bar chart
    viz.plot_comparison_horizontal(summary_df, top_n=25)
    loading_dict['Outlet Article Count'] = True

    # Pie Chart of Overall Political Leaning Distribution for All Articles
    viz.pie_chart(class_df)
    loading_dict['Political Pie Chart'] = True

    # Initialize political visualizer.
    poli_viz = PoliticalAnalysisVisualizer()

    # Timeline
    poli_viz.political_timeline(class_df)
    loading_dict['Political Timeline'] = True

    # Media Outlet by Political Classification
    poli_viz.create_interactive_visualizations(class_df)
    loading_dict['Media Outlet Political Classification'] = True

    # Update news progress status.
    if all(loading_dict.values()):
        news_loading_status = True


if __name__ == '__main__':
    main()