"""
Sentiment Analysis Model for Educational AI Assistant
"""

import pickle
import os
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.model_path = "ai_backend/models/sentiment_analyzer.pkl"
        self.loaded = False
        
        # Sentiment categories
        self.sentiments = ['positive', 'negative', 'neutral']
        
    def load_model(self):
        """Load trained sentiment analysis model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            if os.path.exists(self.model_path):
                logger.info("Loading existing sentiment analyzer...")
                self.model = joblib.load(self.model_path)
                self.loaded = True
                logger.info("Sentiment analyzer loaded successfully")
            else:
                logger.info("No existing model found. Training new sentiment analyzer...")
                self._train_default_model()
                
        except Exception as e:
            logger.error(f"Error loading sentiment analyzer: {str(e)}")
            self.loaded = False
            
    def _train_default_model(self):
        """Train a default sentiment analysis model with sample data"""
        try:
            # Sample training data for educational context
            training_data = [
                # Positive sentiments
                ("I love this explanation", "positive"),
                ("This is really helpful", "positive"),
                ("Great job on the quiz", "positive"),
                ("Thank you for the help", "positive"),
                ("Excellent teaching", "positive"),
                ("This makes perfect sense", "positive"),
                ("Amazing work", "positive"),
                ("I understand now", "positive"),
                ("Very clear explanation", "positive"),
                ("Fantastic lesson", "positive"),
                ("I'm excited to learn", "positive"),
                ("This is interesting", "positive"),
                ("Good job", "positive"),
                ("I appreciate this", "positive"),
                ("Well done", "positive"),
                
                # Negative sentiments
                ("I don't understand this", "negative"),
                ("This is confusing", "negative"),
                ("I hate this subject", "negative"),
                ("This is too difficult", "negative"),
                ("I'm frustrated", "negative"),
                ("This doesn't make sense", "negative"),
                ("I'm struggling with this", "negative"),
                ("This is boring", "negative"),
                ("I can't figure this out", "negative"),
                ("This is wrong", "negative"),
                ("I'm lost", "negative"),
                ("This is terrible", "negative"),
                ("I give up", "negative"),
                ("This is useless", "negative"),
                ("I'm confused", "negative"),
                
                # Neutral sentiments
                ("What is photosynthesis", "neutral"),
                ("Explain quantum physics", "neutral"),
                ("Create a quiz on math", "neutral"),
                ("How does this work", "neutral"),
                ("What are the steps", "neutral"),
                ("Can you help me", "neutral"),
                ("I need assistance", "neutral"),
                ("Show me the answer", "neutral"),
                ("What is the definition", "neutral"),
                ("How do I solve this", "neutral"),
                ("What comes next", "neutral"),
                ("Tell me more", "neutral"),
                ("I have a question", "neutral"),
                ("Can you explain", "neutral"),
                ("What does this mean", "neutral"),
            ]
            
            # Prepare training data
            texts = [item[0] for item in training_data]
            labels = [item[1] for item in training_data]
            
            # Create and train pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
                ('classifier', LogisticRegression(random_state=42))
            ])
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Sentiment analyzer trained with accuracy: {accuracy:.3f}")
            
            # Save model
            joblib.dump(self.model, self.model_path)
            self.loaded = True
            
            logger.info("Sentiment analyzer trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Error training sentiment analyzer: {str(e)}")
            raise
            
    def analyze(self, text):
        """Analyze sentiment of given text"""
        try:
            if not self.loaded or self.model is None:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
                
            # Get prediction and probability
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            
            return {
                'sentiment': prediction,
                'confidence': float(confidence),
                'all_probabilities': {
                    sentiment: float(prob) 
                    for sentiment, prob in zip(self.model.classes_, probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'error': str(e)
            }
            
    def train(self, training_data_path=None):
        """Train the sentiment analyzer with new data"""
        try:
            if training_data_path and os.path.exists(training_data_path):
                # Load training data from file
                logger.info(f"Training with data from {training_data_path}")
                # TODO: Implement file loading logic
            else:
                # Use default training data
                self._train_default_model()
                
            return True
            
        except Exception as e:
            logger.error(f"Error training sentiment analyzer: {str(e)}")
            return False
            
    def is_loaded(self):
        """Check if model is loaded"""
        return self.loaded
        
    def get_sentiment_distribution(self, texts):
        """Get sentiment distribution for a list of texts"""
        try:
            if not self.loaded:
                return None
                
            results = []
            for text in texts:
                sentiment_result = self.analyze(text)
                results.append(sentiment_result)
                
            # Calculate overall distribution
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for result in results:
                sentiment_counts[result['sentiment']] += 1
                
            total = len(results)
            distribution = {
                sentiment: count / total 
                for sentiment, count in sentiment_counts.items()
            }
            
            return {
                'individual_results': results,
                'overall_distribution': distribution,
                'total_analyzed': total
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment distribution: {str(e)}")
            return None
