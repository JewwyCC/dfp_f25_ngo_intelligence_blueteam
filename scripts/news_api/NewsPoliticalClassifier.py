from transformers import pipeline
from typing import List, Dict


class PoliticalLeaningClassifier:
    def __init__(self):
        """
        Initialize the classifier
        """
        # Main political leaning classifier
        self.leaning_classifier = pipeline(
            "text-classification",
            model="matous-volf/political-leaning-politics",
            tokenizer="launch/POLITICS"
        )

    def classify_single(self, text: str) -> Dict:
        """Classify a single article"""
        # Truncate if too long (model max is ~512 tokens)
        text = text[:2000]  # Rough character limit

        result = {
            'is_political': True,
            'political_confidence': 1.0,
            'leaning': None,
            'leaning_confidence': 0.0
        }

        # Classify political leaning
        leaning_result = self.leaning_classifier(text)[0]

        # Map labels to readable names
        label_map = {
            'LABEL_0': 'LEFT',
            'LABEL_1': 'CENTER',
            'LABEL_2': 'RIGHT'
        }

        result['leaning'] = label_map.get(leaning_result['label'], leaning_result['label'])

        return result

    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Classify multiple articles
        """
        results = []

        for i, article in enumerate(articles):

            # Get the text to classify
            text = article.get('text', '') or article.get('content', '')

            # Classify
            classification = self.classify_single(text)

            # Add classification to article data
            article_with_class = {
                **article,
                **classification
            }

            results.append(article_with_class)

        return results