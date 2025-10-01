import re
from collections import Counter, defaultdict
from textblob import TextBlob
from typing import List, Dict, Tuple
import numpy as np


# Topic-specific keyword lists for targeted sentiment analysis
TOPIC_KEYWORDS = {
    'housing_crisis': {
        'positive': [
            'affordable', 'affordable_housing', 'stable', 'security', 'home', 'homeownership',
            'community', 'neighborhood', 'safe', 'comfortable', 'decent', 'quality', 'dignity',
            'support', 'help', 'assistance', 'program', 'initiative', 'solution', 'progress',
            'improvement', 'reform', 'policy', 'investment', 'funding', 'subsidy', 'voucher',
            'success', 'achievement', 'victory', 'win', 'breakthrough', 'hope', 'hopeful',
            'optimistic', 'positive', 'good', 'great', 'excellent', 'amazing', 'wonderful',
            'fantastic', 'love', 'loved', 'happy', 'happiness', 'grateful', 'gratitude',
            'relief', 'joy', 'joyful', 'celebration', 'proud', 'pride', 'accomplishment'
        ],
        'negative': [
            'homeless', 'homelessness', 'eviction', 'evicted', 'displacement', 'crisis',
            'emergency', 'urgent', 'desperate', 'desperation', 'struggle', 'struggling',
            'poverty', 'poor', 'destitute', 'vulnerable', 'at_risk', 'unstable', 'precarious',
            'insecure', 'unsafe', 'dangerous', 'unsanitary', 'overcrowded', 'squalid',
            'deplorable', 'inhumane', 'unacceptable', 'outrage', 'outrageous', 'scandal',
            'injustice', 'unfair', 'discrimination', 'exploitation', 'abuse', 'neglect',
            'abandoned', 'forgotten', 'ignored', 'neglected', 'failed', 'failure', 'broken',
            'anger', 'angry', 'frustrated', 'frustration', 'furious', 'rage', 'outraged',
            'sad', 'sadness', 'depressed', 'depression', 'hopeless', 'despair', 'grief',
            'pain', 'suffering', 'trauma', 'traumatic', 'devastating', 'heartbreaking',
            'terrible', 'awful', 'horrible', 'disgusting', 'appalling', 'shocking',
            'hate', 'hated', 'hateful', 'disgusted', 'disappointed', 'disappointment',
            'fear', 'afraid', 'worried', 'anxious', 'terrified', 'scared', 'panic',
            'stress', 'stressed', 'overwhelmed', 'exhausted', 'burned_out', 'crisis'
        ]
    },
    'tenant_rights': {
        'positive': [
            'rights', 'protection', 'legal', 'law', 'legislation', 'regulation', 'enforcement',
            'fair', 'just', 'justice', 'equity', 'equality', 'dignity', 'respect', 'respectful',
            'professional', 'responsive', 'communication', 'transparency', 'honest', 'honesty',
            'integrity', 'ethical', 'moral', 'principled', 'reasonable', 'flexible', 'understanding',
            'compassionate', 'empathetic', 'caring', 'supportive', 'helpful', 'cooperative',
            'collaborative', 'partnership', 'mutual', 'beneficial', 'win_win', 'solution',
            'resolution', 'agreement', 'compromise', 'negotiation', 'mediation', 'arbitration',
            'success', 'successful', 'achievement', 'victory', 'win', 'progress', 'improvement',
            'reform', 'change', 'positive', 'good', 'great', 'excellent', 'satisfied',
            'content', 'happy', 'pleased', 'grateful', 'thankful', 'appreciative'
        ],
        'negative': [
            'violation', 'violated', 'abuse', 'abused', 'exploitation', 'exploited', 'oppression',
            'oppressed', 'discrimination', 'discriminatory', 'unfair', 'unjust', 'injustice',
            'illegal', 'unlawful', 'wrongful', 'harassment', 'harassed', 'intimidation',
            'intimidated', 'threat', 'threatened', 'retaliation', 'retaliatory', 'revenge',
            'punishment', 'punitive', 'harsh', 'cruel', 'inhumane', 'unethical', 'immoral',
            'corrupt', 'fraud', 'fraudulent', 'deception', 'deceptive', 'misleading',
            'false', 'lies', 'lying', 'dishonest', 'untrustworthy', 'unreliable', 'neglect',
            'neglected', 'abandoned', 'ignored', 'dismissed', 'disregarded', 'disrespect',
            'disrespectful', 'rude', 'hostile', 'aggressive', 'confrontational', 'argumentative',
            'unreasonable', 'inflexible', 'rigid', 'stubborn', 'uncooperative', 'unresponsive',
            'incompetent', 'inept', 'unprofessional', 'inappropriate', 'unacceptable',
            'outrage', 'outrageous', 'scandal', 'scandalous', 'disgrace', 'disgraceful',
            'anger', 'angry', 'furious', 'rage', 'outraged', 'frustrated', 'frustration',
            'sad', 'sadness', 'depressed', 'depression', 'hopeless', 'despair', 'grief',
            'pain', 'suffering', 'trauma', 'traumatic', 'devastating', 'heartbreaking',
            'terrible', 'awful', 'horrible', 'disgusting', 'appalling', 'shocking',
            'hate', 'hated', 'hateful', 'disgusted', 'disappointed', 'disappointment',
            'fear', 'afraid', 'worried', 'anxious', 'terrified', 'scared', 'panic',
            'stress', 'stressed', 'overwhelmed', 'exhausted', 'burned_out'
        ]
    },
    'landlord_tenant_relations': {
        'positive': [
            'professional', 'responsive', 'communication', 'transparent', 'honest', 'integrity',
            'ethical', 'moral', 'principled', 'reasonable', 'flexible', 'understanding',
            'compassionate', 'empathetic', 'caring', 'supportive', 'helpful', 'cooperative',
            'collaborative', 'partnership', 'mutual', 'respect', 'respectful', 'dignity',
            'fair', 'just', 'justice', 'equity', 'equality', 'rights', 'protection',
            'maintenance', 'repair', 'fixed', 'improved', 'upgraded', 'modern', 'clean',
            'safe', 'secure', 'stable', 'reliable', 'trustworthy', 'dependable', 'consistent',
            'timely', 'prompt', 'efficient', 'effective', 'successful', 'satisfied',
            'content', 'happy', 'pleased', 'grateful', 'thankful', 'appreciative',
            'positive', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'
        ],
        'negative': [
            'unresponsive', 'ignored', 'dismissed', 'disregarded', 'neglect', 'neglected',
            'abandoned', 'abandonment', 'incompetent', 'inept', 'unprofessional', 'inappropriate',
            'unacceptable', 'unreasonable', 'inflexible', 'rigid', 'stubborn', 'uncooperative',
            'hostile', 'aggressive', 'confrontational', 'argumentative', 'rude', 'disrespectful',
            'disrespect', 'harassment', 'harassed', 'intimidation', 'intimidated', 'threat',
            'threatened', 'retaliation', 'retaliatory', 'punishment', 'punitive', 'harsh',
            'cruel', 'inhumane', 'unethical', 'immoral', 'corrupt', 'fraud', 'fraudulent',
            'deception', 'deceptive', 'misleading', 'false', 'lies', 'lying', 'dishonest',
            'untrustworthy', 'unreliable', 'violation', 'violated', 'abuse', 'abused',
            'exploitation', 'exploited', 'oppression', 'oppressed', 'discrimination',
            'discriminatory', 'unfair', 'unjust', 'injustice', 'illegal', 'unlawful',
            'wrongful', 'outrage', 'outrageous', 'scandal', 'scandalous', 'disgrace',
            'disgraceful', 'anger', 'angry', 'furious', 'rage', 'outraged', 'frustrated',
            'frustration', 'sad', 'sadness', 'depressed', 'depression', 'hopeless', 'despair',
            'grief', 'pain', 'suffering', 'trauma', 'traumatic', 'devastating', 'heartbreaking',
            'terrible', 'awful', 'horrible', 'disgusting', 'appalling', 'shocking',
            'hate', 'hated', 'hateful', 'disgusted', 'disappointed', 'disappointment',
            'fear', 'afraid', 'worried', 'anxious', 'terrified', 'scared', 'panic',
            'stress', 'stressed', 'overwhelmed', 'exhausted', 'burned_out'
        ]
    }
}

