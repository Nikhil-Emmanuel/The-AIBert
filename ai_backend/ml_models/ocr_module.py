"""
OCR Module for Handwritten Exam Script Recognition
Implements deep learning-based OCR using CNN/TROCR models
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import logging
import os
import base64
from io import BytesIO
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class HandwritingOCR:
    """OCR module for handwritten text recognition"""
    
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = "microsoft/trocr-base-handwritten"
        self.loaded = False
        
    def load_model(self):
        """Load TrOCR model for handwritten text recognition"""
        try:
            logger.info("Loading TrOCR model for handwritten text...")
            
            # Load processor and model
            self.processor = TrOCRProcessor.from_pretrained(self.model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            logger.info("TrOCR model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading TrOCR model: {str(e)}")
            self.loaded = False
            
    def preprocess_image(self, image_data):
        """Preprocess image for OCR"""
        try:
            # Handle different input formats
            if isinstance(image_data, str):
                # Base64 encoded image
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
            elif isinstance(image_data, bytes):
                image = Image.open(BytesIO(image_data))
            else:
                image = image_data
                
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Apply image preprocessing
            img_array = self._enhance_image(img_array)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(img_array)
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return None
            
    def _enhance_image(self, img_array):
        """Enhance image quality for better OCR"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2RGB)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing image: {str(e)}")
            return img_array
            
    def extract_text_regions(self, image):
        """Extract individual text regions from the image"""
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Find contours to identify text regions
            contours, _ = cv2.findContours(
                gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            text_regions = []
            for contour in contours:
                # Filter contours by area
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Extract region
                    region = image.crop((x, y, x + w, y + h))
                    text_regions.append({
                        'region': region,
                        'bbox': (x, y, w, h),
                        'area': area
                    })
            
            # Sort regions by position (top to bottom, left to right)
            text_regions.sort(key=lambda r: (r['bbox'][1], r['bbox'][0]))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Error extracting text regions: {str(e)}")
            return []
            
    def recognize_text(self, image):
        """Recognize text from preprocessed image"""
        try:
            if not self.loaded:
                logger.error("OCR model not loaded")
                return ""
                
            # Process image
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generate text
            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values)
                generated_text = self.processor.batch_decode(
                    generated_ids, skip_special_tokens=True
                )[0]
                
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Error recognizing text: {str(e)}")
            return ""
            
    def process_exam_script(self, image_data):
        """Process complete exam script and extract all text"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            if processed_image is None:
                return {"error": "Failed to preprocess image"}
                
            # Extract text regions
            text_regions = self.extract_text_regions(processed_image)
            
            # Recognize text from each region
            extracted_texts = []
            for i, region_data in enumerate(text_regions):
                region = region_data['region']
                bbox = region_data['bbox']
                
                # Recognize text
                text = self.recognize_text(region)
                
                if text:
                    extracted_texts.append({
                        'region_id': i,
                        'text': text,
                        'bbox': bbox,
                        'confidence': self._calculate_confidence(text)
                    })
                    
            # Also process the full image
            full_text = self.recognize_text(processed_image)
            
            return {
                'full_text': full_text,
                'regions': extracted_texts,
                'total_regions': len(text_regions),
                'processed_regions': len(extracted_texts)
            }
            
        except Exception as e:
            logger.error(f"Error processing exam script: {str(e)}")
            return {"error": str(e)}
            
    def _calculate_confidence(self, text):
        """Calculate confidence score for recognized text"""
        try:
            # Simple confidence calculation based on text characteristics
            if not text:
                return 0.0
                
            # Factors that indicate good recognition
            has_letters = any(c.isalpha() for c in text)
            has_numbers = any(c.isdigit() for c in text)
            has_spaces = ' ' in text
            length_factor = min(len(text) / 10, 1.0)  # Longer text generally more reliable
            
            confidence = 0.0
            if has_letters:
                confidence += 0.4
            if has_numbers:
                confidence += 0.2
            if has_spaces:
                confidence += 0.2
            confidence += length_factor * 0.2
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
            
    def is_loaded(self):
        """Check if model is loaded"""
        return self.loaded
        
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'loaded': self.loaded
        }

class PrintedTextOCR:
    """OCR module for printed text recognition using Tesseract"""
    
    def __init__(self):
        self.loaded = False
        
    def load_model(self):
        """Load Tesseract OCR"""
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.loaded = True
            logger.info("Tesseract OCR loaded successfully")
        except ImportError:
            logger.error("pytesseract not installed. Install with: pip install pytesseract")
            self.loaded = False
            
    def recognize_text(self, image):
        """Recognize printed text from image"""
        try:
            if not self.loaded:
                return ""
                
            # Convert PIL to OpenCV format if needed
            if hasattr(image, 'mode'):
                img_array = np.array(image)
            else:
                img_array = image
                
            # Use Tesseract to extract text
            text = self.pytesseract.image_to_string(img_array)
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error with Tesseract OCR: {str(e)}")
            return ""
            
    def is_loaded(self):
        return self.loaded

class OCRManager:
    """Manager class for different OCR modules"""
    
    def __init__(self):
        self.handwriting_ocr = HandwritingOCR()
        self.printed_ocr = PrintedTextOCR()
        
    def load_models(self):
        """Load all OCR models"""
        self.handwriting_ocr.load_model()
        self.printed_ocr.load_model()
        
    def process_document(self, image_data, document_type='mixed'):
        """Process document with appropriate OCR method"""
        try:
            if document_type == 'handwritten':
                return self.handwriting_ocr.process_exam_script(image_data)
            elif document_type == 'printed':
                processed_image = self.handwriting_ocr.preprocess_image(image_data)
                text = self.printed_ocr.recognize_text(processed_image)
                return {'full_text': text, 'regions': [], 'type': 'printed'}
            else:  # mixed
                # Try both methods and combine results
                handwritten_result = self.handwriting_ocr.process_exam_script(image_data)
                processed_image = self.handwriting_ocr.preprocess_image(image_data)
                printed_text = self.printed_ocr.recognize_text(processed_image)
                
                return {
                    'handwritten_result': handwritten_result,
                    'printed_text': printed_text,
                    'type': 'mixed'
                }
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {"error": str(e)}
            
    def get_status(self):
        """Get status of all OCR modules"""
        return {
            'handwriting_ocr_loaded': self.handwriting_ocr.is_loaded(),
            'printed_ocr_loaded': self.printed_ocr.is_loaded()
        }
