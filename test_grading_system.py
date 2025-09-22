#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI-Assisted Grading System
Tests all components including OCR, grading, feedback, and analytics
"""

import unittest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image
import io
import base64

# Add the ai_backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_backend'))

# Import modules to test
from ml_models.ocr_module import OCRManager, HandwritingOCR
from ml_models.grading_engine import AdvancedGradingEngine
from ml_models.feedback_generator import FeedbackGenerator
from ml_models.human_verification import HumanVerificationManager, FlagReason, ReviewStatus
from ml_models.answer_mapper import AnswerMapper
from ml_models.educational_assistant import EducationalAssistant
from analytics.analytics_engine import AnalyticsEngine

class TestOCRModule(unittest.TestCase):
    """Test OCR functionality"""
    
    def setUp(self):
        self.ocr_manager = OCRManager()
        
    def test_ocr_manager_initialization(self):
        """Test OCR manager initializes correctly"""
        self.assertIsNotNone(self.ocr_manager.handwriting_ocr)
        self.assertIsNotNone(self.ocr_manager.printed_ocr)
        
    def test_image_preprocessing(self):
        """Test image preprocessing functionality"""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='white')
        
        # Convert to base64
        buffer = io.BytesIO()
        test_image.save(buffer, format='PNG')
        buffer.seek(0)
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        
        # Test preprocessing
        processed = self.ocr_manager.handwriting_ocr.preprocess_image(base64_image)
        self.assertIsNotNone(processed)
        
    @patch('transformers.TrOCRProcessor')
    @patch('transformers.VisionEncoderDecoderModel')
    def test_handwriting_ocr_loading(self, mock_model, mock_processor):
        """Test handwriting OCR model loading"""
        mock_processor.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        ocr = HandwritingOCR()
        ocr.load_model()
        
        self.assertTrue(mock_processor.from_pretrained.called)
        self.assertTrue(mock_model.from_pretrained.called)

class TestGradingEngine(unittest.TestCase):
    """Test advanced grading engine"""
    
    def setUp(self):
        self.grading_engine = AdvancedGradingEngine()
        
    def test_grading_engine_initialization(self):
        """Test grading engine initializes with correct criteria"""
        self.assertIn('semantic_similarity', self.grading_engine.grading_criteria)
        self.assertIn('factual_accuracy', self.grading_engine.grading_criteria)
        self.assertIn('completeness', self.grading_engine.grading_criteria)
        
    @patch('sentence_transformers.SentenceTransformer')
    def test_model_loading(self, mock_transformer):
        """Test model loading"""
        mock_transformer.return_value = Mock()
        
        self.grading_engine.load_models()
        self.assertTrue(mock_transformer.called)
        
    def test_text_preprocessing(self):
        """Test text preprocessing"""
        test_text = "  This is a TEST with CAPS and   extra spaces!  "
        processed = self.grading_engine._preprocess_text(test_text)
        
        self.assertEqual(processed, "this is a test with caps and extra spaces!")
        
    def test_grading_without_models(self):
        """Test grading behavior when models aren't loaded"""
        result = self.grading_engine.grade_answer(
            "What is photosynthesis?",
            "Photosynthesis is the process by which plants make food",
            "Photosynthesis is the process by which plants convert sunlight into energy"
        )
        
        self.assertIn('error', result)
        self.assertEqual(result['score'], 0.0)

class TestFeedbackGenerator(unittest.TestCase):
    """Test feedback generation system"""
    
    def setUp(self):
        self.feedback_generator = FeedbackGenerator()
        
    def test_feedback_generator_initialization(self):
        """Test feedback generator initializes with templates"""
        self.assertIn('excellent', self.feedback_generator.feedback_templates)
        self.assertIn('good', self.feedback_generator.feedback_templates)
        self.assertIn('fair', self.feedback_generator.feedback_templates)
        self.assertIn('poor', self.feedback_generator.feedback_templates)
        
    def test_performance_level_determination(self):
        """Test performance level determination"""
        self.assertEqual(self.feedback_generator._determine_performance_level(95), 'excellent')
        self.assertEqual(self.feedback_generator._determine_performance_level(75), 'good')
        self.assertEqual(self.feedback_generator._determine_performance_level(55), 'fair')
        self.assertEqual(self.feedback_generator._determine_performance_level(35), 'poor')
        
    def test_feedback_generation(self):
        """Test comprehensive feedback generation"""
        mock_grading_result = {
            'final_score': 85,
            'max_score': 100,
            'percentage': 85,
            'breakdown': {
                'semantic_similarity': {'score': 90, 'weight': 0.4},
                'factual_accuracy': {'score': 80, 'weight': 0.3}
            },
            'feedback': 'Good answer overall',
            'recommendations': ['Study more examples']
        }
        
        feedback = self.feedback_generator.generate_comprehensive_feedback(
            mock_grading_result,
            "What is AI?",
            "AI is artificial intelligence",
            "AI is the simulation of human intelligence in machines"
        )
        
        self.assertIn('feedback_components', feedback)
        self.assertIn('performance_level', feedback)