# Legacy emotion words for backward compatibility
EMOTION_WORDS = {
    # Positive
    'hope', 'hopeful', 'joy', 'joyful', 'relief', 'grateful', 'gratitude', 'support', 'helpful', 'uplift',
    'positive', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'loved', 'happy',
    'happiness', 'success', 'successful', 'achieve', 'achievement', 'progress', 'improve', 'better', 'best',
    # Negative
    'anger', 'angry', 'frustrated', 'frustration', 'sad', 'sadness', 'fear', 'afraid', 'worried', 'anxious',
    'desperate', 'desperation', 'pain', 'suffering', 'cry', 'outrage', 'shame', 'guilt', 'negative', 'bad',
    'terrible', 'awful', 'horrible', 'hate', 'hated', 'hateful', 'disgusting', 'disgusted', 'disappointed',
    'disappointment', 'failure', 'failed', 'problem', 'problems', 'issue', 'issues', 'concern', 'concerns',
    'worry', 'worries', 'stress', 'stressed', 'overwhelmed', 'depressed', 'depression'
}


def get_stop_words():
    """Get comprehensive list of stop words and filler words to filter out."""
    return {
        # Basic stop words
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'when', 'where',
        'why', 'how', 'who', 'which', 'there', 'here', 'can', 'may', 'must', 'might',
        'shall', 'just', 'now', 'then', 'very', 'also', 'only', 'even', 'still',
        'already', 'yet', 'really', 'quite', 'rather', 'pretty', 'too', 'so', 'such',
        # Additional common words that should be filtered
        'not', 'out', 'from', 'any', 'all', 'about', 'don', 'some', 'because', 'one',
        'after', 'another', 'new', 'over', 'people', 'since', 'more', 'most', 'much',
        'many', 'other', 'others', 'first', 'last', 'next', 'back', 'up', 'down',
        'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which',
        'each', 'every', 'both', 'either', 'neither', 'none', 'nothing', 'something',
        'anything', 'everything', 'someone', 'anyone', 'everyone', 'nobody',
        'somewhere', 'anywhere', 'everywhere', 'nowhere', 'somehow', 'anyhow',
        'somewhat', 'anyway', 'anyways', 'somewhere', 'anywhere', 'everywhere',
        # Filler words and discourse markers
        'like', 'um', 'uh', 'ah', 'oh', 'well', 'okay', 'ok', 'yeah', 'yes', 'no',
        'sure', 'right', 'exactly', 'basically', 'literally', 'actually', 'honestly',
        'seriously', 'obviously', 'clearly', 'definitely', 'probably', 'maybe', 'perhaps',
        'sort', 'kind', 'somewhat', 'somehow', 'anyway', 'anyways', 'though', 'although',
        'however', 'therefore', 'moreover', 'furthermore', 'meanwhile', 'otherwise',
        'instead', 'rather', 'either', 'neither', 'both',
        # Pronouns and indefinite words
        'someone', 'something', 'somewhere', 'anyone', 'anything', 'anywhere',
        'everyone', 'everything', 'everywhere', 'nobody', 'nothing', 'nowhere',
        # Generic nouns
        'thing', 'things', 'stuff', 'way', 'ways', 'time', 'times', 'day', 'days',
        'year', 'years', 'month', 'months', 'week', 'weeks', 'hour', 'hours',
        'minute', 'minutes', 'second', 'seconds', 'moment', 'moments',
        # Common verbs that don't carry sentiment
        'get', 'got', 'getting', 'go', 'goes', 'going', 'went', 'gone', 'come', 'comes',
        'coming', 'came', 'see', 'sees', 'seeing', 'saw', 'seen', 'look', 'looks',
        'looking', 'looked', 'seem', 'seems', 'seeming', 'seemed', 'appear', 'appears',
        'appearing', 'appeared', 'become', 'becomes', 'becoming', 'became', 'make',
        'makes', 'making', 'made', 'take', 'takes', 'taking', 'took', 'taken',
        'give', 'gives', 'giving', 'gave', 'given', 'put', 'puts', 'putting',
        'use', 'uses', 'using', 'used', 'work', 'works', 'working', 'worked',
        'try', 'tries', 'trying', 'tried', 'want', 'wants', 'wanting', 'wanted',
        'need', 'needs', 'needing', 'needed', 'feel', 'feels', 'feeling', 'felt',
        'think', 'thinks', 'thinking', 'thought', 'know', 'knows', 'knowing', 'knew',
        'known', 'say', 'says', 'saying', 'said', 'tell', 'tells', 'telling', 'told',
        'ask', 'asks', 'asking', 'asked', 'find', 'finds', 'finding', 'found',
        'turn', 'turns', 'turning', 'turned', 'move', 'moves', 'moving', 'moved',
        'play', 'plays', 'playing', 'played', 'run', 'runs', 'running', 'ran',
        'walk', 'walks', 'walking', 'walked', 'sit', 'sits', 'sitting', 'sat',
        'stand', 'stands', 'standing', 'stood', 'live', 'lives', 'living', 'lived',
        'die', 'dies', 'dying', 'died', 'dead', 'death', 'born', 'birth'
    }


