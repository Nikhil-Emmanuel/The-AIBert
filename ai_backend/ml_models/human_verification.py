"""
Human Verification Module for flagged responses and quality control
Manages the review process for AI-graded answers that need human oversight
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class FlagReason(Enum):
    LOW_CONFIDENCE = "low_confidence"
    INCONSISTENT_SCORING = "inconsistent_scoring"
    UNUSUAL_ANSWER = "unusual_answer"
    TECHNICAL_ERROR = "technical_error"
    MANUAL_REQUEST = "manual_request"
    QUALITY_CHECK = "quality_check"

@dataclass
class ReviewItem:
    """Data class for items requiring human review"""
    id: str
    student_id: str
    exam_id: str
    question_id: str
    question_text: str
    student_answer: str
    correct_answer: str
    ai_score: float
    ai_feedback: str
    flag_reason: FlagReason
    confidence_score: float
    created_at: str
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_id: Optional[str] = None
    human_score: Optional[float] = None
    human_feedback: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[str] = None
    priority: int = 1  # 1=low, 2=medium, 3=high

class HumanVerificationManager:
    """Manages human verification workflow for AI grading"""
    
    def __init__(self):
        self.review_queue = {}  # id -> ReviewItem
        self.reviewers = {}     # reviewer_id -> reviewer_info
        self.review_history = []
        
        # Configuration
        self.confidence_threshold = 0.7
        self.score_variance_threshold = 0.2
        self.auto_flag_criteria = {
            'low_confidence': 0.6,
            'score_variance': 0.25,
            'unusual_length_ratio': 3.0
        }
        
    def should_flag_for_review(self, grading_result: Dict[str, Any], 
                              question: str, student_answer: str) -> tuple[bool, List[FlagReason]]:
        """Determine if a grading result should be flagged for human review"""
        try:
            flags = []
            
            # Check confidence score
            confidence = grading_result.get('breakdown', {})
            avg_confidence = self._calculate_average_confidence(confidence)
            
            if avg_confidence < self.auto_flag_criteria['low_confidence']:
                flags.append(FlagReason.LOW_CONFIDENCE)
                
            # Check for inconsistent scoring across criteria
            if self._has_inconsistent_scoring(confidence):
                flags.append(FlagReason.INCONSISTENT_SCORING)
                
            # Check for unusual answer characteristics
            if self._is_unusual_answer(student_answer, question):
                flags.append(FlagReason.UNUSUAL_ANSWER)
                
            # Random quality checks (5% of all submissions)
            import random
            if random.random() < 0.05:
                flags.append(FlagReason.QUALITY_CHECK)
                
            return len(flags) > 0, flags
            
        except Exception as e:
            logger.error(f"Error checking flag criteria: {str(e)}")
            return True, [FlagReason.TECHNICAL_ERROR]
            
    def add_to_review_queue(self, student_id: str, exam_id: str, question_id: str,
                           question_text: str, student_answer: str, correct_answer: str,
                           grading_result: Dict[str, Any], flag_reasons: List[FlagReason],
                           priority: int = 1) -> str:
        """Add an item to the human review queue"""
        try:
            review_id = str(uuid.uuid4())
            
            # Calculate confidence score
            confidence = self._calculate_average_confidence(
                grading_result.get('breakdown', {})
            )
            
            review_item = ReviewItem(
                id=review_id,
                student_id=student_id,
                exam_id=exam_id,
                question_id=question_id,
                question_text=question_text,
                student_answer=student_answer,
                correct_answer=correct_answer,
                ai_score=grading_result.get('final_score', 0),
                ai_feedback=grading_result.get('feedback', ''),
                flag_reason=flag_reasons[0] if flag_reasons else FlagReason.MANUAL_REQUEST,
                confidence_score=confidence,
                created_at=datetime.now().isoformat(),
                priority=priority
            )
            
            self.review_queue[review_id] = review_item
            
            logger.info(f"Added item {review_id} to review queue with priority {priority}")
            return review_id
            
        except Exception as e:
            logger.error(f"Error adding to review queue: {str(e)}")
            return ""
            
    def get_review_queue(self, reviewer_id: str = None, status: ReviewStatus = None,
                        priority: int = None) -> List[Dict[str, Any]]:
        """Get items from review queue with optional filtering"""
        try:
            items = list(self.review_queue.values())
            
            # Apply filters
            if status:
                items = [item for item in items if item.status == status]
                
            if priority:
                items = [item for item in items if item.priority >= priority]
                
            if reviewer_id:
                items = [item for item in items if item.reviewer_id == reviewer_id]
                
            # Sort by priority (high to low) and creation time (oldest first)
            items.sort(key=lambda x: (-x.priority, x.created_at))
            
            return [asdict(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error getting review queue: {str(e)}")
            return []
            
    def assign_reviewer(self, review_id: str, reviewer_id: str) -> bool:
        """Assign a reviewer to a review item"""
        try:
            if review_id not in self.review_queue:
                logger.error(f"Review item {review_id} not found")
                return False
                
            item = self.review_queue[review_id]
            
            if item.status != ReviewStatus.PENDING:
                logger.error(f"Review item {review_id} is not in pending status")
                return False
                
            item.reviewer_id = reviewer_id
            item.status = ReviewStatus.IN_REVIEW
            
            logger.info(f"Assigned reviewer {reviewer_id} to item {review_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning reviewer: {str(e)}")
            return False
            
    def submit_review(self, review_id: str, reviewer_id: str, human_score: float,
                     human_feedback: str, review_notes: str = "",
                     final_status: ReviewStatus = ReviewStatus.APPROVED) -> bool:
        """Submit a human review for an item"""
        try:
            if review_id not in self.review_queue:
                logger.error(f"Review item {review_id} not found")
                return False
                
            item = self.review_queue[review_id]
            
            if item.reviewer_id != reviewer_id:
                logger.error(f"Reviewer {reviewer_id} not assigned to item {review_id}")
                return False
                
            # Update review item
            item.human_score = human_score
            item.human_feedback = human_feedback
            item.review_notes = review_notes
            item.status = final_status
            item.reviewed_at = datetime.now().isoformat()
            
            # Add to history
            self.review_history.append({
                'review_id': review_id,
                'reviewer_id': reviewer_id,
                'ai_score': item.ai_score,
                'human_score': human_score,
                'score_difference': abs(human_score - item.ai_score),
                'reviewed_at': item.reviewed_at,
                'flag_reason': item.flag_reason.value,
                'status': final_status.value
            })
            
            logger.info(f"Review submitted for item {review_id} by {reviewer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting review: {str(e)}")
            return False
            
    def get_review_item(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific review item"""
        try:
            if review_id in self.review_queue:
                return asdict(self.review_queue[review_id])
            return None
            
        except Exception as e:
            logger.error(f"Error getting review item: {str(e)}")
            return None
            
    def get_reviewer_workload(self, reviewer_id: str) -> Dict[str, Any]:
        """Get workload statistics for a reviewer"""
        try:
            assigned_items = [
                item for item in self.review_queue.values()
                if item.reviewer_id == reviewer_id
            ]
            
            pending_count = len([
                item for item in assigned_items
                if item.status == ReviewStatus.IN_REVIEW
            ])
            
            completed_count = len([
                item for item in assigned_items
                if item.status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]
            ])
            
            # Calculate average review time
            completed_items = [
                item for item in assigned_items
                if item.reviewed_at and item.status != ReviewStatus.IN_REVIEW
            ]
            
            avg_review_time = 0
            if completed_items:
                total_time = 0
                for item in completed_items:
                    created = datetime.fromisoformat(item.created_at)
                    reviewed = datetime.fromisoformat(item.reviewed_at)
                    total_time += (reviewed - created).total_seconds()
                avg_review_time = total_time / len(completed_items) / 3600  # hours
                
            return {
                'reviewer_id': reviewer_id,
                'pending_reviews': pending_count,
                'completed_reviews': completed_count,
                'total_assigned': len(assigned_items),
                'average_review_time_hours': round(avg_review_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting reviewer workload: {str(e)}")
            return {}
            
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics for human verification"""
        try:
            total_items = len(self.review_queue)
            
            status_counts = {}
            for status in ReviewStatus:
                status_counts[status.value] = len([
                    item for item in self.review_queue.values()
                    if item.status == status
                ])
                
            flag_reason_counts = {}
            for reason in FlagReason:
                flag_reason_counts[reason.value] = len([
                    item for item in self.review_queue.values()
                    if item.flag_reason == reason
                ])
                
            # Calculate AI vs Human score differences
            score_differences = []
            for item in self.review_queue.values():
                if item.human_score is not None:
                    diff = abs(item.ai_score - item.human_score)
                    score_differences.append(diff)
                    
            avg_score_difference = (
                sum(score_differences) / len(score_differences)
                if score_differences else 0
            )
            
            return {
                'total_items': total_items,
                'status_distribution': status_counts,
                'flag_reason_distribution': flag_reason_counts,
                'average_ai_human_score_difference': round(avg_score_difference, 2),
                'review_accuracy': self._calculate_review_accuracy(),
                'queue_age_stats': self._calculate_queue_age_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {str(e)}")
            return {}
            
    def _calculate_average_confidence(self, breakdown: Dict[str, Any]) -> float:
        """Calculate average confidence from grading breakdown"""
        try:
            if not breakdown:
                return 0.0
                
            scores = []
            for criterion_data in breakdown.values():
                if isinstance(criterion_data, dict) and 'score' in criterion_data:
                    scores.append(criterion_data['score'] / 100)
                    
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average confidence: {str(e)}")
            return 0.0
            
    def _has_inconsistent_scoring(self, breakdown: Dict[str, Any]) -> bool:
        """Check if scoring is inconsistent across criteria"""
        try:
            if not breakdown:
                return False
                
            scores = []
            for criterion_data in breakdown.values():
                if isinstance(criterion_data, dict) and 'score' in criterion_data:
                    scores.append(criterion_data['score'])
                    
            if len(scores) < 2:
                return False
                
            # Calculate variance
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            
            return variance > (self.auto_flag_criteria['score_variance'] * 100) ** 2
            
        except Exception as e:
            logger.error(f"Error checking scoring consistency: {str(e)}")
            return False
            
    def _is_unusual_answer(self, student_answer: str, question: str) -> bool:
        """Check if answer has unusual characteristics"""
        try:
            if not student_answer or not question:
                return True
                
            # Check length ratio
            answer_words = len(student_answer.split())
            question_words = len(question.split())
            
            if question_words > 0:
                length_ratio = answer_words / question_words
                if length_ratio > self.auto_flag_criteria['unusual_length_ratio']:
                    return True
                    
            # Check for very short answers
            if answer_words < 3:
                return True
                
            # Check for repeated content
            words = student_answer.lower().split()
            unique_words = set(words)
            if len(words) > 10 and len(unique_words) / len(words) < 0.5:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking unusual answer: {str(e)}")
            return True
            
    def _calculate_review_accuracy(self) -> float:
        """Calculate how often human reviews agree with AI scores"""
        try:
            if not self.review_history:
                return 0.0
                
            agreements = 0
            total_reviews = len(self.review_history)
            
            for review in self.review_history:
                ai_score = review['ai_score']
                human_score = review['human_score']
                
                # Consider it an agreement if scores are within 10 points
                if abs(ai_score - human_score) <= 10:
                    agreements += 1
                    
            return (agreements / total_reviews) * 100 if total_reviews > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating review accuracy: {str(e)}")
            return 0.0
            
    def _calculate_queue_age_stats(self) -> Dict[str, float]:
        """Calculate statistics about how long items stay in queue"""
        try:
            now = datetime.now()
            ages = []
            
            for item in self.review_queue.values():
                created = datetime.fromisoformat(item.created_at)
                age_hours = (now - created).total_seconds() / 3600
                ages.append(age_hours)
                
            if not ages:
                return {'average_age_hours': 0, 'oldest_item_hours': 0}
                
            return {
                'average_age_hours': round(sum(ages) / len(ages), 2),
                'oldest_item_hours': round(max(ages), 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating queue age stats: {str(e)}")
            return {'average_age_hours': 0, 'oldest_item_hours': 0}
            
    def register_reviewer(self, reviewer_id: str, reviewer_info: Dict[str, Any]) -> bool:
        """Register a new reviewer"""
        try:
            self.reviewers[reviewer_id] = {
                **reviewer_info,
                'registered_at': datetime.now().isoformat(),
                'total_reviews': 0,
                'average_score_difference': 0.0
            }
            
            logger.info(f"Registered new reviewer: {reviewer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering reviewer: {str(e)}")
            return False
            
    def get_reviewers(self) -> Dict[str, Any]:
        """Get all registered reviewers"""
        return self.reviewers.copy()
