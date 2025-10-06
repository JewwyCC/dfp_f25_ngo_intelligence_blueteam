import matplotlib.pyplot as plt

# Consolidating common customization parameters in one place for easier editing while working on the front end

### Data Viz Settings ###

# Change cmap name here to change color map for all news data viz.
CMAP = getattr(plt.cm, 'viridis')

## Word Cloud Settings ##
# News word cloud terms to drop
STOPWORDS = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'is', 'are', 'was', 'were',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'say',
            'could', 'may', 'might', 'must', 'shall', 'can', 'need', 'this', 'that', 'these', 'not'
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'U',
            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'D',
            's', 't', 'just', 'don', 'now', 'npr', 'news', 'says', 'said', 'new', 'year', 'years', 'US',
            'one', 'two', 'said', 'her', 'hers', 'him', 'his', 'Eva', 'Brian', 'Marie', 'as', 'told',
            'there', 'here', 'part', 'if', 'Gaza', 'Ukraine', 'Ukrainian', 'Iryna', 'C', 'after', 'zarutska'
            'Zarutska', 'chars', 'its', 'xbox', 'homelessness', 'homeless', 'Homelessness', 'Homeless']

MAX_WORDS = 100 # Maximum number of words to include in word cloud
WC_BG_COLOR = 'white' # Word cloud background color
WC_LAYOUT_PADDING = 1
WC_TITLE_FONT_SIZE = 12
WC_TITLE_PADDING = 15
WC_HEIGHT = 400 # Word cloud height
WC_WIDTH = 700 # Word cloud width


### News Search Settings ###

DELAY = 1.0 # Wait time in seconds between requests

# Default keyword list for testing and fallback if issue with Google Trend pull
KEYWORDS_DEFAULT = ['homeless', 'what is homelessness', 'end homelessness', 'homelessness in america', 'california homelessness']
NPR_KEYWORD = 'homelessness'

# Article scrape page load max. Leave as 100 unless errors.
MAX_PAGES = 100

# NEWSAPI CONSTANTS
SEARCH_TIME = 30 # Number of days history to search
SOURCES = ['abc-news', 'ars-technica', 'associated-press', 'axios', 'bleacher-report', 'bloomberg', 'breitbart-news',
           'buzzfeed', 'cbs-news', 'cnn', 'engadget', 'entertainment-weekly', 'espn', 'espn-cric-info',
           'fortune', 'fox-news', 'google-news', 'hacker-news', 'ign', 'mashable', 'medical-news-today', 'msnbc', 'mtv-news',
           'national-geographic', 'national-review', 'nbc-news', 'new-scientist', 'newsweek', 'new-york-magazine', 'politico',
           'polygon', 'recode', 'reddit-r-all', 'reuters', 'techradar', 'the-american-conservative', 'the-hill', 'the-huffington-post',
           'the-verge', 'the-wall-street-journal', 'the-washington-post', 'the-washington-times', 'time', 'usa-today', 'vice-news', 'wired']