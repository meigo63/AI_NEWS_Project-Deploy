# Gemini API Classification Integration Guide

## Overview

The News Classification System now integrates Google's Gemini API as a secondary AI classifier. The system compares the local ML model predictions with Gemini API results and applies intelligent decision logic to determine the final classification.

## Architecture

### Components

1. **Local ML Model**: BERT-based transformer model for fake news classification
2. **Gemini Service**: (`app/services/gemini_service.py`) - Handles Gemini API communication
3. **Classification Comparison Service**: (`app/services/classification_comparison.py`) - Compares results and applies decision logic
4. **API Endpoint**: `/api/classify` - Unified endpoint for dual classification

### Decision Logic

The system uses the following rules to determine the final result:

```
IF model_result == gemini_result:
    → Use local ML model result (MATCHED)
ELSE IF model_result != gemini_result:
    → Use Gemini API result (CONFLICT)
ELSE IF gemini_api_fails:
    → Use local ML model result with fallback flag (MODEL_ONLY)
```

## Setup

### 1. Environment Variables

Add the Gemini API key to your `.env` file:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 2. Database Migration

The `ArticleResult` model now includes three new columns:

```python
gemini_result = db.Column(db.String(16), nullable=True)
final_displayed_result = db.Column(db.String(16), nullable=True)
comparison_status = db.Column(db.String(20), nullable=True)
```

Create and apply a migration:

```bash
flask db migrate -m "Add Gemini integration fields to ArticleResult"
flask db upgrade
```

### 3. Dependencies

The required dependencies are already in `requirements.txt`:

```
google-genai>=0.3.0
transformers>=4.30.0
torch>=1.13.0
```

## API Usage

### Endpoint: POST `/api/classify`

Classifies a news article using both ML model and Gemini API.

#### Request

```bash
curl -X POST http://localhost:5000/api/classify \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your news article text here..."}'
```

#### Request Body

```json
{
  "text": "Article content to classify..."
}
```

#### Response

```json
{
  "original_text": "Article content to classify...",
  "category": "Politics",
  "category_confidence": 0.95,
  "model_result": "fake",
  "model_confidence": 0.87,
  "gemini_result": "fake",
  "final_displayed_result": "fake",
  "comparison_status": "matched",
  "processing_details": {
    "gemini_available": true,
    "gemini_error": null,
    "processing_time_ms": 1234.56
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `original_text` | string | The input article text |
| `category` | string | Predicted news category (Politics, Sports, etc.) |
| `category_confidence` | float | Confidence score for category (0.0-1.0) |
| `model_result` | string | Local ML model classification ("real" or "fake") |
| `model_confidence` | float | ML model confidence score (0.0-1.0) |
| `gemini_result` | string | Gemini API classification ("real", "fake", or "ERROR") |
| `final_displayed_result` | string | Final result to display to user |
| `comparison_status` | string | One of: "matched", "conflict", "model_only" |
| `processing_details` | object | Metadata about processing |

#### Comparison Status Values

- **`matched`**: Both models agree → uses ML model result
- **`conflict`**: Models disagree → uses Gemini result
- **`model_only`**: Gemini unavailable/failed → uses ML model only

## Python Usage Example

### Using the Comparison Service Directly

```python
from app.services.classification_comparison import ClassificationComparisonService

# Initialize the service
comparison_service = ClassificationComparisonService()

# Classify an article
article_text = "Breaking news about the election..."
ml_result = "fake"
ml_confidence = 0.85

result = comparison_service.classify_with_comparison(
    article_text=article_text,
    model_result=ml_result,
    model_confidence=ml_confidence
)

# Access results
print(f"ML Result: {result['model_result']}")
print(f"Gemini Result: {result['gemini_result']}")
print(f"Final Result: {result['final_displayed_result']}")
print(f"Comparison Status: {result['comparison_status']}")
print(f"Processing Time: {result['processing_details']['processing_time_ms']}ms")
```

### Using the API from Python

```python
import requests

# Authenticate
login_response = requests.post(
    'http://localhost:5000/api/login',
    json={'email': 'user@example.com', 'password': 'password'}
)
token = login_response.json()['token']

# Classify article
headers = {'Authorization': f'Bearer {token}'}
article_response = requests.post(
    'http://localhost:5000/api/classify',
    headers=headers,
    json={'text': 'Your news article...'}
)

