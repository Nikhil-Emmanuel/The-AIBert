"""
Enhanced AI Assistant Backend
Integrates AIML, Machine Learning, and Educational AI capabilities
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import aiml
import os
import json
import logging
from datetime import datetime
import pickle
from pathlib import Path

# Import custom modules
from ml_models.intent_classifier import IntentClassifier
from ml_models.sentiment_analyzer import SentimentAnalyzer
from ml_models.educational_assistant import EducationalAssistant
from ml_models.ocr_module import OCRManager
from ml_models.grading_engine import AdvancedGradingEngine
from ml_models.feedback_generator import FeedbackGenerator
from ml_models.human_verification import HumanVerificationManager
from ml_models.answer_mapper import AnswerMapper
from aiml_engine.aiml_manager import AIMLManager
from utils.conversation_manager import ConversationManager
from utils.training_manager import TrainingManager
from analytics.analytics_engine import AnalyticsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize AI components
aiml_manager = AIMLManager()
intent_classifier = IntentClassifier()
sentiment_analyzer = SentimentAnalyzer()
educational_assistant = EducationalAssistant()
ocr_manager = OCRManager()
grading_engine = AdvancedGradingEngine()
feedback_generator = FeedbackGenerator()
human_verification = HumanVerificationManager()
answer_mapper = AnswerMapper()
conversation_manager = ConversationManager()
training_manager = TrainingManager()
analytics_engine = AnalyticsEngine()

# Global variables for model states
models_loaded = False

def initialize_models():
    """Initialize all AI models and AIML brain"""
    global models_loaded
    try:
        logger.info("Initializing AI models...")
        
        # Load AIML brain
        aiml_manager.load_brain()
        
        # Load ML models
        intent_classifier.load_model()
        sentiment_analyzer.load_model()
        educational_assistant.load_model()
        ocr_manager.load_models()
        grading_engine.load_models()
        feedback_generator.load_model()
        
        models_loaded = True
        logger.info("All AI models initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        models_loaded = False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for AI assistant"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        context = data.get('context', {})
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Analyze user intent
        intent_result = intent_classifier.predict(user_message)
        
        # Analyze sentiment
        sentiment_result = sentiment_analyzer.analyze(user_message)
        
        # Get conversation context
        conversation_context = conversation_manager.get_context(user_id)
        
        # Process with AIML
        aiml_response = aiml_manager.respond(user_message, user_id)
        
        # Enhance response with educational AI if needed
        if intent_result['intent'] in ['educational_query', 'quiz_request', 'explanation']:
            enhanced_response = educational_assistant.enhance_response(
                user_message, aiml_response, context
            )
        else:
            enhanced_response = aiml_response
        
        # Update conversation context
        conversation_manager.update_context(user_id, {
            'user_message': user_message,
            'ai_response': enhanced_response,
            'intent': intent_result,
            'sentiment': sentiment_result,
            'timestamp': datetime.now().isoformat()
        })
        
        response = {
            'response': enhanced_response,
            'intent': intent_result,
            'sentiment': sentiment_result,
            'confidence': intent_result.get('confidence', 0.0),
            'context_updated': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/train', methods=['POST'])
def train_models():
    """Endpoint to trigger model training"""
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'all')
        training_data_path = data.get('training_data_path', None)
        
        result = training_manager.train_models(model_type, training_data_path)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in training endpoint: {str(e)}")
        return jsonify({'error': 'Training failed'}), 500

@app.route('/models/status', methods=['GET'])
def models_status():
    """Get status of all AI models"""
    try:
        status = {
            'aiml_brain_loaded': aiml_manager.is_loaded(),
            'intent_classifier_loaded': intent_classifier.is_loaded(),
            'sentiment_analyzer_loaded': sentiment_analyzer.is_loaded(),
            'educational_assistant_loaded': educational_assistant.is_loaded(),
            'ocr_models_loaded': ocr_manager.get_status(),
            'models_initialized': models_loaded
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        return jsonify({'error': 'Failed to get model status'}), 500

@app.route('/conversation/history/<user_id>', methods=['GET'])
def get_conversation_history(user_id):
    """Get conversation history for a user"""
    try:
        history = conversation_manager.get_history(user_id)
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({'error': 'Failed to get conversation history'}), 500

@app.route('/aiml/reload', methods=['POST'])
def reload_aiml():
    """Reload AIML brain"""
    try:
        aiml_manager.reload_brain()
        return jsonify({'message': 'AIML brain reloaded successfully'})
        
    except Exception as e:
        logger.error(f"Error reloading AIML brain: {str(e)}")
        return jsonify({'error': 'Failed to reload AIML brain'}), 500

@app.route('/ocr/process', methods=['POST'])
def process_ocr():
    """Process image with OCR for handwritten text extraction"""
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image']
        document_type = data.get('document_type', 'mixed')  # handwritten, printed, or mixed

        # Process with OCR
        result = ocr_manager.process_document(image_data, document_type)

        if 'error' in result:
            return jsonify({'error': result['error']}), 500

        return jsonify({
            'success': True,
            'result': result,
            'processed_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        return jsonify({'error': 'Failed to process OCR'}), 500

@app.route('/grading/evaluate', methods=['POST'])
def evaluate_answer():
    """Evaluate student answer using AI grading"""
    try:
        data = request.get_json()

        required_fields = ['question', 'student_answer', 'correct_answer']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        question = data['question']
        student_answer = data['student_answer']
        correct_answer = data['correct_answer']
        max_score = data.get('max_score', 100)

        # Grade the answer
        grading_result = educational_assistant.grade_answer(
            question, student_answer, correct_answer, max_score
        )

        return jsonify({
            'success': True,
            'grading_result': grading_result,
            'evaluated_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        return jsonify({'error': 'Failed to evaluate answer'}), 500

@app.route('/grading/comprehensive', methods=['POST'])
def comprehensive_grading():
    """Comprehensive grading with advanced features and human verification"""
    try:
        data = request.get_json()

        required_fields = ['question', 'student_answer', 'correct_answer']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        question = data['question']
        student_answer = data['student_answer']
        correct_answer = data['correct_answer']
        max_score = data.get('max_score', 100)
        student_id = data.get('student_id', 'anonymous')
        exam_id = data.get('exam_id', 'manual')
        question_id = data.get('question_id', 'manual')

        # Use advanced grading engine
        grading_result = grading_engine.grade_answer(
            question, student_answer, correct_answer, max_score=max_score
        )

        # Generate comprehensive feedback
        feedback_result = feedback_generator.generate_comprehensive_feedback(
            grading_result, question, student_answer, correct_answer
        )

        # Check if should be flagged for human review
        should_flag, flag_reasons = human_verification.should_flag_for_review(
            grading_result, question, student_answer
        )

        review_id = None
        if should_flag:
            review_id = human_verification.add_to_review_queue(
                student_id, exam_id, question_id, question,
                student_answer, correct_answer, grading_result, flag_reasons
            )

        # Record for analytics
        analytics_engine.record_grading_event({
            'student_id': student_id,
            'exam_id': exam_id,
            'question_id': question_id,
            'ai_score': grading_result.get('final_score'),
            'confidence': grading_result.get('breakdown', {}),
            'grading_method': 'comprehensive',
            'flagged_for_review': should_flag,
            'processing_time': 0  # Would be calculated in real implementation
        })

        return jsonify({
            'success': True,
            'grading_result': grading_result,
            'feedback': feedback_result,
            'flagged_for_review': should_flag,
            'review_id': review_id,
            'flag_reasons': [reason.value for reason in flag_reasons] if flag_reasons else [],
            'processed_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in comprehensive grading: {str(e)}")
        return jsonify({'error': 'Failed to process comprehensive grading'}), 500

@app.route('/ocr/extract_answers', methods=['POST'])
def extract_answers():
    """Extract and map answers from OCR text"""
    try:
        data = request.get_json()

        if not data or 'ocr_text' not in data:
            return jsonify({'error': 'No OCR text provided'}), 400

        ocr_text = data['ocr_text']
        expected_questions = data.get('expected_questions', [])

        # Extract Q&A pairs using answer mapper
        extraction_result = answer_mapper.extract_qa_pairs(ocr_text, expected_questions)

        return jsonify({
            'success': True,
            'extraction_result': extraction_result,
            'processed_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error extracting answers: {str(e)}")
        return jsonify({'error': 'Failed to extract answers'}), 500

if __name__ == '__main__':
    # Initialize models on startup
    initialize_models()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('AI_BACKEND_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )
