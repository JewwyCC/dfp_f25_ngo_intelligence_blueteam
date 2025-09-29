#!/usr/bin/env python3
"""
Comprehensive Homelessness Keywords for Bluesky Data Collection
DFP F25 Social Media Blue Team - Enhanced Scraper

This module contains extensive keyword lists for comprehensive homelessness data collection
from Bluesky, organized by categories for better search coverage.
"""

# Core homelessness terms
CORE_HOMELESSNESS_KEYWORDS = [
    'homeless', 'homelessness', 'homeless person', 'homeless people',
    'unhoused', 'unhoused person', 'unhoused people', 'housing insecure',
    'street homeless', 'chronically homeless', 'temporarily homeless',
    'homeless crisis', 'homeless epidemic', 'homeless population'
]

# Action-oriented terms
ACTION_KEYWORDS = [
    'end homelessness', 'solve homelessness', 'fight homelessness',
    'combat homelessness', 'address homelessness', 'tackle homelessness',
    'prevent homelessness', 'reduce homelessness', 'eliminate homelessness',
    'homelessness prevention', 'homelessness intervention', 'homelessness solution'
]

# Geographic terms
GEOGRAPHIC_KEYWORDS = [
    'homelessness in america', 'homelessness in california', 'homelessness in new york',
    'homelessness in texas', 'homelessness in florida', 'homelessness in washington',
    'homelessness in oregon', 'homelessness in seattle', 'homelessness in los angeles',
    'homelessness in san francisco', 'homelessness in portland', 'homelessness in austin',
    'homelessness in denver', 'homelessness in chicago', 'homelessness in boston',
    'homelessness in miami', 'homelessness in phoenix', 'homelessness in las vegas',
    'homelessness in san diego', 'homelessness in oakland', 'homelessness in sacramento'
]

# Policy and political terms
POLICY_KEYWORDS = [
    'homelessness policy', 'homelessness legislation', 'homelessness funding',
    'homelessness budget', 'homelessness bill', 'homelessness law',
    'homelessness reform', 'homelessness initiative', 'homelessness program',
    'homelessness services', 'homelessness support', 'homelessness assistance',
    'homelessness housing', 'affordable housing', 'public housing',
    'housing first', 'rapid rehousing', 'permanent supportive housing'
]

# Demographic and social terms
DEMOGRAPHIC_KEYWORDS = [
    'homeless veterans', 'homeless youth', 'homeless families', 'homeless children',
    'homeless women', 'homeless men', 'homeless seniors', 'homeless elderly',
    'homeless lgbtq', 'homeless disabled', 'homeless mental health',
    'homeless addiction', 'homeless substance abuse', 'homeless domestic violence',
    'homeless refugees', 'homeless immigrants', 'homeless students'
]

# Crisis and emergency terms
CRISIS_KEYWORDS = [
    'homelessness crisis', 'homelessness emergency', 'homelessness disaster',
    'homelessness surge', 'homelessness spike', 'homelessness increase',
    'homelessness rise', 'homelessness growth', 'homelessness explosion',
    'homelessness epidemic', 'homelessness pandemic', 'homelessness outbreak'
]

# Service and support terms
SERVICE_KEYWORDS = [
    'homeless shelter', 'homeless services', 'homeless outreach', 'homeless support',
    'homeless assistance', 'homeless aid', 'homeless help', 'homeless care',
    'homeless resources', 'homeless programs', 'homeless organizations',
    'homeless charities', 'homeless nonprofits', 'homeless advocacy',
    'homeless rights', 'homeless dignity', 'homeless respect'
]

# Economic and financial terms
ECONOMIC_KEYWORDS = [
    'homelessness cost', 'homelessness economics', 'homelessness finance',
    'homelessness spending', 'homelessness investment', 'homelessness money',
    'homelessness budget', 'homelessness funding', 'homelessness cost',
    'homelessness price', 'homelessness expense', 'homelessness burden',
    'homelessness impact', 'homelessness effect', 'homelessness consequence'
]

# Research and data terms
RESEARCH_KEYWORDS = [
    'homelessness data', 'homelessness statistics', 'homelessness numbers',
    'homelessness count', 'homelessness survey', 'homelessness study',
    'homelessness research', 'homelessness report', 'homelessness analysis',
    'homelessness trends', 'homelessness patterns', 'homelessness insights'
]

# Hashtag variations
HASHTAG_KEYWORDS = [
    '#homeless', '#homelessness', '#unhoused', '#housingcrisis',
    '#endhomelessness', '#homelessnesscrisis', '#housingfirst',
    '#affordablehousing', '#homelessnessawareness', '#homelessnessprevention',
    '#homelessnesssupport', '#homelessnessadvocacy', '#homelessnessrights'
]

# Combined comprehensive list
ALL_HOMELESSNESS_KEYWORDS = (
    CORE_HOMELESSNESS_KEYWORDS +
    ACTION_KEYWORDS +
    GEOGRAPHIC_KEYWORDS +
    POLICY_KEYWORDS +
    DEMOGRAPHIC_KEYWORDS +
    CRISIS_KEYWORDS +
    SERVICE_KEYWORDS +
    ECONOMIC_KEYWORDS +
    RESEARCH_KEYWORDS +
    HASHTAG_KEYWORDS
)

# Keywords for location metadata extraction
LOCATION_INDICATORS = [
    'in california', 'in new york', 'in texas', 'in florida', 'in washington',
    'in oregon', 'in seattle', 'in los angeles', 'in san francisco', 'in portland',
    'in austin', 'in denver', 'in chicago', 'in boston', 'in miami',
    'in phoenix', 'in las vegas', 'in san diego', 'in oakland', 'in sacramento',
    'in downtown', 'in the city', 'in the area', 'in this city', 'in my city',
    'in our city', 'in the state', 'in this state', 'in our state'
]

# Profile location keywords
PROFILE_LOCATION_KEYWORDS = [
    'california', 'new york', 'texas', 'florida', 'washington', 'oregon',
    'seattle', 'los angeles', 'san francisco', 'portland', 'austin', 'denver',
    'chicago', 'boston', 'miami', 'phoenix', 'las vegas', 'san diego',
    'oakland', 'sacramento', 'usa', 'united states', 'america'
]

def get_keyword_categories():
    """Return organized keyword categories for analysis"""
    return {
        'core': CORE_HOMELESSNESS_KEYWORDS,
        'action': ACTION_KEYWORDS,
        'geographic': GEOGRAPHIC_KEYWORDS,
        'policy': POLICY_KEYWORDS,
        'demographic': DEMOGRAPHIC_KEYWORDS,
        'crisis': CRISIS_KEYWORDS,
        'service': SERVICE_KEYWORDS,
        'economic': ECONOMIC_KEYWORDS,
        'research': RESEARCH_KEYWORDS,
        'hashtags': HASHTAG_KEYWORDS,
        'location_indicators': LOCATION_INDICATORS,
        'profile_locations': PROFILE_LOCATION_KEYWORDS
    }

def get_all_keywords():
    """Return all keywords as a single list"""
    return ALL_HOMELESSNESS_KEYWORDS

def get_location_keywords():
    """Return location-related keywords for metadata extraction"""
    return LOCATION_INDICATORS + PROFILE_LOCATION_KEYWORDS

if __name__ == "__main__":
    print(f"Total homelessness keywords: {len(ALL_HOMELESSNESS_KEYWORDS)}")
    print(f"Location keywords: {len(get_location_keywords())}")
    
    categories = get_keyword_categories()
    for category, keywords in categories.items():
        print(f"{category}: {len(keywords)} keywords")