data = article_response.json()
print(f"Final result: {data['final_displayed_result']}")
print(f"Models agreed: {data['comparison_status'] == 'matched'}")
```

## Error Handling

The system gracefully handles various failure scenarios:

### Gemini API Timeout

```json
{
  "gemini_result": "ERROR",
  "final_displayed_result": "real",
  "comparison_status": "model_only",
  "processing_details": {
    "gemini_available": true,
    "gemini_error": "API timeout",
    "processing_time_ms": 5000
  }
}
```

### Invalid API Key

```json
{
  "gemini_result": "ERROR",
  "final_displayed_result": "fake",
  "comparison_status": "model_only",
  "processing_details": {
    "gemini_available": false,
    "gemini_error": "GEMINI_API_KEY not found in environment variables",
    "processing_time_ms": 50
  }
}
```

### Unexpected Response Format

```json
{
  "gemini_result": "ERROR",
  "final_displayed_result": "real",
  "comparison_status": "model_only",
  "processing_details": {
    "gemini_available": true,
    "gemini_error": "Invalid Gemini response format",
    "processing_time_ms": 800
  }
}
```

## Code Architecture

### ClassificationComparisonService

Located in `app/services/classification_comparison.py`

**Key Methods:**

- `classify_with_comparison(article_text, model_result, model_confidence)`: Main method that runs dual classification
- `_get_gemini_classification(article_text)`: Calls Gemini API and normalizes result
- `_normalize_classification(classification)`: Converts various formats to standard "real"/"fake"
- `_apply_comparison_logic(model_result, gemini_result)`: Applies decision rules

**Features:**

- Automatic response normalization (handles "real", "fake", "authentic", "hoax", etc.)
- Graceful fallback to ML model if Gemini fails
- Comprehensive error logging
- Processing time tracking

### Integration Points

1. **`app/api.py`**: `/api/classify` endpoint imports and uses `ClassificationComparisonService`
2. **`app/models.py`**: `ArticleResult` model stores comparison results
3. **`app/services/classification_comparison.py`**: New service module
4. **`app/services/gemini_service.py`**: Existing service (no changes needed)

## Testing

### Test the Integration

```python
# test_integration.py
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_classification_with_gemini():
    # Login
    login_res = requests.post(
        f'{BASE_URL}/api/login',
        json={'email': 'admin@gmail.com', 'password': 'admin'}
    )
    token = login_res.json()['token']
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test article
    test_article = """
    Breaking news: Scientists have discovered that the Earth is actually flat
    and NASA has been hiding this information for decades. According to anonymous
    sources, the government has paid billions to cover up this truth.
    """
    
    # Classify
    response = requests.post(
        f'{BASE_URL}/api/classify',
        headers=headers,
        json={'text': test_article}
    )
    
    result = response.json()
    print(json.dumps(result, indent=2))
    
    # Verify response structure
    assert 'model_result' in result
    assert 'gemini_result' in result
    assert 'final_displayed_result' in result
    assert 'comparison_status' in result
    assert result['comparison_status'] in ['matched', 'conflict', 'model_only']
    
    print("✓ Integration test passed!")

if __name__ == '__main__':
    test_classification_with_gemini()
```

## Monitoring & Logging

The system logs all comparison activities. Check logs for:

- **INFO**: Successful classifications and model agreements
- **WARNING**: Gemini service configuration issues
- **ERROR**: API failures, timeout, or unexpected errors

Example log output:

```
INFO: Classification comparison completed. Model: fake, Gemini: real, Final: real (conflict)
WARNING: Gemini service not configured, using ML model result only
ERROR: Gemini classification error: Connection timeout
```

## Future Enhancements

The architecture supports adding alternative AI providers:

```python
# Hypothetical future integration with other APIs
class ClassificationComparisonService:
    def __init__(self, secondary_provider='gemini'):
        if secondary_provider == 'gemini':
            self.secondary_service = GeminiService()
        elif secondary_provider == 'openai':
            self.secondary_service = OpenAIService()
        elif secondary_provider == 'huggingface':
            self.secondary_service = HuggingFaceService()
```

## Troubleshooting

### Gemini API key not working

1. Verify the key in `.env`: `GEMINI_API_KEY=...`
2. Restart the Flask app: `python run.py`
3. Check Google Cloud Console for API quota limits

### Slow responses

- Gemini API calls typically take 1-3 seconds
- Check network connectivity
- Monitor CPU usage during inference

### Inconsistent results

- This is expected behavior! Different models may classify differently
- Check the `comparison_status` field to understand model agreement
- Review logs to identify patterns in conflicts

## API Changes from Previous Version

### Added to Response

New fields added to `/api/classify` response:
- `gemini_result`
- `final_displayed_result`
- `comparison_status`
- `processing_details`

### Backward Compatibility

Old fields remain unchanged:
- `category`
- `category_confidence`
- `model_result` (renamed from `fake_news_label`)
- `model_confidence` (renamed from `fake_confidence`)

Existing code will continue to work with these fields.
