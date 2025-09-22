"""
Educational Assistant for AI-powered grading and feedback
"""

import logging
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)

class EducationalAssistant:
    """Educational AI assistant for grading and feedback generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.loaded = False
        
        # Grading criteria weights
        self.grading_weights = {
            'semantic_similarity': 0.4,
            'keyword_matching': 0.3,
            'completeness': 0.2,
            'clarity': 0.1
        }
        
    def load_model(self):
        """Load BERT-based model for semantic understanding"""
        try:
            logger.info("Loading educational assistant model...")
            
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.model.to(self.device)
            
            self.loaded = True
            logger.info("Educational assistant model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading educational assistant model: {str(e)}")
            self.loaded = False
            
    def enhance_response(self, user_message, aiml_response, context=None):
        """Enhance AIML response with educational AI capabilities"""
        try:
            if not self.loaded:
                return aiml_response
                
            # Analyze the educational context
            educational_context = self._analyze_educational_context(user_message)
            
            # Generate enhanced response based on context
            if educational_context['type'] == 'question_generation':
                enhanced = self._enhance_question_generation(aiml_response, context)
            elif educational_context['type'] == 'grading_request':
                enhanced = self._enhance_grading_response(aiml_response, context)
            elif educational_context['type'] == 'explanation_request':
                enhanced = self._enhance_explanation(aiml_response, context)
            else:
                enhanced = aiml_response
                
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing response: {str(e)}")
            return aiml_response
            
    def grade_answer(self, question, student_answer, correct_answer, max_score=100):
        """Grade student answer against correct answer"""
        try:
            if not self.loaded:
                return {
                    'score': 0,
                    'feedback': 'Grading model not available',
                    'breakdown': {}
                }
                
            # Clean and preprocess answers
            student_clean = self._preprocess_text(student_answer)
            correct_clean = self._preprocess_text(correct_answer)
            question_clean = self._preprocess_text(question)
            
            # Calculate different scoring components
            semantic_score = self._calculate_semantic_similarity(student_clean, correct_clean)
            keyword_score = self._calculate_keyword_matching(student_clean, correct_clean)
            completeness_score = self._calculate_completeness(student_clean, correct_clean)
            clarity_score = self._calculate_clarity(student_clean)
            
            # Calculate weighted final score
            final_score = (
                semantic_score * self.grading_weights['semantic_similarity'] +
                keyword_score * self.grading_weights['keyword_matching'] +
                completeness_score * self.grading_weights['completeness'] +
                clarity_score * self.grading_weights['clarity']
            ) * max_score
            
            # Generate feedback
            feedback = self._generate_feedback(
                question_clean, student_clean, correct_clean,
                semantic_score, keyword_score, completeness_score, clarity_score
            )
            
            return {
                'score': round(final_score, 2),
                'feedback': feedback,
                'breakdown': {
                    'semantic_similarity': round(semantic_score * 100, 2),
                    'keyword_matching': round(keyword_score * 100, 2),
                    'completeness': round(completeness_score * 100, 2),
                    'clarity': round(clarity_score * 100, 2)
                },
                'max_score': max_score
            }
            
        except Exception as e:
            logger.error(f"Error grading answer: {str(e)}")
            return {
                'score': 0,
                'feedback': f'Error in grading: {str(e)}',
                'breakdown': {}
            }
            
    def _analyze_educational_context(self, message):
        """Analyze the educational context of the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['grade', 'score', 'evaluate', 'assess']):
            return {'type': 'grading_request'}
        elif any(word in message_lower for word in ['generate', 'create', 'make', 'questions']):
            return {'type': 'question_generation'}
        elif any(word in message_lower for word in ['explain', 'how', 'why', 'what']):
            return {'type': 'explanation_request'}
        else:
            return {'type': 'general'}
            
    def _preprocess_text(self, text):
        """Preprocess text for analysis"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()
        
    def _calculate_semantic_similarity(self, student_answer, correct_answer):
        """Calculate semantic similarity using sentence embeddings"""
        try:
            if not student_answer or not correct_answer:
                return 0.0
                
            # Get embeddings
            student_embedding = self.model.encode([student_answer])
            correct_embedding = self.model.encode([correct_answer])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(student_embedding, correct_embedding)[0][0]
            
            # Normalize to 0-1 range
            return max(0, min(1, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {str(e)}")
            return 0.0
            
    def _calculate_keyword_matching(self, student_answer, correct_answer):
        """Calculate keyword matching score"""
        try:
            if not student_answer or not correct_answer:
                return 0.0
                
            # Extract keywords (simple approach - can be enhanced)
            student_words = set(student_answer.split())
            correct_words = set(correct_answer.split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            
            student_keywords = student_words - stop_words
            correct_keywords = correct_words - stop_words
            
            if not correct_keywords:
                return 1.0 if not student_keywords else 0.0
                
            # Calculate overlap
            overlap = len(student_keywords.intersection(correct_keywords))
            total_keywords = len(correct_keywords)
            
            return overlap / total_keywords
            
        except Exception as e:
            logger.error(f"Error calculating keyword matching: {str(e)}")
            return 0.0
            
    def _calculate_completeness(self, student_answer, correct_answer):
        """Calculate completeness score based on answer length and content coverage"""
        try:
            if not student_answer:
                return 0.0
            if not correct_answer:
                return 1.0
                
            # Simple length-based completeness (can be enhanced)
            student_length = len(student_answer.split())
            correct_length = len(correct_answer.split())
            
            if correct_length == 0:
                return 1.0
                
            # Optimal length is around 80-120% of correct answer length
            length_ratio = student_length / correct_length
            
            if 0.8 <= length_ratio <= 1.2:
                return 1.0
            elif length_ratio < 0.8:
                return length_ratio / 0.8
            else:
                return max(0.5, 1.2 / length_ratio)
                
        except Exception as e:
            logger.error(f"Error calculating completeness: {str(e)}")
            return 0.0
            
    def _calculate_clarity(self, student_answer):
        """Calculate clarity score based on grammar and structure"""
        try:
            if not student_answer:
                return 0.0
                
            # Simple clarity metrics
            sentences = student_answer.split('.')
            words = student_answer.split()
            
            if not words:
                return 0.0
                
            # Average sentence length (optimal: 10-20 words)
            avg_sentence_length = len(words) / max(1, len(sentences))
            
            # Clarity score based on sentence length
            if 10 <= avg_sentence_length <= 20:
                clarity = 1.0
            elif avg_sentence_length < 10:
                clarity = avg_sentence_length / 10
            else:
                clarity = max(0.5, 20 / avg_sentence_length)
                
            return clarity
            
        except Exception as e:
            logger.error(f"Error calculating clarity: {str(e)}")
            return 0.0
            
    def _generate_feedback(self, question, student_answer, correct_answer, 
                          semantic_score, keyword_score, completeness_score, clarity_score):
        """Generate detailed feedback for the student"""
        try:
            feedback_parts = []
            
            # Overall assessment
            overall_score = (semantic_score + keyword_score + completeness_score + clarity_score) / 4
            
            if overall_score >= 0.9:
                feedback_parts.append("Excellent answer! You demonstrated a strong understanding of the topic.")
            elif overall_score >= 0.7:
                feedback_parts.append("Good answer! You covered most of the key points.")
            elif overall_score >= 0.5:
                feedback_parts.append("Fair answer. There's room for improvement in several areas.")
            else:
                feedback_parts.append("Your answer needs significant improvement. Please review the topic.")
                
            # Specific feedback based on scores
            if semantic_score < 0.6:
                feedback_parts.append("Consider reviewing the core concepts as your answer doesn't fully align with the expected response.")
                
            if keyword_score < 0.5:
                feedback_parts.append("Try to include more relevant keywords and technical terms in your answer.")
                
            if completeness_score < 0.6:
                feedback_parts.append("Your answer could be more comprehensive. Consider adding more details or examples.")
                
            if clarity_score < 0.6:
                feedback_parts.append("Work on making your answer clearer and more structured.")
                
            # Suggestions for improvement
            feedback_parts.append("For improvement, focus on: understanding key concepts, using appropriate terminology, and providing complete explanations.")
            
            return " ".join(feedback_parts)
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return "Unable to generate detailed feedback at this time."
            
    def _enhance_question_generation(self, response, context):
        """Enhance question generation responses"""
        return f"{response}\n\nTip: Consider varying question types (multiple choice, short answer, essay) for comprehensive assessment."
        
    def _enhance_grading_response(self, response, context):
        """Enhance grading-related responses"""
        return f"{response}\n\nRemember: Fair grading considers content accuracy, completeness, and clarity of expression."
        
    def _enhance_explanation(self, response, context):
        """Enhance explanation responses"""
        return f"{response}\n\nWould you like me to provide examples or break this down further?"
        
    def is_loaded(self):
        """Check if model is loaded"""
        return self.loaded
        
    def get_model_info(self):
        """Get model information"""
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'loaded': self.loaded,
            'grading_weights': self.grading_weights
        }
