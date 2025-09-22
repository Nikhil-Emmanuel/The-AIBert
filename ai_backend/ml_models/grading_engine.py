"""
Advanced Grading Engine using BERT/SBERT for semantic understanding
Implements sophisticated answer evaluation and scoring
"""

import logging
import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import joblib

logger = logging.getLogger(__name__)

class AdvancedGradingEngine:
    """Advanced grading engine using transformer models"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Model configurations
        self.sentence_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.bert_model_name = "bert-base-uncased"
        self.qa_model_name = "deepset/roberta-base-squad2"
        
        # Models
        self.sentence_transformer = None
        self.bert_model = None
        self.bert_tokenizer = None
        self.qa_pipeline = None
        
        self.loaded = False
        
        # Grading criteria and weights
        self.grading_criteria = {
            'semantic_similarity': {
                'weight': 0.35,
                'description': 'How semantically similar the answer is to the correct answer'
            },
            'factual_accuracy': {
                'weight': 0.25,
                'description': 'Whether the answer contains correct facts and information'
            },
            'completeness': {
                'weight': 0.20,
                'description': 'How complete the answer is compared to the expected response'
            },
            'relevance': {
                'weight': 0.10,
                'description': 'How relevant the answer is to the question asked'
            },
            'clarity_coherence': {
                'weight': 0.10,
                'description': 'How clear and coherent the answer is structured'
            }
        }
        
    def load_models(self):
        """Load all grading models"""
        try:
            logger.info("Loading advanced grading models...")
            
            # Load sentence transformer for semantic similarity
            self.sentence_transformer = SentenceTransformer(self.sentence_model_name)
            self.sentence_transformer.to(self.device)
            
            # Load BERT for deeper analysis
            self.bert_tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
            self.bert_model = AutoModel.from_pretrained(self.bert_model_name)
            self.bert_model.to(self.device)
            self.bert_model.eval()
            
            # Load QA pipeline for factual checking
            self.qa_pipeline = pipeline(
                "question-answering",
                model=self.qa_model_name,
                tokenizer=self.qa_model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.loaded = True
            logger.info("Advanced grading models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading grading models: {str(e)}")
            self.loaded = False
            
    def grade_answer(self, question: str, student_answer: str, correct_answer: str, 
                    rubric: Dict[str, Any] = None, max_score: float = 100.0) -> Dict[str, Any]:
        """Grade student answer using advanced NLP techniques"""
        try:
            if not self.loaded:
                return {
                    'error': 'Grading models not loaded',
                    'score': 0.0,
                    'breakdown': {}
                }
                
            # Preprocess inputs
            question_clean = self._preprocess_text(question)
            student_clean = self._preprocess_text(student_answer)
            correct_clean = self._preprocess_text(correct_answer)
            
            # Calculate individual scores
            scores = {}
            
            # 1. Semantic Similarity
            scores['semantic_similarity'] = self._calculate_semantic_similarity(
                student_clean, correct_clean
            )
            
            # 2. Factual Accuracy
            scores['factual_accuracy'] = self._calculate_factual_accuracy(
                question_clean, student_clean, correct_clean
            )
            
            # 3. Completeness
            scores['completeness'] = self._calculate_completeness(
                student_clean, correct_clean
            )
            
            # 4. Relevance
            scores['relevance'] = self._calculate_relevance(
                question_clean, student_clean
            )
            
            # 5. Clarity and Coherence
            scores['clarity_coherence'] = self._calculate_clarity_coherence(
                student_clean
            )
            
            # Calculate weighted final score
            final_score = self._calculate_weighted_score(scores, max_score)
            
            # Generate detailed feedback
            feedback = self._generate_detailed_feedback(
                question_clean, student_clean, correct_clean, scores
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scores)
            
            return {
                'final_score': round(final_score, 2),
                'max_score': max_score,
                'percentage': round((final_score / max_score) * 100, 2),
                'breakdown': {
                    criterion: {
                        'score': round(score * 100, 2),
                        'weight': self.grading_criteria[criterion]['weight'],
                        'weighted_score': round(score * self.grading_criteria[criterion]['weight'] * max_score, 2)
                    }
                    for criterion, score in scores.items()
                },
                'feedback': feedback,
                'recommendations': recommendations,
                'graded_at': datetime.now().isoformat(),
                'grading_method': 'advanced_nlp'
            }
            
        except Exception as e:
            logger.error(f"Error grading answer: {str(e)}")
            return {
                'error': str(e),
                'score': 0.0,
                'breakdown': {}
            }
            
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\?\!\:\;\-]', '', text)
        
        return text.strip()
        
    def _calculate_semantic_similarity(self, student_answer: str, correct_answer: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        try:
            if not student_answer or not correct_answer:
                return 0.0
                
            # Get embeddings
            embeddings = self.sentence_transformer.encode([student_answer, correct_answer])
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Normalize to 0-1 range
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {str(e)}")
            return 0.0
            
    def _calculate_factual_accuracy(self, question: str, student_answer: str, correct_answer: str) -> float:
        """Calculate factual accuracy using QA model"""
        try:
            if not student_answer or not correct_answer:
                return 0.0
                
            # Extract key facts from correct answer
            key_facts = self._extract_key_facts(correct_answer)
            
            if not key_facts:
                return 0.5  # Default score if no facts extracted
                
            # Check if student answer contains these facts
            fact_scores = []
            
            for fact in key_facts:
                # Use QA model to check if fact is present in student answer
                try:
                    result = self.qa_pipeline(
                        question=f"Does the answer mention {fact}?",
                        context=student_answer
                    )
                    
                    # Score based on confidence
                    fact_score = result['score'] if result['score'] > 0.3 else 0.0
                    fact_scores.append(fact_score)
                    
                except:
                    # Fallback to simple text matching
                    if fact.lower() in student_answer.lower():
                        fact_scores.append(0.7)
                    else:
                        fact_scores.append(0.0)
                        
            return sum(fact_scores) / len(fact_scores) if fact_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating factual accuracy: {str(e)}")
            return 0.0
            
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts from text"""
        try:
            # Simple fact extraction - can be enhanced with NER
            sentences = text.split('.')
            facts = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # Filter out very short sentences
                    # Look for factual patterns
                    if any(word in sentence.lower() for word in ['is', 'are', 'was', 'were', 'has', 'have', 'contains', 'includes']):
                        facts.append(sentence)
                        
            return facts[:5]  # Limit to top 5 facts
            
        except Exception as e:
            logger.error(f"Error extracting key facts: {str(e)}")
            return []
            
    def _calculate_completeness(self, student_answer: str, correct_answer: str) -> float:
        """Calculate completeness score"""
        try:
            if not student_answer:
                return 0.0
            if not correct_answer:
                return 1.0
                
            # Extract key concepts from correct answer
            correct_concepts = self._extract_concepts(correct_answer)
            student_concepts = self._extract_concepts(student_answer)
            
            if not correct_concepts:
                return 1.0
                
            # Calculate concept coverage
            covered_concepts = 0
            for concept in correct_concepts:
                if any(self._concept_similarity(concept, s_concept) > 0.7 
                      for s_concept in student_concepts):
                    covered_concepts += 1
                    
            completeness = covered_concepts / len(correct_concepts)
            
            # Adjust for answer length (too short or too long)
            length_ratio = len(student_answer.split()) / max(1, len(correct_answer.split()))
            
            if 0.5 <= length_ratio <= 1.5:
                length_penalty = 1.0
            elif length_ratio < 0.5:
                length_penalty = length_ratio / 0.5
            else:
                length_penalty = max(0.7, 1.5 / length_ratio)
                
            return completeness * length_penalty
            
        except Exception as e:
            logger.error(f"Error calculating completeness: {str(e)}")
            return 0.0
            
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        try:
            # Simple concept extraction - can be enhanced with NER/POS tagging
            words = text.split()
            concepts = []
            
            # Look for noun phrases and important terms
            for i, word in enumerate(words):
                if len(word) > 3 and word.isalpha():
                    # Check if it's likely a concept (not a common word)
                    if word.lower() not in ['this', 'that', 'with', 'from', 'they', 'them', 'were', 'been', 'have', 'will', 'would', 'could', 'should']:
                        concepts.append(word.lower())
                        
            return list(set(concepts))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting concepts: {str(e)}")
            return []
            
    def _concept_similarity(self, concept1: str, concept2: str) -> float:
        """Calculate similarity between two concepts"""
        try:
            # Simple string similarity - can be enhanced with word embeddings
            if concept1 == concept2:
                return 1.0
                
            # Check if one is substring of another
            if concept1 in concept2 or concept2 in concept1:
                return 0.8
                
            # Use basic edit distance
            from difflib import SequenceMatcher
            return SequenceMatcher(None, concept1, concept2).ratio()
            
        except Exception as e:
            logger.error(f"Error calculating concept similarity: {str(e)}")
            return 0.0
            
    def _calculate_relevance(self, question: str, student_answer: str) -> float:
        """Calculate relevance of answer to question"""
        try:
            if not student_answer or not question:
                return 0.0
                
            # Use sentence transformer to calculate relevance
            embeddings = self.sentence_transformer.encode([question, student_answer])
            relevance = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Normalize and adjust
            relevance = max(0.0, min(1.0, relevance))
            
            # Boost score if answer directly addresses question words
            question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
            for qword in question_words:
                if qword in question.lower() and qword in student_answer.lower():
                    relevance = min(1.0, relevance + 0.1)
                    
            return relevance
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return 0.0
            
    def _calculate_clarity_coherence(self, student_answer: str) -> float:
        """Calculate clarity and coherence score"""
        try:
            if not student_answer:
                return 0.0
                
            score = 0.0
            
            # Sentence structure analysis
            sentences = student_answer.split('.')
            valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
            
            if not valid_sentences:
                return 0.0
                
            # Average sentence length (optimal: 10-25 words)
            avg_length = sum(len(s.split()) for s in valid_sentences) / len(valid_sentences)
            
            if 10 <= avg_length <= 25:
                length_score = 1.0
            elif avg_length < 10:
                length_score = avg_length / 10
            else:
                length_score = max(0.5, 25 / avg_length)
                
            score += length_score * 0.4
            
            # Grammar and structure (simple heuristics)
            grammar_score = self._assess_grammar(student_answer)
            score += grammar_score * 0.3
            
            # Coherence (transition words, logical flow)
            coherence_score = self._assess_coherence(student_answer)
            score += coherence_score * 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating clarity/coherence: {str(e)}")
            return 0.0
            
    def _assess_grammar(self, text: str) -> float:
        """Simple grammar assessment"""
        try:
            # Basic grammar checks
            score = 1.0
            
            # Check for basic sentence structure
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    words = sentence.split()
                    if len(words) < 3:  # Very short sentences
                        score -= 0.1
                        
            # Check for repeated words (might indicate poor writing)
            words = text.lower().split()
            unique_words = set(words)
            if len(words) > 0:
                repetition_ratio = len(unique_words) / len(words)
                if repetition_ratio < 0.7:  # Too much repetition
                    score -= 0.2
                    
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Error assessing grammar: {str(e)}")
            return 0.5
            
    def _assess_coherence(self, text: str) -> float:
        """Assess coherence and logical flow"""
        try:
            score = 0.5  # Base score
            
            # Look for transition words
            transition_words = [
                'however', 'therefore', 'furthermore', 'moreover', 'additionally',
                'consequently', 'thus', 'hence', 'because', 'since', 'although',
                'while', 'whereas', 'first', 'second', 'finally', 'in conclusion'
            ]
            
            text_lower = text.lower()
            transition_count = sum(1 for word in transition_words if word in text_lower)
            
            # Boost score for appropriate use of transitions
            if transition_count > 0:
                score += min(0.3, transition_count * 0.1)
                
            # Check for logical structure (introduction, body, conclusion patterns)
            if any(phrase in text_lower for phrase in ['in conclusion', 'to summarize', 'finally']):
                score += 0.2
                
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error assessing coherence: {str(e)}")
            return 0.5
            
    def _calculate_weighted_score(self, scores: Dict[str, float], max_score: float) -> float:
        """Calculate final weighted score"""
        try:
            weighted_sum = 0.0
            
            for criterion, score in scores.items():
                weight = self.grading_criteria.get(criterion, {}).get('weight', 0.0)
                weighted_sum += score * weight
                
            return weighted_sum * max_score
            
        except Exception as e:
            logger.error(f"Error calculating weighted score: {str(e)}")
            return 0.0
            
    def _generate_detailed_feedback(self, question: str, student_answer: str, 
                                  correct_answer: str, scores: Dict[str, float]) -> str:
        """Generate detailed feedback based on scores"""
        try:
            feedback_parts = []
            
            # Overall assessment
            avg_score = sum(scores.values()) / len(scores)
            
            if avg_score >= 0.9:
                feedback_parts.append("Excellent work! Your answer demonstrates strong understanding and clear communication.")
            elif avg_score >= 0.7:
                feedback_parts.append("Good answer! You've covered the main points well with room for minor improvements.")
            elif avg_score >= 0.5:
                feedback_parts.append("Fair answer. You've addressed some key points but there are several areas for improvement.")
            else:
                feedback_parts.append("Your answer needs significant improvement. Please review the topic and try again.")
                
            # Specific feedback for each criterion
            if scores.get('semantic_similarity', 0) < 0.6:
                feedback_parts.append("Your answer doesn't closely match the expected response. Review the key concepts.")
                
            if scores.get('factual_accuracy', 0) < 0.6:
                feedback_parts.append("Some factual information appears to be missing or incorrect.")
                
            if scores.get('completeness', 0) < 0.6:
                feedback_parts.append("Your answer could be more comprehensive. Consider adding more details or examples.")
                
            if scores.get('relevance', 0) < 0.6:
                feedback_parts.append("Make sure your answer directly addresses the question asked.")
                
            if scores.get('clarity_coherence', 0) < 0.6:
                feedback_parts.append("Work on making your answer clearer and more well-structured.")
                
            return " ".join(feedback_parts)
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return "Unable to generate detailed feedback."
            
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate specific recommendations for improvement"""
        try:
            recommendations = []
            
            if scores.get('semantic_similarity', 0) < 0.7:
                recommendations.append("Study the key concepts more thoroughly to better align with expected answers.")
                
            if scores.get('factual_accuracy', 0) < 0.7:
                recommendations.append("Verify facts and include more specific, accurate information.")
                
            if scores.get('completeness', 0) < 0.7:
                recommendations.append("Provide more comprehensive answers with examples and detailed explanations.")
                
            if scores.get('relevance', 0) < 0.7:
                recommendations.append("Focus on directly answering the question without going off-topic.")
                
            if scores.get('clarity_coherence', 0) < 0.7:
                recommendations.append("Improve writing clarity with better sentence structure and logical flow.")
                
            if not recommendations:
                recommendations.append("Continue the excellent work! Minor refinements in expression could make your answers even better.")
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Focus on understanding key concepts and expressing them clearly."]
            
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return self.loaded
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'sentence_model': self.sentence_model_name,
            'bert_model': self.bert_model_name,
            'qa_model': self.qa_model_name,
            'device': str(self.device),
            'loaded': self.loaded,
            'grading_criteria': self.grading_criteria
        }