def extract_keywords(text: str, min_length: int = 4):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    stop_words = get_stop_words()
    filtered = [w for w in words if len(w) >= min_length and w not in stop_words]
    return Counter(filtered).most_common()


def expand_keywords_with_variants(keywords: List[str]) -> List[str]:
    variants = set()
    for kw in keywords:
        kw_l = kw.lower()
        variants.add(kw_l)
        # naive plural/suffix variants
        if kw_l.endswith('y'):
            variants.add(kw_l[:-1] + 'ies')
        variants.add(kw_l + 's')
        variants.add(kw_l.replace(' ', ''))
        variants.add(kw_l.replace('-', ' '))
    # include emotion words
    variants.update(EMOTION_WORDS)
    return list(variants)


def compute_post_sentiment(text: str) -> float:
    blob = TextBlob(text)
    return float(blob.sentiment.polarity)


def extract_important_terms(text: str, focus_terms: List[str]) -> List[str]:
    text_l = text.lower()
    hits = []
    for term in focus_terms:
        if term in text_l:
            hits.append(term)
    return hits


def compute_topic_keyword_sentiment_scores(text: str, topic: str = 'housing_crisis') -> Dict[str, float]:
    """
    Compute sentiment scores for topic-specific keywords based on their context.
    Returns a dictionary mapping keywords to their sentiment scores (-1 to +1).
    """
    text_lower = text.lower()
    words = re.findall(r"\b[a-zA-Z]+\b", text_lower)
    
    # Get topic-specific keywords
    topic_keywords = TOPIC_KEYWORDS.get(topic, TOPIC_KEYWORDS['housing_crisis'])
    positive_keywords = set(topic_keywords['positive'])
    negative_keywords = set(topic_keywords['negative'])
    
    # Negation words that flip sentiment
    negation_words = {'not', 'no', 'never', 'none', 'nothing', 'nowhere', 'nobody', 'neither', 'nor', 'without', 'lack', 'lacking', 'unable', 'cannot', 'can\'t', 'won\'t', 'don\'t', 'doesn\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t'}
    
    keyword_scores = {}
    
    # Analyze each word in context
    for i, word in enumerate(words):
        if len(word) < 3:  # Skip very short words
            continue
            
        # Only analyze topic-relevant keywords
        if word not in positive_keywords and word not in negative_keywords:
            continue
            
        # Get context window (5 words before and after for better context)
        start_idx = max(0, i - 5)
        end_idx = min(len(words), i + 6)
        context_words = words[start_idx:end_idx]
        
        # Check for negation in context
        has_negation = any(neg_word in context_words for neg_word in negation_words)
        
        # Calculate context sentiment from surrounding words
        context_text = ' '.join(context_words)
        context_sentiment = 0.0
        if context_text.strip():
            context_sentiment = float(TextBlob(context_text).sentiment.polarity)
        
        # Count positive and negative emotion words in context
        positive_count = sum(1 for w in context_words if w in positive_keywords)
        negative_count = sum(1 for w in context_words if w in negative_keywords)
        
        # Base sentiment from keyword type
        if word in positive_keywords:
            base_sentiment = 0.3  # Positive bias
        elif word in negative_keywords:
            base_sentiment = -0.3  # Negative bias
        else:
            base_sentiment = 0.0
        
        # Apply negation (flip sentiment if negation is present)
        if has_negation:
            base_sentiment = -base_sentiment
            context_sentiment = -context_sentiment
            positive_count, negative_count = negative_count, positive_count
        
        # Calculate emotion weight
        emotion_weight = (positive_count - negative_count) / max(1, len(context_words))
        
        # Combine factors with better weighting
        # 40% context sentiment, 30% emotion words, 30% base sentiment
        final_score = (0.4 * context_sentiment + 0.3 * emotion_weight + 0.3 * base_sentiment)
        
        # Normalize to -1 to +1 range
        final_score = max(-1.0, min(1.0, final_score))
        
        keyword_scores[word] = final_score
    
    return keyword_scores


