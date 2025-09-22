"""
Training Manager for AI models training and evaluation
"""

import logging
import json
import os
import numpy as np
from datetime import datetime
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

logger = logging.getLogger(__name__)

class TrainingManager:
    """Manages training of AI models"""
    
    def __init__(self):
        self.training_data_dir = Path("ai_backend/training_data")
        self.models_dir = Path("ai_backend/models")
        self.training_logs_dir = Path("ai_backend/logs/training")
        
        # Create directories if they don't exist
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.training_logs_dir.mkdir(parents=True, exist_ok=True)
        
    def prepare_intent_training_data(self):
        """Prepare training data for intent classification"""
        try:
            # Educational intent training data
            training_data = [
                # Greetings
                ("hello", "greeting"),
                ("hi there", "greeting"),
                ("good morning", "greeting"),
                ("hey", "greeting"),
                ("greetings", "greeting"),
                
                # Goodbyes
                ("goodbye", "goodbye"),
                ("bye", "goodbye"),
                ("see you later", "goodbye"),
                ("farewell", "goodbye"),
                ("take care", "goodbye"),
                
                # Educational queries
                ("explain photosynthesis", "educational_query"),
                ("what is algebra", "educational_query"),
                ("how does gravity work", "educational_query"),
                ("tell me about world war 2", "educational_query"),
                ("define democracy", "educational_query"),
                ("what are prime numbers", "educational_query"),
                ("explain the water cycle", "educational_query"),
                
                # Quiz requests
                ("create a quiz on biology", "quiz_request"),
                ("generate questions about math", "quiz_request"),
                ("make a test on history", "quiz_request"),
                ("quiz me on science", "quiz_request"),
                ("create questions for chemistry", "quiz_request"),
                
                # Explanation requests
                ("can you explain this", "explanation"),
                ("help me understand", "explanation"),
                ("break this down for me", "explanation"),
                ("make it simpler", "explanation"),
                ("clarify this concept", "explanation"),
                
                # Help requests
                ("i need help", "help"),
                ("can you assist me", "help"),
                ("help me with homework", "help"),
                ("i'm stuck", "help"),
                ("support needed", "help"),
                
                # Grading requests
                ("grade my answer", "grading_request"),
                ("evaluate this response", "grading_request"),
                ("score my work", "grading_request"),
                ("assess my assignment", "grading_request"),
                ("check my homework", "grading_request"),
                
                # Lesson planning
                ("create a lesson plan", "lesson_plan"),
                ("plan a class on biology", "lesson_plan"),
                ("design a curriculum", "lesson_plan"),
                ("structure a lesson", "lesson_plan"),
                
                # Homework help
                ("help with homework", "homework_help"),
                ("homework assistance", "homework_help"),
                ("solve this problem", "homework_help"),
                ("homework question", "homework_help"),
                
                # General questions
                ("what is this", "general_question"),
                ("tell me more", "general_question"),
                ("information about", "general_question"),
                ("details on", "general_question"),
                
                # Complaints
                ("this is wrong", "complaint"),
                ("not working properly", "complaint"),
                ("having issues", "complaint"),
                ("problem with system", "complaint"),
                
                # Compliments
                ("great job", "compliment"),
                ("excellent work", "compliment"),
                ("very helpful", "compliment"),
                ("thank you", "compliment"),
                ("amazing", "compliment")
            ]
            
            # Save training data
            training_file = self.training_data_dir / "intent_training_data.json"
            with open(training_file, 'w') as f:
                json.dump(training_data, f, indent=2)
                
            logger.info(f"Prepared {len(training_data)} intent training examples")
            return training_data
            
        except Exception as e:
            logger.error(f"Error preparing intent training data: {str(e)}")
            return []
            
    def prepare_sentiment_training_data(self):
        """Prepare training data for sentiment analysis"""
        try:
            # Educational sentiment training data
            training_data = [
                # Positive sentiments
                ("I love learning about science", "positive"),
                ("This explanation is very clear", "positive"),
                ("Great job on the lesson", "positive"),
                ("I understand it now", "positive"),
                ("Excellent teaching method", "positive"),
                ("Very helpful information", "positive"),
                ("Amazing content", "positive"),
                ("Perfect explanation", "positive"),
                ("I'm excited to learn more", "positive"),
                ("This is interesting", "positive"),
                
                # Negative sentiments
                ("I don't understand this", "negative"),
                ("This is too difficult", "negative"),
                ("Confusing explanation", "negative"),
                ("I'm frustrated", "negative"),
                ("This doesn't make sense", "negative"),
                ("Poor teaching", "negative"),
                ("Waste of time", "negative"),
                ("Boring content", "negative"),
                ("I hate this subject", "negative"),
                ("Terrible explanation", "negative"),
                
                # Neutral sentiments
                ("What is photosynthesis", "neutral"),
                ("Explain the concept", "neutral"),
                ("Define this term", "neutral"),
                ("Show me the formula", "neutral"),
                ("List the steps", "neutral"),
                ("Provide examples", "neutral"),
                ("What are the types", "neutral"),
                ("How does this work", "neutral"),
                ("When did this happen", "neutral"),
                ("Where is this located", "neutral")
            ]
            
            # Save training data
            training_file = self.training_data_dir / "sentiment_training_data.json"
            with open(training_file, 'w') as f:
                json.dump(training_data, f, indent=2)
                
            logger.info(f"Prepared {len(training_data)} sentiment training examples")
            return training_data
            
        except Exception as e:
            logger.error(f"Error preparing sentiment training data: {str(e)}")
            return []
            
    def train_intent_classifier(self, intent_classifier):
        """Train the intent classification model"""
        try:
            logger.info("Starting intent classifier training...")
            
            # Prepare training data
            training_data = self.prepare_intent_training_data()
            if not training_data:
                logger.error("No training data available")
                return False
                
            # Train the model
            success = intent_classifier.train(training_data)
            
            if success:
                # Log training completion
                self._log_training_completion("intent_classifier", len(training_data))
                logger.info("Intent classifier training completed successfully")
                return True
            else:
                logger.error("Intent classifier training failed")
                return False
                
        except Exception as e:
            logger.error(f"Error training intent classifier: {str(e)}")
            return False
            
    def train_sentiment_analyzer(self, sentiment_analyzer):
        """Train the sentiment analysis model"""
        try:
            logger.info("Starting sentiment analyzer training...")
            
            # Prepare training data
            training_data = self.prepare_sentiment_training_data()
            if not training_data:
                logger.error("No training data available")
                return False
                
            # Train the model
            success = sentiment_analyzer.train(training_data)
            
            if success:
                # Log training completion
                self._log_training_completion("sentiment_analyzer", len(training_data))
                logger.info("Sentiment analyzer training completed successfully")
                return True
            else:
                logger.error("Sentiment analyzer training failed")
                return False
                
        except Exception as e:
            logger.error(f"Error training sentiment analyzer: {str(e)}")
            return False
            
    def evaluate_model(self, model, test_data, model_name):
        """Evaluate a trained model"""
        try:
            logger.info(f"Evaluating {model_name}...")
            
            # Prepare test data
            texts = [item[0] for item in test_data]
            true_labels = [item[1] for item in test_data]
            
            # Get predictions
            predictions = []
            for text in texts:
                if model_name == "intent_classifier":
                    result = model.predict(text)
                    predictions.append(result['intent'])
                elif model_name == "sentiment_analyzer":
                    result = model.analyze(text)
                    predictions.append(result['sentiment'])
                    
            # Calculate metrics
            accuracy = accuracy_score(true_labels, predictions)
            report = classification_report(true_labels, predictions, output_dict=True)
            
            # Save evaluation results
            evaluation_results = {
                'model_name': model_name,
                'accuracy': accuracy,
                'classification_report': report,
                'test_samples': len(test_data),
                'evaluated_at': datetime.now().isoformat()
            }
            
            eval_file = self.training_logs_dir / f"{model_name}_evaluation.json"
            with open(eval_file, 'w') as f:
                json.dump(evaluation_results, f, indent=2)
                
            logger.info(f"{model_name} evaluation completed. Accuracy: {accuracy:.3f}")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating {model_name}: {str(e)}")
            return None
            
    def _log_training_completion(self, model_name, training_samples):
        """Log training completion details"""
        try:
            log_entry = {
                'model_name': model_name,
                'training_samples': training_samples,
                'trained_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            log_file = self.training_logs_dir / f"{model_name}_training_log.json"
            
            # Load existing logs
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    
            # Add new log entry
            logs.append(log_entry)
            
            # Save updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging training completion: {str(e)}")
            
    def get_training_history(self, model_name=None):
        """Get training history for models"""
        try:
            if model_name:
                log_file = self.training_logs_dir / f"{model_name}_training_log.json"
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        return json.load(f)
                return []
            else:
                # Get all training histories
                all_histories = {}
                for log_file in self.training_logs_dir.glob("*_training_log.json"):
                    model = log_file.stem.replace("_training_log", "")
                    with open(log_file, 'r') as f:
                        all_histories[model] = json.load(f)
                return all_histories
                
        except Exception as e:
            logger.error(f"Error getting training history: {str(e)}")
            return {} if model_name is None else []
            
    def create_training_dataset(self, data_type, custom_data=None):
        """Create or update training dataset"""
        try:
            if data_type == "intent" and custom_data:
                # Add custom intent data
                existing_data = self.prepare_intent_training_data()
                combined_data = existing_data + custom_data
                
                training_file = self.training_data_dir / "intent_training_data.json"
                with open(training_file, 'w') as f:
                    json.dump(combined_data, f, indent=2)
                    
                logger.info(f"Updated intent training dataset with {len(custom_data)} new examples")
                return True
                
            elif data_type == "sentiment" and custom_data:
                # Add custom sentiment data
                existing_data = self.prepare_sentiment_training_data()
                combined_data = existing_data + custom_data
                
                training_file = self.training_data_dir / "sentiment_training_data.json"
                with open(training_file, 'w') as f:
                    json.dump(combined_data, f, indent=2)
                    
                logger.info(f"Updated sentiment training dataset with {len(custom_data)} new examples")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error creating training dataset: {str(e)}")
            return False