class TestHumanVerification(unittest.TestCase):
    """Test human verification system"""
    
    def setUp(self):
        self.human_verification = HumanVerificationManager()
        
    def test_human_verification_initialization(self):
        """Test human verification manager initializes correctly"""
        self.assertEqual(len(self.human_verification.review_queue), 0)
        self.assertEqual(len(self.human_verification.reviewers), 0)
        
    def test_flagging_criteria(self):
        """Test automatic flagging criteria"""
        # Test low confidence flagging
        low_confidence_result = {
            'breakdown': {
                'semantic_similarity': {'score': 40},
                'factual_accuracy': {'score': 30}
            }
        }
        
        should_flag, reasons = self.human_verification.should_flag_for_review(
            low_confidence_result, "Test question", "Test answer"
        )
        
        self.assertTrue(should_flag)
        self.assertIn(FlagReason.LOW_CONFIDENCE, reasons)
        
    def test_review_queue_management(self):
        """Test adding and managing review queue items"""
        review_id = self.human_verification.add_to_review_queue(
            'student1', 'exam1', 'q1', 'What is AI?',
            'AI is smart computers', 'AI is artificial intelligence',
            {'final_score': 60}, [FlagReason.LOW_CONFIDENCE]
        )
        
        self.assertIsNotNone(review_id)
        self.assertEqual(len(self.human_verification.review_queue), 1)
        
        # Test getting queue
        queue = self.human_verification.get_review_queue()
        self.assertEqual(len(queue), 1)
        
    def test_reviewer_assignment(self):
        """Test reviewer assignment"""
        # Add item to queue
        review_id = self.human_verification.add_to_review_queue(
            'student1', 'exam1', 'q1', 'What is AI?',
            'AI is smart computers', 'AI is artificial intelligence',
            {'final_score': 60}, [FlagReason.LOW_CONFIDENCE]
        )
        
        # Assign reviewer
        success = self.human_verification.assign_reviewer(review_id, 'reviewer1')
        self.assertTrue(success)
        
        # Check assignment
        item = self.human_verification.get_review_item(review_id)
        self.assertEqual(item['reviewer_id'], 'reviewer1')
        self.assertEqual(item['status'], ReviewStatus.IN_REVIEW.value)

class TestAnswerMapper(unittest.TestCase):
    """Test answer mapping system"""
    
    def setUp(self):
        self.answer_mapper = AnswerMapper()
        
    def test_answer_mapper_initialization(self):
        """Test answer mapper initializes with patterns"""
        self.assertGreater(len(self.answer_mapper.question_patterns), 0)
        self.assertGreater(len(self.answer_mapper.answer_patterns), 0)
        
    def test_text_preprocessing(self):
        """Test OCR text preprocessing"""
        test_text = "Question 1: What is AI?\nAnswer: AI is artificial intelligence."
        processed = self.answer_mapper._preprocess_text(test_text)
        
        self.assertIsInstance(processed, str)
        self.assertNotIn('\n', processed)
        
    def test_qa_extraction(self):
        """Test question-answer pair extraction"""
        test_text = """
        Question 1: What is photosynthesis?
        Answer: Photosynthesis is the process by which plants make food using sunlight.
        
        Question 2: What is gravity?
        Answer: Gravity is the force that attracts objects toward each other.
        """
        
        result = self.answer_mapper.extract_qa_pairs(test_text)
        
        self.assertIn('qa_pairs', result)
        self.assertIn('total_extracted', result)
        self.assertGreaterEqual(result['total_extracted'], 0)

