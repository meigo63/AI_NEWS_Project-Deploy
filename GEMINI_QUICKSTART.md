# Gemini Integration - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Set Your Gemini API Key
```bash
# Edit .env file and add:
GEMINI_API_KEY=your-api-key-from-https://aistudio.google.com/apikey
```

### Step 2: Create Database Migration
```bash
flask db migrate -m "Add Gemini integration fields"
flask db upgrade
```

### Step 3: Restart the App
```bash
python run.py
```

### Step 4: Test the Integration
```bash
python test_comparison_integration.py
```

---

## 📝 Quick API Test

### 1. Get Auth Token
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gmail.com",
    "password": "admin"
  }'
```

Response:
```json
{"token": "abc123...", "role": "admin"}
```

### 2. Classify an Article
```bash
curl -X POST http://localhost:5000/api/classify \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking: Scientists discover Earth is flat and NASA covers it up!"
  }'
```

Response:
```json
{
  "original_text": "Breaking: Scientists discover Earth is flat...",
  "category": "GeneralNews",
  "category_confidence": 0.92,
  "model_result": "fake",
  "model_confidence": 0.89,
  "gemini_result": "fake",
  "final_displayed_result": "fake",
  "comparison_status": "matched",
  "processing_details": {
    "gemini_available": true,
    "gemini_error": null,
    "processing_time_ms": 1250.34
  }
}
```

---

## 🔍 Understanding the Response

| Field | Meaning |
|-------|---------|
| `model_result` | What the local ML model says |
| `gemini_result` | What Google Gemini says |
| `final_displayed_result` | **What you should show the user** |
| `comparison_status` | Why that result was chosen |

### Comparison Status Explained

- **`matched`**: Both models agree → Shows ML result (faster)
- **`conflict`**: Models disagree → Shows Gemini result (secondary verification)
- **`model_only`**: Gemini unavailable → Shows ML result only

---

## 🛠️ Troubleshooting

### Problem: Gemini returns "ERROR"
**Solution:** Check your API key
```bash
# In .env file:
GEMINI_API_KEY=sk-...  # Must be valid
```

### Problem: Slow responses (5+ seconds)
**Solution:** This is normal - Gemini API takes 1-3 seconds
- Local ML model: ~100ms
- Gemini API: ~1-3 seconds
- **Total: ~1-4 seconds**

### Problem: Different results for same article
**Solution:** This is expected! Models can disagree
- Check `comparison_status` to see if models agreed
- Review both `model_result` and `gemini_result`

---

## 📚 Documentation

For detailed information, see:
- **[GEMINI_INTEGRATION_GUIDE.md](GEMINI_INTEGRATION_GUIDE.md)** - Full API documentation
- **[GEMINI_INTEGRATION_IMPLEMENTATION.md](GEMINI_INTEGRATION_IMPLEMENTATION.md)** - Technical implementation details

---

## ✅ What's New

### New API Response Fields
```
✓ gemini_result         - Gemini API classification
✓ final_displayed_result - Result for user display
✓ comparison_status      - Match/conflict/model_only
✓ processing_details     - Timing and error info
```

### Updated Endpoints
- `POST /api/classify` - Now includes Gemini results
- `GET /api/history` - Now includes Gemini results
- `GET /api/admin/results` - Now includes Gemini results

---

## 🔄 How It Works

```
User submits article
        ↓
    ┌───────────────────────┐
    │  ML Model Classifier  │
    │   (50-200ms)          │
    └───────────┬───────────┘
                │
                ├─────────→ Gemini API
                │           (1-3 seconds)
                │
                ↓
        ┌─────────────────┐
        │  Compare Results│
        │  Apply Logic    │
        └────────┬────────┘
                 │
        ┌────────▼─────────┐
        │ Final Result for │
        │  User Display    │
        └──────────────────┘
```

---

## 🎯 Decision Logic

```
IF ML says FAKE and Gemini says FAKE
    → Show FAKE (status: matched)

IF ML says REAL and Gemini says REAL
    → Show REAL (status: matched)

IF ML says FAKE and Gemini says REAL
    → Show REAL (status: conflict - use Gemini)

IF ML says REAL and Gemini says FAKE
    → Show FAKE (status: conflict - use Gemini)

IF Gemini fails/times out
    → Show ML result (status: model_only)
```

---

## 📊 Example Classifications

### Example 1: Obvious Fake News
```
Input: "Earth is flat, NASA covers it up"
ML Model:      fake (0.95 confidence)
Gemini:        fake
Result:        fake (matched)
```

### Example 2: Legitimate News
```
Input: "Federal Reserve raises interest rates"
ML Model:      real (0.88 confidence)
Gemini:        real
Result:        real (matched)
```

### Example 3: Conflicting Results
```
Input: "New study claims coffee cures cancer"
ML Model:      fake (0.62 confidence)
Gemini:        real
Result:        real (conflict - uses Gemini)
```

### Example 4: Gemini Unavailable
```
Input: "Some news article"
ML Model:      real (0.85 confidence)
Gemini:        ERROR (timeout)
Result:        real (model_only)
```

---

## 🚨 Error Handling

The system handles these scenarios gracefully:

| Error | Behavior |
|-------|----------|
| Gemini timeout | Falls back to ML model |
| Invalid API key | Falls back to ML model |
| Network error | Falls back to ML model |
| Malformed response | Falls back to ML model |

**All errors are logged** - Check app logs for details

---

## 💡 Pro Tips

1. **Monitor comparison_status**
   - `matched` indicates high confidence
   - `conflict` indicates low confidence scenario
   - `model_only` indicates Gemini issue

2. **Use for improving model**
   - Collect `conflict` cases to understand model limitations
   - Use Gemini results for retraining data

3. **Performance optimization**
   - Responses take 1-4 seconds (normal for API calls)
   - Consider caching for identical articles
   - Use async processing for batch classification

4. **Fallback behavior**
   - System always returns a result, even if Gemini fails
   - No disruption to user experience
   - Fallback is logged for monitoring

---

## 🎓 Learning Path

1. **First Time?** Read this file (you're here!)
2. **Want more details?** See `GEMINI_INTEGRATION_GUIDE.md`
3. **Curious about code?** See `GEMINI_INTEGRATION_IMPLEMENTATION.md`
4. **Want to test?** Run `python test_comparison_integration.py`

---

## ✨ Features Summary

✅ Dual classification (ML + Gemini)
✅ Intelligent comparison logic
✅ Automatic fallback if Gemini fails
✅ Response normalization
✅ Comprehensive error handling
✅ Full audit trail in database
✅ Minimal code changes
✅ Backward compatible
✅ Production ready

---

**Ready?** Start with Step 1 above! 🚀
