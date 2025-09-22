"""
Intent Classification Model for Educational AI Assistant
"""

import pickle
import os
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.model = None
        self.model_path = "ai_backend/models/intent_classifier.pkl"
        self.loaded = False
        
        # Define intent categories for educational assistant
        self.intents = [
            'greeting',
            'goodbye',
            'educational_query',
            'quiz_request',
            'explanation',
            'help',
            'grading_request',
            'lesson_plan',
            'homework_help',
            'general_question',
            'complaint',
            'compliment'
        ]
        
    def load_model(self):
        """Load trained intent classification model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            if os.path.exists(self.model_path):
                logger.info("Loading existing intent classifier...")
                self.model = joblib.load(self.model_path)
                self.loaded = True
                logger.info("Intent classifier loaded successfully")
            else:
                logger.info("No existing model found. Training new intent classifier...")
                self._train_default_model()
                
        except Exception as e:
            logger.error(f"Error loading intent classifier: {str(e)}")
            self.loaded = False
            
    def _train_default_model(self):
        """Train a default intent classification model with sample data"""
        try:
            # Sample training data for educational context
            training_data = [
                # Greetings
                ("hello", "greeting"),
                ("hi", "greeting"),
                ("good morning", "greeting"),
                ("hey there", "greeting"),
                ("greetings", "greeting"),
                
                # Goodbyes
                ("goodbye", "goodbye"),
                ("bye", "goodbye"),
                ("see you later", "goodbye"),
                ("farewell", "goodbye"),
                
                # Educational queries
                ("what is photosynthesis", "educational_query"),
                ("explain quantum physics", "educational_query"),
                ("how does mitosis work", "educational_query"),
                ("tell me about world war 2", "educational_query"),
                ("what are prime numbers", "educational_query"),
                
                # Quiz requests
                ("create a quiz on biology", "quiz_request"),
                ("generate questions about math", "quiz_request"),
                ("make a test on history", "quiz_request"),
                ("quiz me on chemistry", "quiz_request"),
                
                # Explanations
                ("explain this concept", "explanation"),
                ("help me understand", "explanation"),
                ("can you clarify", "explanation"),
                ("break this down for me", "explanation"),
                
                # Help requests
                ("help", "help"),
                ("i need assistance", "help"),
                ("can you help me", "help"),
                ("what can you do", "help"),
                
                # Grading requests
                ("grade this assignment", "grading_request"),
                ("evaluate my answers", "grading_request"),
                ("check my work", "grading_request"),
                ("score my test", "grading_request"),
                
                # Lesson planning
                ("create a lesson plan", "lesson_plan"),
                ("help me plan a class", "lesson_plan"),
                ("design a curriculum", "lesson_plan"),
                
                # Homework help
                ("help with homework", "homework_help"),
                ("assist with assignment", "homework_help"),
                ("homework question", "homework_help"),
                
                # General questions
                ("how are you", "general_question"),
                ("what is your name", "general_question"),
                ("who made you", "general_question"),
                
                # Complaints
                ("this is wrong", "complaint"),
                ("you made an error", "complaint"),
                ("this doesn't work", "complaint"),
                
                # Compliments
                ("great job", "compliment"),
                ("thank you", "compliment"),
                ("excellent work", "compliment"),
            ]
            
            # Prepare training data
            texts = [item[0] for item in training_data]
            labels = [item[1] for item in training_data]
            
            # Create and train pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
                ('classifier', MultinomialNB(alpha=0.1))
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
            
            logger.info(f"Intent classifier trained with accuracy: {accuracy:.3f}")
            
            # Save model
            joblib.dump(self.model, self.model_path)
            self.loaded = True
            
            logger.info("Intent classifier trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Error training intent classifier: {str(e)}")
            raise
            
    def predict(self, text):
        """Predict intent for given text"""
        try:
            if not self.loaded or self.model is None:
                return {
                    'intent': 'general_question',
                    'confidence': 0.0,
                    'error': 'Model not loaded'
                }
                
            # Get prediction and probability
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            
            return {
                'intent': prediction,
                'confidence': float(confidence),
                'all_probabilities': {
                    intent: float(prob) 
                    for intent, prob in zip(self.model.classes_, probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting intent: {str(e)}")
            return {
                'intent': 'general_question',
                'confidence': 0.0,
                'error': str(e)
            }
            
    def train(self, training_data_path=None):
        """Train the intent classifier with new data"""
        try:
            if training_data_path and os.path.exists(training_data_path):
                # Load training data from file
                # Implementation depends on file format (CSV, JSON, etc.)
                logger.info(f"Training with data from {training_data_path}")
                # TODO: Implement file loading logic
            else:
                # Use default training data
                self._train_default_model()
                
            return True
            
        except Exception as e:
            logger.error(f"Error training intent classifier: {str(e)}")
            return False
            
    def is_loaded(self):
        """Check if model is loaded"""
        return self.loaded
        
    def get_supported_intents(self):
        """Get list of supported intents"""
        return self.intents
