# Explainable AI (XAI) Implementation Guide

## Overview

This document describes the new Explainable AI pipeline integrated into the Fake News Detection system. The system automatically provides ML-powered predictions combined with Gemini AI explanations and performance metrics.

## Architecture

### Service-Based Design

The implementation uses a modular service architecture:

```
app/services/
├── metrics_service.py      - Performance tracking (CPU, inference time)
├── gemini_service.py       - Gemini API integration for explanations
├── insight_service.py      - Database persistence layer
└── xai_pipeline.py         - Main orchestrator
```

### Execution Flow

```
1. User clicks "Classify"
   ↓
2. ML Model Inference (fake/real prediction)
   ↓
3. Performance Tracking
   - Inference time (ms)
   - CPU usage (%)
   ↓
4. Conditional Gemini Verification
   - If confidence < 60% → Call Gemini
   - If confidence ≥ 60% → Use ML only
   ↓
5. Gemini Generates (if triggered)
   - Article summary
   - Decision explanation
   - Confidence interpretation
   ↓
6. Database Persistence
   - Store classification + explanations
   - Store metrics
   - Store verification status
   ↓
7. Display to User
   - Prediction + confidence
   - Explanation + summary
   - (Admin only) Metrics
```

## Components

### 1. MetricsTracker (metrics_service.py)

Lightweight performance monitoring:

```python
from app.services.metrics_service import MetricsTracker

tracker = MetricsTracker()
tracker.start()
# ... do inference ...
tracker.stop()

time_ms = tracker.get_processing_time_ms()
cpu_percent = tracker.get_cpu_usage_percent()
```

**Key Features:**
- Non-blocking CPU measurement (no interval delays)
- High-precision timing with `time.perf_counter()`
- Minimal overhead

### 2. GeminiService (gemini_service.py)

Conditional AI verification and explanation:

```python
from app.services.gemini_service import GeminiService

service = GeminiService()

# Check if verification should trigger
if service.should_verify(confidence_score=45.5):  # < 60%
    summary, explanation, conf_explanation = service.generate_explanation(
        article_text="...",
        prediction_label="fake",
        confidence_score=45.5
    )
```

**Gemini Prompt Template:**

```
You are an Explainable AI assistant for a Fake News Detection system.

Article:
"""
{ARTICLE_TEXT}
"""

ML Prediction:
- Label: {PREDICTION_LABEL}
- Confidence: {CONFIDENCE_SCORE}%

Tasks:
1. Explain why article was classified as {PREDICTION_LABEL}
2. Identify misleading patterns
3. Summarize article (4-6 bullets)
4. Explain confidence score meaning
5. If < 60%, explain uncertainty

Rules:
- No technical jargon
- Be neutral and factual
- Don't invent facts
- Keep human-readable
```

**Important:**
- Gemini NEVER overrides ML decision
- API failures are non-blocking
- Falls back gracefully to ML-only

### 3. InsightService (insight_service.py)

Database persistence with analytics:

```python
from app.services.insight_service import (
    save_classification_insight,
    get_analytics,
    get_all_insights
)

# Save classification
saved = save_classification_insight(
    user_id=123,
    article_text="...",
    prediction_label="fake",
    confidence_score=95.3,
    summary="...",
    explanation="...",
    verification_triggered=False,
    decision_source="ML_ONLY",
    processing_time_ms=245.3,
    cpu_usage_percent=12.5
)

# Get analytics
analytics = get_analytics()
# Returns: total, avg_confidence, avg_time, fake_ratio, etc.

# Get insights (admin)
insights = get_all_insights(limit=100)
```

### 4. XAIPipeline (xai_pipeline.py)

Main orchestrator that ties everything together:

```python
from app.services.xai_pipeline import XAIPipeline

pipeline = XAIPipeline()

result = pipeline.process_classification(
    article_text="...",
    predict_fn=predict_fake_news,  # Your ML function
    user_id=current_user.id
)

# Returns complete result:
# {
#   'prediction_label': 'fake',
#   'confidence_score': 95.3,
#   'summary': '...',
#   'explanation': '...',
#   'verification_triggered': False,
#   'decision_source': 'ML_ONLY',
#   'processing_time_ms': 245.3,
#   'cpu_usage_percent': 12.5
# }
```

## Database Schema

### ClassificationInsight Table

```python
class ClassificationInsight(db.Model):
    id                      # Primary key
    user_id                 # Foreign key to users
    
    # Input
    article_text            # Full article text
    
    # ML Results
    prediction_label        # 'REAL' or 'FAKE'
    confidence_score        # 0-100
    
    # Gemini Explanations (nullable)
    summary                 # Article summary from Gemini
    explanation             # Decision explanation
    confidence_explanation  # What confidence means
    
    # Pipeline Status
    verification_triggered  # Boolean: was Gemini called?
    decision_source         # 'ML_ONLY' or 'ML_GEMINI'
    
    # Performance Metrics
    processing_time_ms      # Inference time
    cpu_usage_percent       # CPU during inference
    
    created_at              # Timestamp
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# Key additions:
# - google-generativeai>=0.3.0
# - psutil>=5.9.0
```

