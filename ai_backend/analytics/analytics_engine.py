"""
Analytics Engine for performance insights, trend analysis, and grading consistency
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
from collections import defaultdict
import io
import base64

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Comprehensive analytics for AI grading system"""
    
    def __init__(self):
        self.grading_history = []
        self.student_performance = defaultdict(list)
        self.question_analytics = defaultdict(list)
        self.system_metrics = defaultdict(list)
        
    def record_grading_event(self, event_data: Dict[str, Any]):
        """Record a grading event for analytics"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'student_id': event_data.get('student_id'),
                'exam_id': event_data.get('exam_id'),
                'question_id': event_data.get('question_id'),
                'ai_score': event_data.get('ai_score'),
                'human_score': event_data.get('human_score'),
                'confidence': event_data.get('confidence'),
                'grading_method': event_data.get('grading_method', 'ai'),
                'processing_time': event_data.get('processing_time'),
                'breakdown': event_data.get('breakdown', {}),
                'flagged_for_review': event_data.get('flagged_for_review', False)
            }
            
            self.grading_history.append(event)
            
            # Update student performance tracking
            if event['student_id']:
                self.student_performance[event['student_id']].append(event)
                
            # Update question analytics
            if event['question_id']:
                self.question_analytics[event['question_id']].append(event)
                
            logger.info(f"Recorded grading event for student {event['student_id']}")
            
        except Exception as e:
            logger.error(f"Error recording grading event: {str(e)}")
            
    def generate_student_report(self, student_id: str, 
                              time_period: int = 30) -> Dict[str, Any]:
        """Generate comprehensive student performance report"""
        try:
            # Get student data for the time period
            cutoff_date = datetime.now() - timedelta(days=time_period)
            student_events = [
                event for event in self.student_performance[student_id]
                if datetime.fromisoformat(event['timestamp']) >= cutoff_date
            ]
            
            if not student_events:
                return {'error': 'No data available for this student'}
                
            # Calculate performance metrics
            scores = [event['ai_score'] for event in student_events if event['ai_score']]
            
            performance_metrics = {
                'average_score': np.mean(scores) if scores else 0,
                'median_score': np.median(scores) if scores else 0,
                'score_std': np.std(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'total_submissions': len(student_events),
                'improvement_trend': self._calculate_improvement_trend(scores)
            }
            
            # Analyze performance by criteria
            criteria_analysis = self._analyze_criteria_performance(student_events)
            
            # Generate recommendations
            recommendations = self._generate_student_recommendations(
                performance_metrics, criteria_analysis
            )
            
            # Create visualizations
            visualizations = self._create_student_visualizations(student_events)
            
            return {
                'student_id': student_id,
                'time_period_days': time_period,
                'performance_metrics': performance_metrics,
                'criteria_analysis': criteria_analysis,
                'recommendations': recommendations,
                'visualizations': visualizations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating student report: {str(e)}")
            return {'error': str(e)}
            
    def generate_class_report(self, exam_id: str = None) -> Dict[str, Any]:
        """Generate class-wide performance report"""
        try:
            # Filter events by exam if specified
            if exam_id:
                events = [e for e in self.grading_history if e['exam_id'] == exam_id]
            else:
                events = self.grading_history
                
            if not events:
                return {'error': 'No data available'}
                
            # Calculate class statistics
            scores = [event['ai_score'] for event in events if event['ai_score']]
            
            class_metrics = {
                'total_students': len(set(e['student_id'] for e in events)),
                'total_submissions': len(events),
                'average_score': np.mean(scores) if scores else 0,
                'median_score': np.median(scores) if scores else 0,
                'score_std': np.std(scores) if scores else 0,
                'score_distribution': self._calculate_score_distribution(scores),
                'grading_consistency': self._calculate_grading_consistency(events)
            }
            
            # Analyze question difficulty
            question_analysis = self._analyze_question_difficulty(events)
            
            # Identify struggling students
            struggling_students = self._identify_struggling_students(events)
            
            # Create class visualizations
            visualizations = self._create_class_visualizations(events)
            
            return {
                'exam_id': exam_id,
                'class_metrics': class_metrics,
                'question_analysis': question_analysis,
                'struggling_students': struggling_students,
                'visualizations': visualizations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating class report: {str(e)}")
            return {'error': str(e)}
            
    def generate_system_report(self) -> Dict[str, Any]:
        """Generate system performance and reliability report"""
        try:
            # Calculate system metrics
            total_gradings = len(self.grading_history)
            flagged_count = len([e for e in self.grading_history if e['flagged_for_review']])
            
            # AI vs Human score comparison
            ai_human_comparisons = [
                e for e in self.grading_history 
                if e['ai_score'] and e['human_score']
            ]
            
            system_metrics = {
                'total_gradings': total_gradings,
                'flagged_percentage': (flagged_count / total_gradings * 100) if total_gradings > 0 else 0,
                'ai_human_agreement': self._calculate_ai_human_agreement(ai_human_comparisons),
                'average_processing_time': self._calculate_average_processing_time(),
                'grading_accuracy': self._calculate_grading_accuracy(),
                'system_reliability': self._calculate_system_reliability()
            }
            
            # Performance trends over time
            performance_trends = self._analyze_performance_trends()
            
            # Error analysis
            error_analysis = self._analyze_errors()
            
            return {
                'system_metrics': system_metrics,
                'performance_trends': performance_trends,
                'error_analysis': error_analysis,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating system report: {str(e)}")
            return {'error': str(e)}
            
    def _calculate_improvement_trend(self, scores: List[float]) -> str:
        """Calculate if student is improving, declining, or stable"""
        try:
            if len(scores) < 3:
                return "insufficient_data"
                
            # Use linear regression to find trend
            x = np.arange(len(scores))
            slope = np.polyfit(x, scores, 1)[0]
            
            if slope > 2:
                return "improving"
            elif slope < -2:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating improvement trend: {str(e)}")
            return "unknown"
            
    def _analyze_criteria_performance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance across different grading criteria"""
        try:
            criteria_scores = defaultdict(list)
            
            for event in events:
                breakdown = event.get('breakdown', {})
                for criterion, data in breakdown.items():
                    if isinstance(data, dict) and 'score' in data:
                        criteria_scores[criterion].append(data['score'])
                        
            criteria_analysis = {}
            for criterion, scores in criteria_scores.items():
                if scores:
                    criteria_analysis[criterion] = {
                        'average': np.mean(scores),
                        'trend': self._calculate_improvement_trend(scores),
                        'consistency': np.std(scores)
                    }
                    
            return criteria_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing criteria performance: {str(e)}")
            return {}
            
    def _generate_student_recommendations(self, metrics: Dict[str, Any], 
                                        criteria: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations for student"""
        recommendations = []
        
        try:
            avg_score = metrics.get('average_score', 0)
            trend = metrics.get('improvement_trend', 'unknown')
            
            # Overall performance recommendations
            if avg_score < 60:
                recommendations.append("Focus on fundamental concepts and seek additional help")
            elif avg_score < 80:
                recommendations.append("Good progress! Work on consistency and detail")
            else:
                recommendations.append("Excellent work! Challenge yourself with advanced topics")
                
            # Trend-based recommendations
            if trend == "declining":
                recommendations.append("Recent performance shows decline - review recent topics")
            elif trend == "improving":
                recommendations.append("Great improvement trend! Keep up the good work")
                
            # Criteria-specific recommendations
            for criterion, data in criteria.items():
                avg = data.get('average', 0)
                if avg < 70:
                    criterion_recommendations = {
                        'semantic_similarity': "Review key concepts and their relationships",
                        'factual_accuracy': "Focus on memorizing important facts and details",
                        'completeness': "Practice writing more comprehensive answers",
                        'clarity_coherence': "Work on organizing and expressing ideas clearly"
                    }
                    
                    if criterion in criterion_recommendations:
                        recommendations.append(criterion_recommendations[criterion])
                        
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            
        return recommendations
        
    def _create_student_visualizations(self, events: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create visualizations for student performance"""
        visualizations = {}
        
        try:
            # Score trend over time
            dates = [datetime.fromisoformat(e['timestamp']) for e in events]
            scores = [e['ai_score'] for e in events if e['ai_score']]
            
            if dates and scores:
                plt.figure(figsize=(10, 6))
                plt.plot(dates, scores, marker='o')
                plt.title('Score Trend Over Time')
                plt.xlabel('Date')
                plt.ylabel('Score')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                visualizations['score_trend'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
            # Criteria performance radar chart
            criteria_data = self._analyze_criteria_performance(events)
            if criteria_data:
                categories = list(criteria_data.keys())
                values = [criteria_data[cat]['average'] for cat in categories]
                
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
                values += values[:1]  # Complete the circle
                angles = np.concatenate((angles, [angles[0]]))
                
                plt.figure(figsize=(8, 8))
                ax = plt.subplot(111, projection='polar')
                ax.plot(angles, values, 'o-', linewidth=2)
                ax.fill(angles, values, alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories)
                ax.set_ylim(0, 100)
                plt.title('Performance by Criteria')
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                visualizations['criteria_radar'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            
        return visualizations
        
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution in grade bands"""
        try:
            distribution = {
                'A (90-100)': 0,
                'B (80-89)': 0,
                'C (70-79)': 0,
                'D (60-69)': 0,
                'F (0-59)': 0
            }
            
            for score in scores:
                if score >= 90:
                    distribution['A (90-100)'] += 1
                elif score >= 80:
                    distribution['B (80-89)'] += 1
                elif score >= 70:
                    distribution['C (70-79)'] += 1
                elif score >= 60:
                    distribution['D (60-69)'] += 1
                else:
                    distribution['F (0-59)'] += 1
                    
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating score distribution: {str(e)}")
            return {}
            
    def _calculate_grading_consistency(self, events: List[Dict[str, Any]]) -> float:
        """Calculate consistency of grading across similar questions"""
        try:
            # Group by question and calculate variance
            question_scores = defaultdict(list)
            
            for event in events:
                if event['question_id'] and event['ai_score']:
                    question_scores[event['question_id']].append(event['ai_score'])
                    
            variances = []
            for scores in question_scores.values():
                if len(scores) > 1:
                    variances.append(np.var(scores))
                    
            # Lower variance indicates higher consistency
            avg_variance = np.mean(variances) if variances else 0
            consistency_score = max(0, 100 - avg_variance)  # Convert to 0-100 scale
            
            return round(consistency_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating grading consistency: {str(e)}")
            return 0.0
            
    def _analyze_question_difficulty(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze difficulty of different questions"""
        try:
            question_stats = defaultdict(list)
            
            for event in events:
                if event['question_id'] and event['ai_score']:
                    question_stats[event['question_id']].append(event['ai_score'])
                    
            difficulty_analysis = {}
            for question_id, scores in question_stats.items():
                avg_score = np.mean(scores)
                
                if avg_score >= 85:
                    difficulty = "Easy"
                elif avg_score >= 70:
                    difficulty = "Medium"
                elif avg_score >= 55:
                    difficulty = "Hard"
                else:
                    difficulty = "Very Hard"
                    
                difficulty_analysis[question_id] = {
                    'average_score': round(avg_score, 2),
                    'difficulty_level': difficulty,
                    'attempts': len(scores),
                    'score_range': [min(scores), max(scores)]
                }
                
            return difficulty_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing question difficulty: {str(e)}")
            return {}
            
    def _identify_struggling_students(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify students who may need additional support"""
        try:
            student_performance = defaultdict(list)
            
            for event in events:
                if event['student_id'] and event['ai_score']:
                    student_performance[event['student_id']].append(event['ai_score'])
                    
            struggling_students = []
            
            for student_id, scores in student_performance.items():
                avg_score = np.mean(scores)
                recent_scores = scores[-3:] if len(scores) >= 3 else scores
                recent_avg = np.mean(recent_scores)
                
                # Criteria for struggling: low average or declining trend
                if avg_score < 60 or recent_avg < avg_score - 10:
                    struggling_students.append({
                        'student_id': student_id,
                        'average_score': round(avg_score, 2),
                        'recent_average': round(recent_avg, 2),
                        'total_submissions': len(scores),
                        'needs_attention': True
                    })
                    
            # Sort by most concerning first
            struggling_students.sort(key=lambda x: x['recent_average'])
            
            return struggling_students
            
        except Exception as e:
            logger.error(f"Error identifying struggling students: {str(e)}")
            return []
            
    def _create_class_visualizations(self, events: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create class-wide visualizations"""
        visualizations = {}
        
        try:
            scores = [e['ai_score'] for e in events if e['ai_score']]
            
            if scores:
                # Score distribution histogram
                plt.figure(figsize=(10, 6))
                plt.hist(scores, bins=20, edgecolor='black', alpha=0.7)
                plt.title('Class Score Distribution')
                plt.xlabel('Score')
                plt.ylabel('Frequency')
                plt.grid(True, alpha=0.3)
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                visualizations['score_distribution'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
        except Exception as e:
            logger.error(f"Error creating class visualizations: {str(e)}")
            
        return visualizations
        
    def _calculate_ai_human_agreement(self, comparisons: List[Dict[str, Any]]) -> float:
        """Calculate agreement between AI and human scores"""
        try:
            if not comparisons:
                return 0.0
                
            agreements = 0
            for comp in comparisons:
                ai_score = comp['ai_score']
                human_score = comp['human_score']
                
                # Consider agreement if within 10 points
                if abs(ai_score - human_score) <= 10:
                    agreements += 1
                    
            return round((agreements / len(comparisons)) * 100, 2)
            
        except Exception as e:
            logger.error(f"Error calculating AI-human agreement: {str(e)}")
            return 0.0
            
    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time for grading"""
        try:
            processing_times = [
                e['processing_time'] for e in self.grading_history 
                if e.get('processing_time')
            ]
            
            return round(np.mean(processing_times), 3) if processing_times else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating processing time: {str(e)}")
            return 0.0
            
    def _calculate_grading_accuracy(self) -> float:
        """Calculate overall grading accuracy"""
        try:
            # This would be based on human verification results
            # For now, return a placeholder
            return 85.0
            
        except Exception as e:
            logger.error(f"Error calculating grading accuracy: {str(e)}")
            return 0.0
            
    def _calculate_system_reliability(self) -> float:
        """Calculate system reliability metrics"""
        try:
            total_attempts = len(self.grading_history)
            successful_attempts = len([
                e for e in self.grading_history 
                if e.get('ai_score') is not None
            ])
            
            return round((successful_attempts / total_attempts) * 100, 2) if total_attempts > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating system reliability: {str(e)}")
            return 0.0
            
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            # Group events by day and calculate daily averages
            daily_scores = defaultdict(list)
            
            for event in self.grading_history:
                if event.get('ai_score'):
                    date = datetime.fromisoformat(event['timestamp']).date()
                    daily_scores[date].append(event['ai_score'])
                    
            trends = {}
            for date, scores in daily_scores.items():
                trends[date.isoformat()] = {
                    'average_score': round(np.mean(scores), 2),
                    'total_submissions': len(scores)
                }
                
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {}
            
    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze system errors and issues"""
        try:
            # This would analyze error logs and failed grading attempts
            # For now, return placeholder data
            return {
                'total_errors': 0,
                'error_rate': 0.0,
                'common_error_types': []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing errors: {str(e)}")
            return {}