def compute_keyword_sentiment_scores(text: str) -> Dict[str, float]:
    """
    Legacy function for backward compatibility.
    Compute sentiment scores for keywords based on their context.
    Returns a dictionary mapping keywords to their sentiment scores (-1 to +1).
    """
    return compute_topic_keyword_sentiment_scores(text, 'housing_crisis')


def aggregate_topic_keyword_sentiments(df, topic: str = 'housing_crisis') -> Dict[str, float]:
    """
    Aggregate sentiment scores for topic-specific keywords across the dataset.
    Returns z-score normalized average sentiment scores for each keyword.
    """
    keyword_sentiment_sums = defaultdict(float)
    keyword_counts = defaultdict(int)
    
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} {row.get('selftext', '')}"
        keyword_scores = compute_topic_keyword_sentiment_scores(text, topic)
        
        for keyword, score in keyword_scores.items():
            keyword_sentiment_sums[keyword] += score
            keyword_counts[keyword] += 1
    
    # Calculate average sentiment for each keyword
    keyword_averages = {}
    for keyword in keyword_sentiment_sums:
        if keyword_counts[keyword] > 0:
            keyword_averages[keyword] = keyword_sentiment_sums[keyword] / keyword_counts[keyword]
    
    # Z-score normalization to ensure range from -1 to +1
    if keyword_averages:
        values = list(keyword_averages.values())
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val > 0:
            # Normalize to z-scores, then scale to [-1, 1] range
            normalized = {}
            for keyword, avg_sentiment in keyword_averages.items():
                z_score = (avg_sentiment - mean_val) / std_val
                # Scale z-score to [-1, 1] range (clamp extreme values)
                normalized_score = max(-1.0, min(1.0, z_score / 3.0))  # Divide by 3 to reduce extreme values
                normalized[keyword] = normalized_score
            return normalized
    
    return keyword_averages