### 2. Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env`:

```env
GEMINI_API_KEY=your_key_here
```

### 3. Create Database Table

Option A - Flask-Migrate:
```bash
flask db upgrade
```

Option B - Manual SQL:
```sql
CREATE TABLE classification_insights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    article_text LONGTEXT NOT NULL,
    prediction_label VARCHAR(10) NOT NULL,
    confidence_score FLOAT NOT NULL,
    summary LONGTEXT,
    explanation LONGTEXT,
    confidence_explanation LONGTEXT,
    verification_triggered BOOLEAN DEFAULT FALSE,
    decision_source VARCHAR(20) DEFAULT 'ML_ONLY',
    processing_time_ms FLOAT,
    cpu_usage_percent FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4. Test the Pipeline

```python
# In Flask shell
from app import create_app
from app.classification import predict_fake_news
from app.services.xai_pipeline import XAIPipeline

app = create_app()
with app.app_context():
    pipeline = XAIPipeline()
    
    result = pipeline.process_classification(
        article_text="Test article about climate change...",
        predict_fn=predict_fake_news,
        user_id=1
    )
    
    print(result)
```

## User Interface

### For Users

Classification page now automatically shows:

1. **Prediction** - REAL/FAKE label with confidence %
2. **Article Summary** - 4-6 bullet points (from Gemini)
3. **Explanation** - Why the article got this label
4. **Confidence Explanation** - What the score means

**Special Case:**
- If confidence < 60% → Shows "Uncertainty Verification Triggered"
- Gemini provides deeper analysis

### For Admins

New XAI Analytics Dashboard at `/admin/xai_analytics`:

**Metrics Cards:**
- Total classifications
- Average confidence
- Avg processing time
- Avg CPU usage

**Charts:**
- Confidence distribution (0-20%, 20-40%, etc.)
- Processing time trend (last 20)
- Fake/Real ratio

**Table:**
- Article preview
- Prediction
- Confidence
- Verification status
- Decision source (ML vs ML+Gemini)
- Metrics (time, CPU)

**Visibility:**
- Admins see: CPU, processing time, Gemini insights
- Users see: Prediction, summary, explanation

## Failure Handling

### Gemini API Fails

```
User still sees:
✓ ML prediction
✓ Confidence
✓ Basic UI

Missing:
✗ Explanation/summary
✗ Verification insights

Result:
- Logged as warning
- Marked as decision_source='ML_ONLY'
- Classification continues (non-blocking)
```

### Database Fails

```
- Classification still completes
- Metrics still shown
- Data not persisted
- Error logged
- User unaffected
```

### Metrics Calculation Fails

```
- Returns 0.0 for metrics
- Doesn't block classification
- Non-critical component
```

## Performance Considerations

### Inference Time
- Typical: 200-500ms (ML only)
- With Gemini: +2-5 seconds

### CPU Usage
- Light operations
- No full CPU exhaustion
- Measured per-process

### Database
- No heavy queries in pipeline
- Async logging optional
- Indexes on `user_id`, `created_at`

## Limitations & Future Work

### Current
- Gemini API has usage limits
- Processing visible to users
- No async execution

### Future
- Async Gemini calls
- Caching for similar articles
- Custom explanation prompts
- A/B testing different explanations

## API Endpoints

### For Users

```
POST /classify
- Form submission with article text
- Returns: HTML with results + XAI explanations

POST /api/xai_result (AJAX)
- Used by frontend to fetch explanations
- Returns: JSON with XAI pipeline output
```

### For Admins

```
GET /admin/xai_analytics
- Main dashboard

GET /admin/api/xai_metrics
- JSON metrics for charts
```

## Configuration

All configuration in `.env`:

```env
GEMINI_API_KEY=your_key
FLASK_SECRET_KEY=...
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=...
MYSQL_DB=news_ai_system
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Check `.env` file exists
- Check variable name spelling
- Restart Flask app

### Database table doesn't exist
- Run migration: `flask db upgrade`
- Or run manual SQL from MIGRATION.md

### Gemini explanations not showing
- Check API key validity
- Check internet connection
- Check logs for errors
- Classification still works (fallback)

### High processing time
- Normal: ~500ms for ML only
- With Gemini: ~2-5 seconds
- Monitor `/admin/xai_analytics`

## Support & Documentation

- Service docs: See docstrings in each service file
- Database schema: app/models.py
- Routes: app/classification.py, app/admin.py
- Templates: app/templates/classify.html, admin_xai_analytics.html
