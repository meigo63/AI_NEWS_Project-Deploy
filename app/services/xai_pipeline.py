"""
Explainable AI Pipeline Service
Orchestrates ML classification, performance tracking, and Gemini explanations.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from ..services.metrics_service import MetricsTracker
from ..services.gemini_service import GeminiService
from ..services.insight_service import save_classification_insight

logger = logging.getLogger(__name__)


class XAIPipeline:
    """Main orchestrator for the Explainable AI pipeline."""
    
    def __init__(self):
        """Initialize the XAI pipeline."""
        self.gemini_service = None
        try:
            self.gemini_service = GeminiService()
        except ValueError as e:
            logger.warning(f"Gemini service not initialized: {str(e)}")
    
    def process_classification(
        self,
        article_text: str,
        predict_fn,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete XAI pipeline: ML -> Metrics -> Gemini -> DB.
        
        Args:
            article_text: The article to classify
            predict_fn: Function that returns (label, confidence) tuple
            user_id: Optional user ID for database persistence
        
        Returns:
            dict: Complete classification result with explanations and metrics
        """
        result = {
            'prediction_label': None,
            'confidence_score': 0.0,
            'summary': None,
            'explanation': None,
            'confidence_explanation': None,
            'verification_triggered': False,
            'decision_source': 'ML_ONLY',
            'processing_time_ms': 0.0,
            'cpu_usage_percent': 0.0,
            'error': None
        }
        
        try:
            # Step 1: Start performance tracking
            metrics = MetricsTracker()
            metrics.start()
            
            # Step 2: Run ML model
            label, confidence = predict_fn(article_text)
            
            # Normalize confidence to 0-100 scale
            if confidence is not None and confidence <= 1.0:
                confidence = confidence * 100
            
            result['prediction_label'] = label
            result['confidence_score'] = float(confidence or 0.0)
            
            # Step 3: Stop performance tracking
            metrics.stop()
            result['processing_time_ms'] = metrics.get_processing_time_ms()
            result['cpu_usage_percent'] = metrics.get_cpu_usage_percent()
            
            # Step 4: Determine if Gemini verification is needed
            should_verify = (
                self.gemini_service is not None and 
                confidence is not None and 
                confidence < 60
            )
            
            result['verification_triggered'] = should_verify
            
            # Step 5: Call Gemini for explanations (if available)
            if self.gemini_service is not None:
                try:
                    summary, explanation, conf_explanation = self.gemini_service.generate_explanation(
                        article_text=article_text,
                        prediction_label=label,
                        confidence_score=float(confidence or 0.0)
                    )
                    
                    if summary is not None:
                        result['summary'] = summary
                        result['explanation'] = explanation
                        result['confidence_explanation'] = conf_explanation
                        result['decision_source'] = 'ML_GEMINI'
                
                except Exception as e:
                    logger.warning(f"Gemini explanation failed (non-blocking): {str(e)}")
                    # Continue without Gemini explanations
            
            # Step 6: Save to database (if user is authenticated)
            if user_id is not None:
                try:
                    saved = save_classification_insight(
                        user_id=user_id,
                        article_text=article_text,
                        prediction_label=label,
                        confidence_score=float(confidence or 0.0),
                        summary=result['summary'],
                        explanation=result['explanation'],
                        confidence_explanation=result['confidence_explanation'],
                        verification_triggered=result['verification_triggered'],
                        decision_source=result['decision_source'],
                        processing_time_ms=result['processing_time_ms'],
                        cpu_usage_percent=result['cpu_usage_percent']
                    )
                    if saved:
                        result['insight_id'] = saved.get('id')
                except Exception as e:
                    logger.warning(f"Failed to save insight to database: {str(e)}")
            
        except Exception as e:
            logger.exception(f"XAI pipeline error: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    @staticmethod
    def format_for_display(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the result for frontend display.
        
        Args:
            result: Raw result from process_classification
        
        Returns:
            dict: Formatted result for UI
        """
        return {
            'prediction_label': result.get('prediction_label'),
            'confidence_score': round(result.get('confidence_score', 0.0), 2),
            'confidence_percent': f"{result.get('confidence_score', 0.0):.1f}%",
            'summary': result.get('summary'),
            'explanation': result.get('explanation'),
            'confidence_explanation': result.get('confidence_explanation'),
            'verification_triggered': result.get('verification_triggered', False),
            'decision_source': result.get('decision_source'),
            'processing_time_ms': round(result.get('processing_time_ms', 0.0), 2),
            'cpu_usage_percent': round(result.get('cpu_usage_percent', 0.0), 2),
            'error': result.get('error')
        }
