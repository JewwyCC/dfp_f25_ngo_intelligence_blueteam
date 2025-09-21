#!/usr/bin/env python3
"""
Political Polarization Analyzer for Social Justice Posts

This module analyzes posts for political leanings without affecting the main scraper.
It classifies posts as Left Wing (Democratic), Right Wing (Republican), or Neutral.
"""

import re
import json
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass

@dataclass
class PolarizationResult:
    """Result of political polarization analysis"""
    classification: str  # 'left', 'right', 'neutral'
    confidence: float   # 0.0 to 1.0
    keywords: List[str] # Keywords that influenced the classification
    reasoning: str      # Human-readable explanation

class PoliticalPolarizationAnalyzer:
    """Analyzes social justice posts for political leanings"""
    
    def __init__(self):
        # Left-wing (Democratic) indicators
        self.left_keywords = {
            'economic': [
                'minimum wage', 'living wage', 'universal basic income', 'ubi',
                'wealth inequality', 'income inequality', 'wealth tax', 'progressive tax',
                'corporate greed', 'billionaire', 'millionaire', 'rich getting richer',
                'medicare for all', 'single payer', 'public healthcare', 'affordable healthcare',
                'student debt', 'free college', 'public education', 'education funding',
                'social security', 'safety net', 'welfare', 'unemployment benefits',
                'union', 'workers rights', 'labor rights', 'collective bargaining'
            ],
            'social': [
                'climate change', 'global warming', 'environmental justice', 'green new deal',
                'renewable energy', 'fossil fuels', 'carbon tax', 'climate action',
                'lgbtq+', 'lgbt rights', 'trans rights', 'marriage equality',
                'reproductive rights', 'abortion rights', 'planned parenthood',
                'immigration reform', 'path to citizenship', 'refugee', 'asylum',
                'racial justice', 'systemic racism', 'police reform', 'criminal justice reform',
                'voting rights', 'voter suppression', 'gerrymandering', 'democracy'
            ],
            'language': [
                'systemic', 'institutional', 'privilege', 'equity', 'inclusion',
                'marginalized', 'oppressed', 'intersectional', 'ally', 'solidarity',
                'community organizing', 'grassroots', 'movement', 'protest', 'activism'
            ]
        }
        
        # Right-wing (Republican) indicators
        self.right_keywords = {
            'economic': [
                'free market', 'capitalism', 'free enterprise', 'deregulation',
                'tax cuts', 'tax relief', 'small government', 'limited government',
                'fiscal responsibility', 'balanced budget', 'deficit reduction',
                'private sector', 'entrepreneur', 'job creator', 'business friendly',
                'government waste', 'bureaucracy', 'red tape', 'overregulation',
                'individual responsibility', 'personal responsibility', 'bootstraps'
            ],
            'social': [
                'traditional values', 'family values', 'pro-life', 'sanctity of life',
                'second amendment', 'gun rights', 'constitutional rights', 'founding fathers',
                'law and order', 'back the blue', 'thin blue line', 'police support',
                'border security', 'illegal immigration', 'secure borders', 'enforcement',
                'school choice', 'parental rights', 'local control', 'state rights',
                'religious freedom', 'freedom of religion', 'christian values'
            ],
            'language': [
                'woke', 'cancel culture', 'political correctness', 'mainstream media',
                'fake news', 'establishment', 'elite', 'coastal elite', 'swamp',
                'deep state', 'big tech', 'censorship', 'free speech', 'constitution'
            ]
        }
        
        # Neutral indicators (social justice without clear political lean)
        self.neutral_keywords = [
            'human rights', 'civil rights', 'justice', 'equality', 'fairness',
            'community', 'helping', 'support', 'volunteer', 'charity', 'nonprofit',
            'awareness', 'education', 'understanding', 'dialogue', 'conversation',
            'facts', 'research', 'data', 'study', 'report', 'statistics'
        ]
        
        # Compile regex patterns for better matching
        self.left_patterns = self._compile_patterns(self.left_keywords)
        self.right_patterns = self._compile_patterns(self.right_keywords)
        self.neutral_patterns = self._compile_patterns({'neutral': self.neutral_keywords})
    
    def _compile_patterns(self, keyword_dict: Dict[str, List[str]]) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for keyword matching"""
        patterns = {}
        for category, keywords in keyword_dict.items():
            patterns[category] = []
            for keyword in keywords:
                # Create case-insensitive pattern with word boundaries
                pattern = re.compile(r'\b' + re.escape(keyword.lower()) + r'\b', re.IGNORECASE)
                patterns[category].append(pattern)
        return patterns
    
    def analyze_post(self, post_text: str) -> PolarizationResult:
        """
        Analyze a single post for political polarization
        
        Args:
            post_text: The text content of the post
            
        Returns:
            PolarizationResult with classification, confidence, and reasoning
        """
        if not post_text or len(post_text.strip()) < 10:
            return PolarizationResult('neutral', 0.0, [], 'Post too short for analysis')
        
        text_lower = post_text.lower()
        
        # Count matches for each political leaning
        left_score = self._calculate_score(text_lower, self.left_patterns)
        right_score = self._calculate_score(text_lower, self.right_patterns)
        neutral_score = self._calculate_score(text_lower, self.neutral_patterns)
        
        # Determine classification
        total_score = left_score['total'] + right_score['total'] + neutral_score['total']
        
        if total_score == 0:
            return PolarizationResult('neutral', 0.0, [], 'No political indicators found')
        
        # Calculate confidence based on how dominant the winning score is
        max_score = max(left_score['total'], right_score['total'], neutral_score['total'])
        if max_score == 0:
            confidence = 0.0
        else:
            # Confidence based on how much the winning score dominates
            confidence = min(max_score / total_score)  # Cap at 90% to avoid 100%
        
        # Classify based on highest score
        if left_score['total'] > right_score['total'] and left_score['total'] > neutral_score['total']:
            classification = 'left'
            keywords = left_score['keywords']
            reasoning = f"Left-wing indicators: {', '.join(keywords[:3])}"
        elif right_score['total'] > left_score['total'] and right_score['total'] > neutral_score['total']:
            classification = 'right'
            keywords = right_score['keywords']
            reasoning = f"Right-wing indicators: {', '.join(keywords[:3])}"
        else:
            classification = 'neutral'
            keywords = neutral_score['keywords'] if neutral_score['keywords'] else []
            reasoning = "Balanced or neutral political indicators"
        
        return PolarizationResult(classification, confidence, keywords, reasoning)
    
    def _calculate_score(self, text: str, patterns: Dict[str, List[re.Pattern]]) -> Dict:
        """Calculate political leaning score for a text"""
        total_matches = 0
        matched_keywords = []
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = pattern.findall(text)
                if matches:
                    total_matches += len(matches)
                    # Extract the original keyword from the pattern
                    keyword = pattern.pattern.replace(r'\b', '').replace('\\', '').lower()
                    matched_keywords.append(keyword)
        
        return {
            'total': total_matches,
            'keywords': matched_keywords
        }
    
    def analyze_posts_batch(self, posts: List[Dict]) -> Dict:
        """
        Analyze a batch of posts for political polarization
        
        Args:
            posts: List of post dictionaries with 'text' field
            
        Returns:
            Dictionary with overall statistics and individual results
        """
        results = []
        classifications = Counter()
        confidence_scores = []
        examples = defaultdict(list)
        
        for post in posts:
            if not post.get('text'):
                continue
                
            result = self.analyze_post(post['text'])
            results.append({
                'post_id': post.get('uri', ''),
                'classification': result.classification,
                'confidence': result.confidence,
                'keywords': result.keywords,
                'reasoning': result.reasoning
            })
            
            classifications[result.classification] += 1
            confidence_scores.append(result.confidence)
            
            # Collect examples for each classification (top 10 by confidence for pagination)
            if len(examples[result.classification]) < 10 and result.confidence > 0.3:
                examples[result.classification].append({
                    'text': post['text'][:200] + '...' if len(post['text']) > 200 else post['text'],
                    'confidence': result.confidence,
                    'keywords': result.keywords[:3],
                    'author_handle': post.get('author_handle', ''),
                    'author_display_name': post.get('author_display_name', ''),
                    'author_followers_count': post.get('author_followers_count', 0),
                    'created_at': post.get('created_at', ''),
                    'uri': post.get('uri', '')
                })
        
        # Calculate overall statistics
        total_posts = len(results)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'total_posts_analyzed': total_posts,
            'classifications': dict(classifications),
            'percentages': {
                'left': (classifications['left'] / total_posts * 100) if total_posts > 0 else 0,
                'right': (classifications['right'] / total_posts * 100) if total_posts > 0 else 0,
                'neutral': (classifications['neutral'] / total_posts * 100) if total_posts > 0 else 0
            },
            'average_confidence': avg_confidence,
            'examples': dict(examples),
            'individual_results': results
        }

# Global analyzer instance
polarization_analyzer = PoliticalPolarizationAnalyzer()

def analyze_posts_polarization(posts: List[Dict]) -> Dict:
    """
    Convenience function to analyze posts for political polarization
    
    Args:
        posts: List of post dictionaries
        
    Returns:
        Analysis results dictionary
    """
    return polarization_analyzer.analyze_posts_batch(posts)

if __name__ == "__main__":
    # Test the analyzer with sample posts
    test_posts = [
        {
            'uri': 'test1',
            'text': 'We need to raise the minimum wage to $15/hour to address income inequality and help working families.'
        },
        {
            'uri': 'test2', 
            'text': 'The free market will solve our economic problems if we reduce government regulation and cut taxes.'
        },
        {
            'uri': 'test3',
            'text': 'Everyone deserves access to quality healthcare regardless of their income level.'
        },
        {
            'uri': 'test4',
            'text': 'Climate change is a serious issue that requires immediate action from our government.'
        }
    ]
    
    results = analyze_posts_polarization(test_posts)
    print(json.dumps(results, indent=2))
