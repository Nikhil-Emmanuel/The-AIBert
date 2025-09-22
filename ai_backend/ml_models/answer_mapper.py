"""
Answer Mapping System for extracting and mapping answers from OCR text
Uses regex and semantic matching to identify answer fields
"""

import re
import logging
import json
from typing import List, Dict, Any, Tuple
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnswerMapper:
    """Maps extracted OCR text to structured answer fields"""
    
    def __init__(self):
        self.question_patterns = [
            r'(?:question|q\.?)\s*(\d+)[\s\.:]*(.+?)(?=(?:question|q\.?)\s*\d+|$)',
            r'(\d+)[\s\.:]+(.+?)(?=\d+[\s\.:]+|$)',
            r'([a-z])\)?\s*(.+?)(?=[a-z]\)|$)',
            r'([ivx]+)[\s\.:]+(.+?)(?=[ivx]+[\s\.:]+|$)'
        ]
        
        self.answer_patterns = [
            r'(?:answer|ans\.?|a\.?)\s*(\d+)[\s\.:]*(.+?)(?=(?:answer|ans\.?|a\.?)\s*\d+|$)',
            r'(\d+)[\s\.:]*(.+?)(?=\d+[\s\.:]*|$)',
            r'([a-z])\)?\s*(.+?)(?=[a-z]\)|$)'
        ]
        
        # Common answer indicators
        self.answer_indicators = [
            'answer:', 'ans:', 'a:', 'solution:', 'sol:', 
            'response:', 'reply:', 'result:'
        ]
        
        # Question indicators
        self.question_indicators = [
            'question:', 'q:', 'problem:', 'prob:', 'query:', 'ask:'
        ]
        
    def extract_qa_pairs(self, ocr_text: str, expected_questions: List[str] = None) -> Dict[str, Any]:
        """Extract question-answer pairs from OCR text"""
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(ocr_text)
            
            # Try different extraction strategies
            qa_pairs = []
            
            # Strategy 1: Pattern-based extraction
            pattern_pairs = self._extract_with_patterns(cleaned_text)
            qa_pairs.extend(pattern_pairs)
            
            # Strategy 2: Semantic matching with expected questions
            if expected_questions:
                semantic_pairs = self._extract_with_semantic_matching(
                    cleaned_text, expected_questions
                )
                qa_pairs.extend(semantic_pairs)
            
            # Strategy 3: Structure-based extraction
            structure_pairs = self._extract_with_structure(cleaned_text)
            qa_pairs.extend(structure_pairs)
            
            # Merge and deduplicate results
            merged_pairs = self._merge_qa_pairs(qa_pairs)
            
            return {
                'qa_pairs': merged_pairs,
                'total_extracted': len(merged_pairs),
                'extraction_confidence': self._calculate_extraction_confidence(merged_pairs),
                'raw_text': ocr_text,
                'processed_text': cleaned_text
            }
            
        except Exception as e:
            logger.error(f"Error extracting QA pairs: {str(e)}")
            return {
                'qa_pairs': [],
                'total_extracted': 0,
                'extraction_confidence': 0.0,
                'error': str(e)
            }
            
    def _preprocess_text(self, text: str) -> str:
        """Preprocess OCR text for better extraction"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In some contexts
        
        # Normalize line breaks
        text = text.replace('\n', ' ')
        
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.\,\?\!\:\;\(\)\-\+\=]', '', text)
        
        return text.strip()
        
    def _extract_with_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract QA pairs using regex patterns"""
        qa_pairs = []
        
        try:
            # Look for question-answer patterns
            for q_pattern in self.question_patterns:
                q_matches = re.finditer(q_pattern, text, re.IGNORECASE | re.DOTALL)
                
                for q_match in q_matches:
                    question_num = q_match.group(1)
                    question_text = q_match.group(2).strip()
                    
                    # Look for corresponding answer
                    answer_text = self._find_answer_for_question(
                        text, question_num, q_match.end()
                    )
                    
                    if question_text and answer_text:
                        qa_pairs.append({
                            'question_number': question_num,
                            'question': question_text,
                            'answer': answer_text,
                            'extraction_method': 'pattern',
                            'confidence': 0.8
                        })
                        
        except Exception as e:
            logger.error(f"Error in pattern extraction: {str(e)}")
            
        return qa_pairs
        
    def _find_answer_for_question(self, text: str, question_num: str, start_pos: int) -> str:
        """Find answer text for a specific question"""
        try:
            # Look for answer patterns after the question
            remaining_text = text[start_pos:]
            
            # Try different answer patterns
            for a_pattern in self.answer_patterns:
                a_match = re.search(a_pattern, remaining_text, re.IGNORECASE)
                
                if a_match and a_match.group(1) == question_num:
                    return a_match.group(2).strip()
                    
            # If no numbered answer found, look for answer indicators
            for indicator in self.answer_indicators:
                pattern = rf'{re.escape(indicator)}\s*(.+?)(?=question|q\.|$)'
                match = re.search(pattern, remaining_text, re.IGNORECASE)
                
                if match:
                    return match.group(1).strip()
                    
            # Fallback: take text until next question
            next_q_pattern = r'(?:question|q\.?)\s*\d+'
            next_q_match = re.search(next_q_pattern, remaining_text, re.IGNORECASE)
            
            if next_q_match:
                return remaining_text[:next_q_match.start()].strip()
            else:
                # Take reasonable amount of text
                words = remaining_text.split()
                return ' '.join(words[:50])  # First 50 words
                
        except Exception as e:
            logger.error(f"Error finding answer: {str(e)}")
            return ""
            
    def _extract_with_semantic_matching(self, text: str, expected_questions: List[str]) -> List[Dict[str, Any]]:
        """Extract answers using semantic matching with expected questions"""
        qa_pairs = []
        
        try:
            # Split text into potential segments
            segments = self._segment_text(text)
            
            for i, expected_q in enumerate(expected_questions):
                best_match = None
                best_score = 0.0
                
                # Find best matching segment for this question
                for segment in segments:
                    similarity = self._calculate_similarity(expected_q, segment['text'])
                    
                    if similarity > best_score and similarity > 0.3:  # Threshold
                        best_score = similarity
                        best_match = segment
                        
                if best_match:
                    # Extract answer from the matched segment
                    answer = self._extract_answer_from_segment(
                        best_match['text'], expected_q
                    )
                    
                    if answer:
                        qa_pairs.append({
                            'question_number': str(i + 1),
                            'question': expected_q,
                            'answer': answer,
                            'extraction_method': 'semantic',
                            'confidence': best_score
                        })
                        
        except Exception as e:
            logger.error(f"Error in semantic extraction: {str(e)}")
            
        return qa_pairs
        
    def _segment_text(self, text: str) -> List[Dict[str, Any]]:
        """Segment text into logical parts"""
        segments = []
        
        try:
            # Split by common delimiters
            delimiters = [
                r'(?:question|q\.?)\s*\d+',
                r'(?:answer|ans\.?)\s*\d+',
                r'\d+[\s\.:]+',
                r'[a-z]\)\s*'
            ]
            
            # Create combined pattern
            combined_pattern = '|'.join(f'({pattern})' for pattern in delimiters)
            
            parts = re.split(combined_pattern, text, flags=re.IGNORECASE)
            
            for i, part in enumerate(parts):
                if part and part.strip():
                    segments.append({
                        'index': i,
                        'text': part.strip(),
                        'length': len(part.strip())
                    })
                    
        except Exception as e:
            logger.error(f"Error segmenting text: {str(e)}")
            # Fallback: split by sentences
            sentences = text.split('.')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    segments.append({
                        'index': i,
                        'text': sentence.strip(),
                        'length': len(sentence.strip())
                    })
                    
        return segments
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            # Use SequenceMatcher for basic similarity
            matcher = SequenceMatcher(None, text1.lower(), text2.lower())
            return matcher.ratio()
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
            
    def _extract_answer_from_segment(self, segment: str, question: str) -> str:
        """Extract answer from a text segment"""
        try:
            # Remove question text if present
            segment_clean = segment
            
            # Look for answer indicators
            for indicator in self.answer_indicators:
                pattern = rf'{re.escape(indicator)}\s*(.+)'
                match = re.search(pattern, segment_clean, re.IGNORECASE)
                
                if match:
                    return match.group(1).strip()
                    
            # If no indicator found, return the segment (might be the answer itself)
            return segment_clean.strip()
            
        except Exception as e:
            logger.error(f"Error extracting answer from segment: {str(e)}")
            return ""
            
    def _extract_with_structure(self, text: str) -> List[Dict[str, Any]]:
        """Extract QA pairs based on document structure"""
        qa_pairs = []
        
        try:
            # Look for numbered lists
            numbered_pattern = r'(\d+)[\s\.:]+(.+?)(?=\d+[\s\.:]+|$)'
            matches = re.finditer(numbered_pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                number = match.group(1)
                content = match.group(2).strip()
                
                # Try to split content into question and answer
                q_and_a = self._split_question_answer(content)
                
                if q_and_a:
                    qa_pairs.append({
                        'question_number': number,
                        'question': q_and_a['question'],
                        'answer': q_and_a['answer'],
                        'extraction_method': 'structure',
                        'confidence': 0.6
                    })
                    
        except Exception as e:
            logger.error(f"Error in structure extraction: {str(e)}")
            
        return qa_pairs
        
    def _split_question_answer(self, content: str) -> Dict[str, str]:
        """Split content into question and answer parts"""
        try:
            # Look for answer indicators
            for indicator in self.answer_indicators:
                if indicator in content.lower():
                    parts = content.lower().split(indicator, 1)
                    if len(parts) == 2:
                        return {
                            'question': parts[0].strip(),
                            'answer': parts[1].strip()
                        }
                        
            # If no clear split, assume first part is question, rest is answer
            sentences = content.split('.')
            if len(sentences) >= 2:
                return {
                    'question': sentences[0].strip(),
                    'answer': '.'.join(sentences[1:]).strip()
                }
                
            # Fallback: entire content as answer
            return {
                'question': '',
                'answer': content.strip()
            }
            
        except Exception as e:
            logger.error(f"Error splitting question-answer: {str(e)}")
            return None
            
    def _merge_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate QA pairs from different extraction methods"""
        try:
            # Group by question number
            grouped = defaultdict(list)
            
            for pair in qa_pairs:
                key = pair.get('question_number', 'unknown')
                grouped[key].append(pair)
                
            merged = []
            
            for question_num, pairs in grouped.items():
                if len(pairs) == 1:
                    merged.append(pairs[0])
                else:
                    # Merge multiple pairs for same question
                    best_pair = max(pairs, key=lambda x: x.get('confidence', 0))
                    
                    # Combine information from all pairs
                    combined_pair = best_pair.copy()
                    
                    # Use longest/best answer
                    all_answers = [p['answer'] for p in pairs if p['answer']]
                    if all_answers:
                        combined_pair['answer'] = max(all_answers, key=len)
                        
                    # Average confidence
                    confidences = [p.get('confidence', 0) for p in pairs]
                    combined_pair['confidence'] = sum(confidences) / len(confidences)
                    
                    merged.append(combined_pair)
                    
            # Sort by question number
            merged.sort(key=lambda x: self._extract_number(x.get('question_number', '0')))
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging QA pairs: {str(e)}")
            return qa_pairs
            
    def _extract_number(self, text: str) -> int:
        """Extract numeric value from text"""
        try:
            match = re.search(r'\d+', str(text))
            return int(match.group()) if match else 0
        except:
            return 0
            
    def _calculate_extraction_confidence(self, qa_pairs: List[Dict[str, Any]]) -> float:
        """Calculate overall extraction confidence"""
        try:
            if not qa_pairs:
                return 0.0
                
            confidences = [pair.get('confidence', 0) for pair in qa_pairs]
            return sum(confidences) / len(confidences)
            
        except Exception as e:
            logger.error(f"Error calculating extraction confidence: {str(e)}")
            return 0.0
            
    def map_to_expected_format(self, qa_pairs: List[Dict[str, Any]], 
                              expected_format: Dict[str, Any]) -> Dict[str, Any]:
        """Map extracted QA pairs to expected format"""
        try:
            mapped_data = {
                'student_id': expected_format.get('student_id', ''),
                'exam_id': expected_format.get('exam_id', ''),
                'answers': {},
                'metadata': {
                    'extraction_timestamp': '',
                    'total_questions': len(qa_pairs),
                    'extraction_confidence': self._calculate_extraction_confidence(qa_pairs)
                }
            }
            
            for pair in qa_pairs:
                question_num = pair.get('question_number', '')
                answer = pair.get('answer', '')
                confidence = pair.get('confidence', 0.0)
                
                mapped_data['answers'][question_num] = {
                    'answer_text': answer,
                    'confidence': confidence,
                    'extraction_method': pair.get('extraction_method', 'unknown')
                }
                
            return mapped_data
            
        except Exception as e:
            logger.error(f"Error mapping to expected format: {str(e)}")
            return {'error': str(e)}