def aggregate_keyword_sentiments(df) -> Dict[str, float]:
    """
    Legacy function for backward compatibility.
    Aggregate sentiment scores for all keywords across the dataset.
    Returns z-score normalized average sentiment scores for each keyword.
    """
    return aggregate_topic_keyword_sentiments(df, 'housing_crisis')


def get_top_topic_keywords_by_frequency(df, topic: str = 'housing_crisis', top_n: int = 50) -> List[Tuple[str, int, float]]:
    """
    Get top topic-specific keywords by frequency with their z-score normalized sentiment scores.
    Returns list of (keyword, frequency, normalized_sentiment) tuples.
    """
    keyword_sentiment_sums = defaultdict(float)
    keyword_counts = defaultdict(int)
    
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} {row.get('selftext', '')}"
        keyword_scores = compute_topic_keyword_sentiment_scores(text, topic)
        
        for keyword, score in keyword_scores.items():
            keyword_sentiment_sums[keyword] += score
            keyword_counts[keyword] += 1
    
    # Calculate average sentiment for each keyword
    keyword_averages = {}
    for keyword in keyword_sentiment_sums:
        if keyword_counts[keyword] >= 2:  # Only include keywords that appear at least twice
            keyword_averages[keyword] = keyword_sentiment_sums[keyword] / keyword_counts[keyword]
    
    # Z-score normalization
    if keyword_averages:
        values = list(keyword_averages.values())
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val > 0:
            # Normalize to z-scores, then scale to [-1, 1] range
            normalized_sentiments = {}
            for keyword, avg_sentiment in keyword_averages.items():
                z_score = (avg_sentiment - mean_val) / std_val
                # Scale z-score to [-1, 1] range (clamp extreme values)
                normalized_score = max(-1.0, min(1.0, z_score / 3.0))  # Divide by 3 to reduce extreme values
                normalized_sentiments[keyword] = normalized_score
        else:
            normalized_sentiments = keyword_averages
    else:
        normalized_sentiments = {}
    
    # Combine frequency and normalized sentiment data
    keyword_data = []
    for keyword in keyword_counts:
        if keyword_counts[keyword] >= 2:  # Only include keywords that appear at least twice
            normalized_sentiment = normalized_sentiments.get(keyword, 0.0)
            keyword_data.append((
                keyword, 
                keyword_counts[keyword], 
                normalized_sentiment
            ))
    
    # Sort by frequency (descending)
    keyword_data.sort(key=lambda x: x[1], reverse=True)
    return keyword_data[:top_n]


def get_top_keywords_by_frequency(df, top_n: int = 50) -> List[Tuple[str, int, float]]:
    """
    Legacy function for backward compatibility.
    Get top keywords by frequency with their z-score normalized sentiment scores.
    Returns list of (keyword, frequency, normalized_sentiment) tuples.
    """
    return get_top_topic_keywords_by_frequency(df, 'housing_crisis', top_n)


def compute_term_sentiment(df, terms: List[str]) -> Dict[str, float]:
    """Mean sentiment per term based on posts where the term appears."""
    term_to_values: Dict[str, List[float]] = {t: [] for t in terms}
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} {row.get('selftext', '')}".lower()
        sent = float(row.get('sentiment_polarity', 0.0))
        for t in terms:
            if t in text:
                term_to_values[t].append(sent)
    term_to_mean: Dict[str, float] = {}
    for t, vals in term_to_values.items():
        if vals:
            term_to_mean[t] = sum(vals) / len(vals)
    return term_to_mean



