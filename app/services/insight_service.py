"""
Database persistence service for classification insights.
Handles storing and retrieving classification results with explanations.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from flask import current_app
from ..database import db

logger = logging.getLogger(__name__)


def save_classification_insight(
    user_id: Optional[int],
    article_text: str,
    prediction_label: str,
    confidence_score: float,
    summary: Optional[str] = None,
    explanation: Optional[str] = None,
    confidence_explanation: Optional[str] = None,
    verification_triggered: bool = False,
    decision_source: str = "ML_ONLY",
    processing_time_ms: float = 0.0,
    cpu_usage_percent: float = 0.0
) -> Optional[Dict[str, Any]]:
    """
    Save a classification insight to the database.
    
    Args:
        user_id: User ID (None for anonymous)
        article_text: The article text
        prediction_label: ML prediction (REAL/FAKE)
        confidence_score: Confidence score (0-1 or 0-100, will normalize)
        summary: Article summary from Gemini
        explanation: Detailed explanation from Gemini
        confidence_explanation: Confidence explanation from Gemini
        verification_triggered: Whether Gemini verification was used
        decision_source: "ML_ONLY" or "ML_GEMINI"
        processing_time_ms: Total processing time in milliseconds
        cpu_usage_percent: CPU usage percentage
    
    Returns:
        dict: Classification insight data or None if failed
    """
    try:
        # Normalize confidence score to 0-100 range if needed
        if confidence_score <= 1.0:
            confidence_score = confidence_score * 100
        
        # Import here to avoid circular imports
        from ..models import ClassificationInsight
        
        insight = ClassificationInsight(
            user_id=user_id,
            article_text=article_text,
            prediction_label=prediction_label,
            confidence_score=float(confidence_score),
            summary=summary,
            explanation=explanation,
            confidence_explanation=confidence_explanation,
            verification_triggered=verification_triggered,
            decision_source=decision_source,
            processing_time_ms=float(processing_time_ms),
            cpu_usage_percent=float(cpu_usage_percent),
            created_at=datetime.utcnow()
        )
        
        db.session.add(insight)
        db.session.commit()
        
        return {
            'id': insight.id,
            'prediction_label': insight.prediction_label,
            'confidence_score': insight.confidence_score,
            'summary': insight.summary,
            'explanation': insight.explanation,
            'confidence_explanation': insight.confidence_explanation,
            'verification_triggered': insight.verification_triggered,
            'decision_source': insight.decision_source,
            'processing_time_ms': insight.processing_time_ms,
            'cpu_usage_percent': insight.cpu_usage_percent,
            'created_at': insight.created_at.isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Failed to save classification insight: {str(e)}")
        # Rollback the session to prevent PendingRollbackError
        try:
            db.session.rollback()
        except Exception as rollback_err:
            logger.error(f"Error rolling back session: {str(rollback_err)}")
        return None



def get_user_insights(user_id: int, limit: int = 50) -> list:
    """
    Get classification insights for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of insights to return
    
    Returns:
        list: List of classification insights
    """
    try:
        from ..models import ClassificationInsight
        
        insights = ClassificationInsight.query.filter_by(
            user_id=user_id
        ).order_by(
            ClassificationInsight.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': i.id,
                'article_text': i.article_text,
                'prediction_label': i.prediction_label,
                'confidence_score': i.confidence_score,
                'summary': i.summary,
                'explanation': i.explanation,
                'confidence_explanation': i.confidence_explanation,
                'verification_triggered': i.verification_triggered,
                'decision_source': i.decision_source,
                'processing_time_ms': i.processing_time_ms,
                'cpu_usage_percent': i.cpu_usage_percent,
                'created_at': i.created_at.isoformat()
            }
            for i in insights
        ]
        
    except Exception as e:
        logger.exception(f"Failed to get user insights: {str(e)}")
        return []


def get_all_insights(limit: int = 100) -> list:
    """
    Get all classification insights (admin only).
    
    Args:
        limit: Maximum number of insights to return
    
    Returns:
        list: List of all classification insights
    """
    try:
        from ..models import ClassificationInsight
        
        insights = ClassificationInsight.query.order_by(
            ClassificationInsight.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': i.id,
                'user_id': i.user_id,
                'article_text': i.article_text[:100] + '...' if len(i.article_text) > 100 else i.article_text,
                'prediction_label': i.prediction_label,
                'confidence_score': i.confidence_score,
                'summary': i.summary,
                'explanation': i.explanation,
                'confidence_explanation': i.confidence_explanation,
                'verification_triggered': i.verification_triggered,
                'decision_source': i.decision_source,
                'processing_time_ms': i.processing_time_ms,
                'cpu_usage_percent': i.cpu_usage_percent,
                'created_at': i.created_at.isoformat()
            }
            for i in insights
        ]
        
    except Exception as e:
        logger.exception(f"Failed to get all insights: {str(e)}")
        return []


def get_analytics() -> dict:
    """
    Get analytics for admin dashboard.
    
    Returns:
        dict: Analytics metrics
    """
    try:
        from ..models import ClassificationInsight
        from sqlalchemy import func
        
        total_classifications = ClassificationInsight.query.count()
        
        if total_classifications == 0:
            return {
                'total_classifications': 0,
                'avg_confidence': 0.0,
                'avg_processing_time_ms': 0.0,
                'avg_cpu_usage_percent': 0.0,
                'fake_count': 0,
                'real_count': 0,
                'verification_count': 0,
                'fake_ratio': 0.0
            }
        
        # Get averages
        avg_metrics = db.session.query(
            func.avg(ClassificationInsight.confidence_score).label('avg_confidence'),
            func.avg(ClassificationInsight.processing_time_ms).label('avg_processing_time'),
            func.avg(ClassificationInsight.cpu_usage_percent).label('avg_cpu_usage')
        ).first()
        
        # Get label counts
        fake_count = ClassificationInsight.query.filter_by(
            prediction_label='fake'
        ).count()
        real_count = ClassificationInsight.query.filter_by(
            prediction_label='real'
        ).count()
        
        # Get verification count
        verification_count = ClassificationInsight.query.filter_by(
            verification_triggered=True
        ).count()
        
        fake_ratio = (fake_count / total_classifications * 100) if total_classifications > 0 else 0
        
        return {
            'total_classifications': total_classifications,
            'avg_confidence': float(avg_metrics.avg_confidence or 0.0),
            'avg_processing_time_ms': float(avg_metrics.avg_processing_time or 0.0),
            'avg_cpu_usage_percent': float(avg_metrics.avg_cpu_usage or 0.0),
            'fake_count': fake_count,
            'real_count': real_count,
            'verification_count': verification_count,
            'fake_ratio': round(fake_ratio, 2)
        }
        
    except Exception as e:
        logger.exception(f"Failed to get analytics: {str(e)}")
        return {}
