"""
Automated Feedback Generator with detailed explanations
Generates personalized feedback for student answers
"""

import logging
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
import random
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """Generates detailed, personalized feedback for student answers"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.text_generator = None
        self.loaded = False
        
        # Feedback templates organized by score ranges and criteria
        self.feedback_templates = {
            'excellent': {
                'overall': [
                    "Outstanding work! Your answer demonstrates exceptional understanding of the topic.",
                    "Excellent response! You've shown mastery of the key concepts.",
                    "Superb answer! Your explanation is comprehensive and well-articulated."
                ],
                'semantic': [
                    "Your answer aligns perfectly with the expected response.",
                    "You've captured the essence of the correct answer beautifully.",
                    "Your understanding of the core concepts is excellent."
                ],
                'factual': [
                    "All factual information in your answer is accurate and relevant.",
                    "You've included all the key facts correctly.",
                    "Your factual accuracy is impressive."
                ],
                'completeness': [
                    "Your answer is comprehensive and covers all important aspects.",
                    "You've provided a complete and thorough response.",
                    "Your answer addresses all parts of the question effectively."
                ],
                'clarity': [
                    "Your answer is exceptionally clear and well-structured.",
                    "Your writing is coherent and easy to follow.",
                    "You've expressed your ideas with remarkable clarity."
                ]
            },
            'good': {
                'overall': [
                    "Good work! Your answer shows solid understanding with room for minor improvements.",
                    "Well done! You've grasped the main concepts effectively.",
                    "Nice job! Your response demonstrates good knowledge of the topic."
                ],
                'semantic': [
                    "Your answer is generally aligned with the expected response.",
                    "You've understood most of the key concepts correctly.",
                    "Your interpretation is mostly accurate with minor gaps."
                ],
                'factual': [
                    "Most of your factual information is correct.",
                    "You've included several key facts accurately.",
                    "Your factual content is generally reliable."
                ],
                'completeness': [
                    "Your answer covers most of the important points.",
                    "You've addressed the main aspects of the question well.",
                    "Your response is fairly comprehensive."
                ],
                'clarity': [
                    "Your answer is generally clear and well-organized.",
                    "Your writing is mostly coherent and understandable.",
                    "You've expressed your ideas reasonably well."
                ]
            },
            'fair': {
                'overall': [
                    "Fair attempt. Your answer shows some understanding but needs improvement.",
                    "You've made a reasonable effort, but there are several areas to work on.",
                    "Your answer demonstrates partial understanding of the topic."
                ],
                'semantic': [
                    "Your answer partially aligns with the expected response.",
                    "You've understood some concepts but missed others.",
                    "Your interpretation needs refinement in several areas."
                ],
                'factual': [
                    "Some of your factual information is correct, but there are inaccuracies.",
                    "You've included some relevant facts but missed key information.",
                    "Your factual accuracy needs improvement."
                ],
                'completeness': [
                    "Your answer addresses some aspects but lacks completeness.",
                    "You've covered basic points but need more detail.",
                    "Your response could be more comprehensive."
                ],
                'clarity': [
                    "Your answer could be clearer and better organized.",
                    "Your writing needs improvement in structure and flow.",
                    "Work on expressing your ideas more clearly."
                ]
            },
            'poor': {
                'overall': [
                    "Your answer needs significant improvement. Please review the topic thoroughly.",
                    "This response shows limited understanding. Additional study is recommended.",
                    "Your answer requires substantial revision. Consider seeking additional help."
                ],
                'semantic': [
                    "Your answer doesn't align well with the expected response.",
                    "You seem to have misunderstood key concepts.",
                    "Your interpretation needs major correction."
                ],
                'factual': [
                    "Several factual errors are present in your answer.",
                    "Key factual information is missing or incorrect.",
                    "Your factual accuracy needs significant improvement."
                ],
                'completeness': [
                    "Your answer is incomplete and lacks important details.",
                    "You've missed most of the key points.",
                    "Your response needs to be much more comprehensive."
                ],
                'clarity': [
                    "Your answer is unclear and poorly structured.",
                    "Your writing is difficult to follow and understand.",
                    "Significant improvement in clarity and organization is needed."
                ]
            }
        }
        
        # Improvement suggestions
        self.improvement_suggestions = {
            'semantic_similarity': [
                "Review the key concepts and their relationships more carefully.",
                "Study model answers to better understand expected responses.",
                "Focus on understanding the core principles behind the topic."
            ],
            'factual_accuracy': [
                "Verify facts using reliable sources before including them.",
                "Create fact cards to memorize key information.",
                "Practice identifying and correcting factual errors."
            ],
            'completeness': [
                "Create an outline before writing to ensure all points are covered.",
                "Use the question as a checklist to verify completeness.",
                "Practice expanding on key points with examples and details."
            ],
            'relevance': [
                "Read the question carefully and underline key terms.",
                "Stay focused on the specific question being asked.",
                "Avoid including irrelevant information that doesn't answer the question."
            ],
            'clarity_coherence': [
                "Use transition words to connect ideas smoothly.",
                "Write shorter, clearer sentences to improve readability.",
                "Organize your answer with a clear introduction, body, and conclusion."
            ]
        }
        
    def load_model(self):
        """Load text generation model for enhanced feedback"""
        try:
            logger.info("Loading feedback generation model...")
            
            # Load a lightweight text generation model
            model_name = "facebook/bart-base"
            self.text_generator = pipeline(
                "text2text-generation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                max_length=150
            )
            
            self.loaded = True
            logger.info("Feedback generation model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading feedback model: {str(e)}")
            self.loaded = False
            
    def generate_comprehensive_feedback(self, grading_result: Dict[str, Any], 
                                      question: str, student_answer: str, 
                                      correct_answer: str) -> Dict[str, Any]:
        """Generate comprehensive feedback based on grading results"""
        try:
            # Extract scores and breakdown
            final_score = grading_result.get('final_score', 0)
            max_score = grading_result.get('max_score', 100)
            percentage = grading_result.get('percentage', 0)
            breakdown = grading_result.get('breakdown', {})
            
            # Determine overall performance level
            performance_level = self._determine_performance_level(percentage)
            
            # Generate different types of feedback
            feedback_components = {
                'overall_feedback': self._generate_overall_feedback(
                    performance_level, final_score, max_score
                ),
                'detailed_feedback': self._generate_detailed_feedback(
                    breakdown, performance_level
                ),
                'specific_improvements': self._generate_improvement_suggestions(
                    breakdown
                ),
                'strengths': self._identify_strengths(breakdown),
                'weaknesses': self._identify_weaknesses(breakdown),
                'next_steps': self._generate_next_steps(breakdown, performance_level),
                'encouragement': self._generate_encouragement(performance_level)
            }
            
            # Generate AI-enhanced feedback if model is loaded
            if self.loaded:
                ai_feedback = self._generate_ai_enhanced_feedback(
                    question, student_answer, correct_answer, grading_result
                )
                feedback_components['ai_enhanced_feedback'] = ai_feedback
                
            return {
                'feedback_components': feedback_components,
                'summary': self._create_feedback_summary(feedback_components),
                'generated_at': datetime.now().isoformat(),
                'performance_level': performance_level
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive feedback: {str(e)}")
            return {
                'error': str(e),
                'feedback_components': {},
                'summary': "Unable to generate feedback at this time."
            }
            
    def _determine_performance_level(self, percentage: float) -> str:
        """Determine performance level based on percentage score"""
        if percentage >= 90:
            return 'excellent'
        elif percentage >= 70:
            return 'good'
        elif percentage >= 50:
            return 'fair'
        else:
            return 'poor'
            
    def _generate_overall_feedback(self, performance_level: str, 
                                 final_score: float, max_score: float) -> str:
        """Generate overall feedback message"""
        try:
            templates = self.feedback_templates[performance_level]['overall']
            base_feedback = random.choice(templates)
            
            score_info = f" You scored {final_score:.1f} out of {max_score} points ({(final_score/max_score)*100:.1f}%)."
            
            return base_feedback + score_info
            
        except Exception as e:
            logger.error(f"Error generating overall feedback: {str(e)}")
            return f"You scored {final_score:.1f} out of {max_score} points."
            
    def _generate_detailed_feedback(self, breakdown: Dict[str, Any], 
                                  performance_level: str) -> Dict[str, str]:
        """Generate detailed feedback for each criterion"""
        detailed_feedback = {}
        
        try:
            for criterion, data in breakdown.items():
                score = data.get('score', 0) / 100  # Convert to 0-1 range
                
                # Determine level for this specific criterion
                if score >= 0.9:
                    level = 'excellent'
                elif score >= 0.7:
                    level = 'good'
                elif score >= 0.5:
                    level = 'fair'
                else:
                    level = 'poor'
                    
                # Get appropriate template
                criterion_key = self._map_criterion_to_template_key(criterion)
                if criterion_key in self.feedback_templates[level]:
                    templates = self.feedback_templates[level][criterion_key]
                    feedback = random.choice(templates)
                    detailed_feedback[criterion] = feedback
                    
        except Exception as e:
            logger.error(f"Error generating detailed feedback: {str(e)}")
            
        return detailed_feedback
        
    def _map_criterion_to_template_key(self, criterion: str) -> str:
        """Map grading criterion to feedback template key"""
        mapping = {
            'semantic_similarity': 'semantic',
            'factual_accuracy': 'factual',
            'completeness': 'completeness',
            'relevance': 'semantic',
            'clarity_coherence': 'clarity'
        }
        return mapping.get(criterion, 'overall')
        
    def _generate_improvement_suggestions(self, breakdown: Dict[str, Any]) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        try:
            for criterion, data in breakdown.items():
                score = data.get('score', 0)
                
                if score < 70:  # Needs improvement
                    if criterion in self.improvement_suggestions:
                        criterion_suggestions = self.improvement_suggestions[criterion]
                        suggestions.extend(random.sample(
                            criterion_suggestions, 
                            min(2, len(criterion_suggestions))
                        ))
                        
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {str(e)}")
            
        return list(set(suggestions))  # Remove duplicates
        
    def _identify_strengths(self, breakdown: Dict[str, Any]) -> List[str]:
        """Identify student's strengths based on scores"""
        strengths = []
        
        try:
            for criterion, data in breakdown.items():
                score = data.get('score', 0)
                
                if score >= 80:  # Strong performance
                    strength_descriptions = {
                        'semantic_similarity': 'Strong conceptual understanding',
                        'factual_accuracy': 'Excellent factual knowledge',
                        'completeness': 'Comprehensive answer coverage',
                        'relevance': 'Good focus on the question',
                        'clarity_coherence': 'Clear and well-organized writing'
                    }
                    
                    if criterion in strength_descriptions:
                        strengths.append(strength_descriptions[criterion])
                        
        except Exception as e:
            logger.error(f"Error identifying strengths: {str(e)}")
            
        return strengths
        
    def _identify_weaknesses(self, breakdown: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        weaknesses = []
        
        try:
            for criterion, data in breakdown.items():
                score = data.get('score', 0)
                
                if score < 60:  # Needs improvement
                    weakness_descriptions = {
                        'semantic_similarity': 'Conceptual understanding needs work',
                        'factual_accuracy': 'Factual knowledge requires improvement',
                        'completeness': 'Answer completeness needs attention',
                        'relevance': 'Focus on question relevance',
                        'clarity_coherence': 'Writing clarity and organization'
                    }
                    
                    if criterion in weakness_descriptions:
                        weaknesses.append(weakness_descriptions[criterion])
                        
        except Exception as e:
            logger.error(f"Error identifying weaknesses: {str(e)}")
            
        return weaknesses
        
    def _generate_next_steps(self, breakdown: Dict[str, Any], 
                           performance_level: str) -> List[str]:
        """Generate actionable next steps"""
        next_steps = []
        
        try:
            if performance_level == 'excellent':
                next_steps = [
                    "Continue your excellent work and help others learn",
                    "Challenge yourself with more advanced topics",
                    "Consider teaching or tutoring to reinforce your knowledge"
                ]
            elif performance_level == 'good':
                next_steps = [
                    "Review areas where you lost points for improvement",
                    "Practice similar questions to reinforce learning",
                    "Seek clarification on any remaining unclear concepts"
                ]
            elif performance_level == 'fair':
                next_steps = [
                    "Schedule additional study time for this topic",
                    "Review class materials and textbook sections",
                    "Consider forming a study group with classmates",
                    "Ask your teacher for additional practice materials"
                ]
            else:  # poor
                next_steps = [
                    "Schedule a meeting with your teacher for extra help",
                    "Review fundamental concepts before moving forward",
                    "Consider tutoring or additional learning resources",
                    "Break down the topic into smaller, manageable parts"
                ]
                
        except Exception as e:
            logger.error(f"Error generating next steps: {str(e)}")
            
        return next_steps
        
    def _generate_encouragement(self, performance_level: str) -> str:
        """Generate encouraging message"""
        encouragement_messages = {
            'excellent': [
                "Keep up the outstanding work! You're demonstrating mastery of this subject.",
                "Your dedication to learning is evident in your excellent performance.",
                "You're setting a great example for others with your thorough understanding."
            ],
            'good': [
                "You're doing well! With a little more focus, you can achieve excellence.",
                "Good progress! You're on the right track to mastering this topic.",
                "Your effort is paying off. Keep building on this solid foundation."
            ],
            'fair': [
                "Don't get discouraged! Learning is a process, and you're making progress.",
                "With continued effort and practice, you can improve significantly.",
                "Every expert was once a beginner. Keep working and you'll get there!"
            ],
            'poor': [
                "Remember that everyone learns at their own pace. Don't give up!",
                "This is an opportunity to identify areas for growth and improvement.",
                "With the right support and effort, you can overcome these challenges."
            ]
        }
        
        messages = encouragement_messages.get(performance_level, encouragement_messages['fair'])
        return random.choice(messages)
        
    def _generate_ai_enhanced_feedback(self, question: str, student_answer: str, 
                                     correct_answer: str, grading_result: Dict[str, Any]) -> str:
        """Generate AI-enhanced feedback using language model"""
        try:
            if not self.loaded:
                return ""
                
            # Create prompt for AI feedback generation
            prompt = f"""
            Question: {question[:200]}
            Student Answer: {student_answer[:300]}
            Expected Answer: {correct_answer[:300]}
            Score: {grading_result.get('percentage', 0):.1f}%
            
            Generate constructive feedback:
            """
            
            # Generate feedback using the model
            result = self.text_generator(
                prompt,
                max_length=100,
                num_return_sequences=1,
                temperature=0.7
            )
            
            if result and len(result) > 0:
                return result[0]['generated_text'].strip()
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error generating AI-enhanced feedback: {str(e)}")
            return ""
            
    def _create_feedback_summary(self, feedback_components: Dict[str, Any]) -> str:
        """Create a concise summary of all feedback"""
        try:
            summary_parts = []
            
            # Add overall feedback
            if 'overall_feedback' in feedback_components:
                summary_parts.append(feedback_components['overall_feedback'])
                
            # Add key strengths
            strengths = feedback_components.get('strengths', [])
            if strengths:
                summary_parts.append(f"Strengths: {', '.join(strengths[:2])}")
                
            # Add key areas for improvement
            weaknesses = feedback_components.get('weaknesses', [])
            if weaknesses:
                summary_parts.append(f"Areas for improvement: {', '.join(weaknesses[:2])}")
                
            # Add encouragement
            if 'encouragement' in feedback_components:
                summary_parts.append(feedback_components['encouragement'])
                
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating feedback summary: {str(e)}")
            return "Feedback summary unavailable."
            
    def is_loaded(self) -> bool:
        """Check if feedback model is loaded"""
        return self.loaded
        
    def get_feedback_templates(self) -> Dict[str, Any]:
        """Get available feedback templates"""
        return self.feedback_templates