class TestEducationalAssistant(unittest.TestCase):
    """Test educational assistant"""
    
    def setUp(self):
        self.educational_assistant = EducationalAssistant()
        
    def test_educational_assistant_initialization(self):
        """Test educational assistant initializes correctly"""
        self.assertIn('semantic_similarity', self.educational_assistant.grading_weights)
        self.assertIn('keyword_matching', self.educational_assistant.grading_weights)
        
    def test_context_analysis(self):
        """Test educational context analysis"""
        grading_message = "Please grade this answer"
        context = self.educational_assistant._analyze_educational_context(grading_message)
        self.assertEqual(context['type'], 'grading_request')
        
        question_message = "Generate questions about biology"
        context = self.educational_assistant._analyze_educational_context(question_message)
        self.assertEqual(context['type'], 'question_generation')
        
    def test_text_preprocessing(self):
        """Test text preprocessing"""
        test_text = "This is a TEST with SPECIAL characters!@#"
        processed = self.educational_assistant._preprocess_text(test_text)
        
        self.assertEqual(processed, "this is a test with special characters!")

class TestAnalyticsEngine(unittest.TestCase):
    """Test analytics engine"""
    
    def setUp(self):
        self.analytics_engine = AnalyticsEngine()
        
    def test_analytics_engine_initialization(self):
        """Test analytics engine initializes correctly"""
        self.assertEqual(len(self.analytics_engine.grading_history), 0)
        self.assertIsInstance(self.analytics_engine.student_performance, dict)
        
    def test_grading_event_recording(self):
        """Test recording grading events"""
        event_data = {
            'student_id': 'student1',
            'exam_id': 'exam1',
            'question_id': 'q1',
            'ai_score': 85,
            'confidence': 0.8
        }
        
        self.analytics_engine.record_grading_event(event_data)
        
        self.assertEqual(len(self.analytics_engine.grading_history), 1)
        self.assertIn('student1', self.analytics_engine.student_performance)
        
    def test_score_distribution_calculation(self):
        """Test score distribution calculation"""
        scores = [95, 85, 75, 65, 55, 45]
        distribution = self.analytics_engine._calculate_score_distribution(scores)
        
        self.assertIn('A (90-100)', distribution)
        self.assertIn('B (80-89)', distribution)
        self.assertIn('C (70-79)', distribution)
        self.assertIn('D (60-69)', distribution)
        self.assertIn('F (0-59)', distribution)
        
        self.assertEqual(distribution['A (90-100)'], 1)
        self.assertEqual(distribution['F (0-59)'], 2)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.ocr_manager = OCRManager()
        self.grading_engine = AdvancedGradingEngine()
        self.feedback_generator = FeedbackGenerator()
        self.human_verification = HumanVerificationManager()
        self.analytics_engine = AnalyticsEngine()
        
    def test_complete_grading_workflow(self):
        """Test complete grading workflow without models"""
        # Simulate OCR extraction
        ocr_text = "Question 1: What is AI? Answer: AI is artificial intelligence."
        
        # Simulate grading (without actual models)
        question = "What is AI?"
        student_answer = "AI is artificial intelligence"
        correct_answer = "AI is the simulation of human intelligence in machines"
        
        # Test that the workflow doesn't crash
        try:
            # This would normally use loaded models
            grading_result = {
                'final_score': 80,
                'max_score': 100,
                'percentage': 80,
                'breakdown': {
                    'semantic_similarity': {'score': 85, 'weight': 0.4},
                    'factual_accuracy': {'score': 75, 'weight': 0.3}
                }
            }
            
            # Generate feedback
            feedback = self.feedback_generator.generate_comprehensive_feedback(
                grading_result, question, student_answer, correct_answer
            )
            
            # Check for human verification
            should_flag, reasons = self.human_verification.should_flag_for_review(
                grading_result, question, student_answer
            )
            
            # Record analytics
            self.analytics_engine.record_grading_event({
                'student_id': 'test_student',
                'ai_score': grading_result['final_score'],
                'confidence': 0.8
            })
            
            # Verify workflow completed
            self.assertIn('feedback_components', feedback)
            self.assertIsInstance(should_flag, bool)
            self.assertEqual(len(self.analytics_engine.grading_history), 1)
            
        except Exception as e:
            self.fail(f"Complete workflow failed: {str(e)}")

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOCRModule,
        TestGradingEngine,
        TestFeedbackGenerator,
        TestHumanVerification,
        TestAnswerMapper,
        TestEducationalAssistant,
        TestAnalyticsEngine,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
