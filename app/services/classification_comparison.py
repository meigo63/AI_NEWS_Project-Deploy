"""
Classification Comparison Service

Integrates local ML model classification with Gemini API for secondary verification.
Implements comparison logic and applies decision rules based on result agreement.
"""

import logging
import time
from typing import Dict, Optional, Tuple
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ClassificationComparisonService:
    """
    Compares local ML model classification with Gemini API classification.
    
    Decision Logic:
    - If results match: Use local ML model result
    - If results conflict: Use Gemini API result
    """
    
    def __init__(self):
        """Initialize the comparison service with Gemini client."""
        try:
            self.gemini_service = GeminiService()
        except ValueError as e:
            logger.warning(f"Gemini API not configured: {e}")
            self.gemini_service = None
    
    def classify_with_comparison(
        self,
        article_text: str,
        model_result: str,
        model_confidence: float
    ) -> Dict:
        """
        Performs dual classification: local ML model + Gemini API.
        Applies comparison logic and returns structured response.
        
        Args:
            article_text: The news article text to classify
            model_result: Local ML model classification result ("real" or "fake")
            model_confidence: Confidence score from ML model (0.0-1.0)
        
        Returns:
            Dict containing:
                - original_text: The input article text
                - model_result: Local ML model classification
                - model_confidence: Local ML model confidence
                - gemini_result: Gemini API classification or error status
                - final_displayed_result: Result to display based on comparison logic
                - comparison_status: "matched" or "conflict"
                - processing_details: Metadata about the comparison
        """
        start_time = time.time()
        
        # Initialize response structure
        response = {
            'original_text': article_text,
            'model_result': model_result,
            'model_confidence': float(model_confidence),
            'gemini_result': None,
            'final_displayed_result': model_result,  # Default to ML model
            'comparison_status': 'model_only',
            'processing_details': {
                'gemini_available': self.gemini_service is not None,
                'gemini_error': None,
                'processing_time_ms': 0
            }
        }
        
        # If Gemini is not configured, return early with ML model result
        if not self.gemini_service:
            logger.info("Gemini service not configured, using ML model result only")
            response['processing_details']['processing_time_ms'] = (
                (time.time() - start_time) * 1000
            )
            return response
        
        # Call Gemini API for secondary verification
        try:
            gemini_result = self._get_gemini_classification(article_text)
            response['gemini_result'] = gemini_result
            
            # Apply comparison logic
            if gemini_result and gemini_result != 'ERROR':
                comparison_result = self._apply_comparison_logic(
                    model_result,
                    gemini_result
                )
                response['final_displayed_result'] = comparison_result['final_result']
                response['comparison_status'] = comparison_result['status']
            else:
                # Gemini failed, fall back to ML model
                response['comparison_status'] = 'model_only'
                response['gemini_result'] = 'ERROR'
                response['processing_details']['gemini_error'] = 'API call failed or returned invalid format'
        
        except Exception as e:
            # Handle unexpected errors gracefully
            logger.error(f"Classification comparison error: {str(e)}", exc_info=True)
            response['gemini_result'] = 'ERROR'
            response['comparison_status'] = 'model_only'
            response['processing_details']['gemini_error'] = str(e)
        
        # Record processing time
        response['processing_details']['processing_time_ms'] = (
            (time.time() - start_time) * 1000
        )
        
        return response
    
    def _get_gemini_classification(self, article_text: str) -> Optional[str]:
        """
        Calls Gemini API to classify article as 'real' or 'fake'.
        
        Args:
            article_text: The news article text
        
        Returns:
            Normalized classification string ("real" or "fake") or None if error
        """
        try:
            # Use existing Gemini service method
            result = self.gemini_service.analyze_article_comprehensive(article_text)
            
            if not result or 'verdict' not in result:
                logger.warning("Invalid Gemini response format")
                return None
            
            # Normalize Gemini verdict to match ML model format
            verdict = result['verdict'].strip().upper()
            normalized = self._normalize_classification(verdict)
            
            return normalized
        
        except Exception as e:
            logger.error(f"Gemini classification error: {str(e)}", exc_info=True)
            return None
    
    def _normalize_classification(self, classification: str) -> Optional[str]:
        """
        Normalizes classification output to standard format.
        
        Args:
            classification: Raw classification string from API or model
        
        Returns:
            Normalized string: "real" or "fake", or None if invalid
        """
        if not classification:
            return None
        
        normalized = classification.strip().lower()
        
        # Handle various possible input formats
        if normalized in ('real', 'fake'):
            return normalized
        
        # Map common variations
        real_variants = ('real', 'true', 'authentic', 'genuine', 'verified', 'legit')
        fake_variants = ('fake', 'false', 'fabricated', 'hoax', 'misleading', 'misinformation')
        
        if normalized in real_variants or 'real' in normalized:
            return 'real'
        elif normalized in fake_variants or 'fake' in normalized:
            return 'fake'
        
        # Could not normalize
        logger.warning(f"Could not normalize classification: {classification}")
        return None
    
    def _apply_comparison_logic(
        self,
        model_result: str,
        gemini_result: str
    ) -> Dict[str, str]:
        """
        Applies comparison logic to determine final result.
        
        Decision Rules:
        - If results match: Use local ML model result, status = "matched"
        - If results conflict: Use Gemini API result, status = "conflict"
        
        Args:
            model_result: Local ML model result ("real" or "fake")
            gemini_result: Gemini API result ("real" or "fake")
        
        Returns:
            Dict with:
                - final_result: Classification to display
                - status: "matched" or "conflict"
        """
        if not model_result or not gemini_result:
            return {
                'final_result': model_result or gemini_result,
                'status': 'model_only'
            }
        
        # Normalize both results for comparison
        model_normalized = self._normalize_classification(model_result)
        gemini_normalized = self._normalize_classification(gemini_result)
        
        if not model_normalized or not gemini_normalized:
            return {
                'final_result': model_result,
                'status': 'model_only'
            }
        
        # Apply decision logic
        if model_normalized == gemini_normalized:
            # Results agree: use ML model result
            return {
                'final_result': model_normalized,
                'status': 'matched'
            }
        else:
            # Results conflict: use Gemini result
            logger.info(
                f"Classification conflict detected. "
                f"ML: {model_normalized}, Gemini: {gemini_normalized}. "
                f"Using Gemini result."
            )
            return {
                'final_result': gemini_normalized,
                'status': 'conflict'
            }
