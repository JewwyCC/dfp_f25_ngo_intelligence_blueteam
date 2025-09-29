#!/usr/bin/env python3
"""
Homelessness keywords module for Bluesky data collection
"""

def get_all_keywords():
    """Get all homelessness-related keywords"""
    return [
        'homeless', 'homelessness', 'unhoused', 'housing crisis', 'affordable housing',
        'homeless shelter', 'street homelessness', 'housing first', 'homeless veterans',
        'homeless families', 'homeless youth', 'chronic homelessness', 'temporary housing',
        'transitional housing', 'supportive housing', 'homeless services', 'homeless outreach',
        'homeless encampment', 'housing insecurity', 'homeless population', 'rough sleeper',
        'tent city', 'homeless camp', 'housing assistance', 'homeless prevention',
        'homeless intervention', 'homeless support', 'homeless advocacy', 'homeless rights',
        'homeless policy', 'homeless legislation', 'homeless funding', 'homeless budget',
        'homeless statistics', 'homeless data', 'homeless research', 'homeless study',
        'homeless survey', 'homeless count', 'point in time', 'homeless census',
        'homeless demographics', 'homeless trends', 'homeless patterns', 'homeless causes',
        'homeless solutions', 'homeless programs', 'homeless initiatives', 'homeless projects',
        'homeless campaigns', 'homeless awareness', 'homeless education', 'homeless training',
        'homeless employment', 'homeless job', 'homeless work', 'homeless income',
        'homeless benefits', 'homeless assistance', 'homeless aid', 'homeless help',
        'homeless support', 'homeless care', 'homeless treatment', 'homeless therapy',
        'homeless counseling', 'homeless case management', 'homeless navigation',
        'homeless coordination', 'homeless collaboration', 'homeless partnership',
        'homeless coalition', 'homeless network', 'homeless alliance', 'homeless union',
        'homeless organization', 'homeless nonprofit', 'homeless charity', 'homeless foundation',
        'homeless fund', 'homeless donation', 'homeless volunteer', 'homeless volunteering',
        'homeless activism', 'homeless protest', 'homeless march', 'homeless rally',
        'homeless demonstration', 'homeless advocacy', 'homeless lobbying', 'homeless policy',
        'homeless reform', 'homeless change', 'homeless improvement', 'homeless progress',
        'homeless success', 'homeless story', 'homeless testimonial', 'homeless experience',
        'homeless journey', 'homeless recovery', 'homeless rehabilitation', 'homeless reintegration',
        'homeless reintegration', 'homeless reentry', 'homeless transition', 'homeless pathway',
        'homeless route', 'homeless direction', 'homeless guidance', 'homeless mentorship',
        'homeless coaching', 'homeless training', 'homeless skill', 'homeless development',
        'homeless growth', 'homeless advancement', 'homeless opportunity', 'homeless chance',
        'homeless hope', 'homeless future', 'homeless dream', 'homeless goal',
        'homeless aspiration', 'homeless ambition', 'homeless vision', 'homeless mission',
        'homeless purpose', 'homeless meaning', 'homeless value', 'homeless worth',
        'homeless dignity', 'homeless respect', 'homeless honor', 'homeless pride',
        'homeless identity', 'homeless belonging', 'homeless community', 'homeless family',
        'homeless home', 'homeless place', 'homeless space', 'homeless location',
        'homeless address', 'homeless residence', 'homeless dwelling', 'homeless abode',
        'homeless shelter', 'homeless housing', 'homeless accommodation', 'homeless lodging',
        'homeless residence', 'homeless home', 'homeless place', 'homeless space'
    ]

def get_keyword_categories():
    """Get keywords organized by categories"""
    return {
        'core_terms': [
            'homeless', 'homelessness', 'unhoused', 'housing crisis', 'affordable housing'
        ],
        'housing_types': [
            'homeless shelter', 'temporary housing', 'transitional housing', 'supportive housing',
            'housing assistance', 'housing first', 'affordable housing'
        ],
        'demographics': [
            'homeless veterans', 'homeless families', 'homeless youth', 'chronic homelessness',
            'homeless population', 'homeless demographics'
        ],
        'services': [
            'homeless services', 'homeless outreach', 'homeless prevention', 'homeless intervention',
            'homeless support', 'homeless advocacy', 'homeless assistance', 'homeless aid'
        ],
        'locations': [
            'homeless encampment', 'street homelessness', 'rough sleeper', 'tent city',
            'homeless camp', 'homeless shelter'
        ],
        'geographic': [
            'california', 'los angeles', 'san francisco', 'oakland', 'sacramento', 'san diego',
            'new york', 'manhattan', 'brooklyn', 'queens', 'bronx', 'staten island',
            'chicago', 'seattle', 'portland', 'denver', 'austin', 'houston', 'dallas',
            'miami', 'atlanta', 'boston', 'philadelphia', 'phoenix', 'las vegas',
            'usa', 'america', 'united states', 'canada', 'uk', 'australia'
        ],
        'profile_locations': [
            'california', 'ca', 'cali', 'los angeles', 'la', 'san francisco', 'sf',
            'oakland', 'sacramento', 'san diego', 'new york', 'ny', 'manhattan',
            'brooklyn', 'queens', 'bronx', 'chicago', 'seattle', 'portland', 'denver',
            'austin', 'houston', 'dallas', 'miami', 'atlanta', 'boston', 'philadelphia',
            'phoenix', 'las vegas', 'usa', 'america', 'united states'
        ],
        'policy_terms': [
            'homeless policy', 'homeless legislation', 'homeless funding', 'homeless budget',
            'homeless reform', 'homeless change', 'homeless improvement'
        ],
        'research_terms': [
            'homeless statistics', 'homeless data', 'homeless research', 'homeless study',
            'homeless survey', 'homeless count', 'point in time', 'homeless census'
        ]
    }
