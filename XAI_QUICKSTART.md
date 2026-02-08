# XAI Implementation - Quick Start Guide

## ✅ What Was Implemented

A **fully automatic Explainable AI pipeline** that runs with a single click. No extra UI steps needed.

### The Complete Flow

1. **User clicks "Classify"** → Article submitted
2. **ML Model runs** → Predicts REAL/FAKE with confidence score
3. **Performance tracked** → CPU usage & inference time measured
4. **Conditional Gemini verification** → If confidence < 60%, Gemini re-checks
5. **Gemini generates explanations** → Summary, reasoning, confidence interpretation
6. **Everything stored in database** → For admin analytics
7. **User sees results** → Prediction + explanation (all automatic)
8. **Admin sees metrics** → CPU, time, verification status

---

## 🚀 Setup (5 Steps)

### 1. Install New Dependencies
```bash
pip install google-generativeai psutil
```

### 2. Get Gemini API Key
- Go to https://makersuite.google.com/app/apikey
- Create new API key
- Keep it safe

### 3. Update .env
```env
GEMINI_API_KEY=your_actual_key_here
```

### 4. Create Database Table
```bash
flask db upgrade
```

Or use manual SQL from `MIGRATION.md`

### 5. Restart App
```bash
python run.py
```

---

## 📊 What You Get

### For Users
✓ Prediction (REAL/FAKE) with confidence %  
✓ Article summary (4-6 bullet points)  
✓ Explanation of why this label  
✓ What the confidence score means  
✓ All automatic, no extra clicks  

### For Admins
✓ Total classifications tracked  
✓ Average confidence across all  
✓ Processing time analytics  
✓ CPU usage monitoring  
✓ Fake/Real distribution  
✓ Gemini verification frequency  
✓ Beautiful dashboard charts  

---

## 📁 New Files Created

```
app/services/
├── __init__.py
├── metrics_service.py      ← Performance tracking
├── gemini_service.py       ← Gemini AI integration
├── insight_service.py      ← Database persistence
└── xai_pipeline.py         ← Main orchestrator

app/templates/
└── admin_xai_analytics.html ← New admin dashboard

Documentation/
├── XAI_IMPLEMENTATION.md   ← Full technical details
└── MIGRATION.md            ← Database setup help
```

---

## 📝 Code Changes (Summary)

### Modified Files

**app/models.py**
- Added `ClassificationInsight` table model

**app/classification.py**
- Added XAI pipeline integration to classify route
- Automatic explanations on every classification
- New `/api/xai_result` endpoint for AJAX

**app/admin.py**
- Added `/admin/xai_analytics` route
- Added `/admin/api/xai_metrics` API endpoint
- Integrated analytics service

**app/requirements.txt**
- Added `google-generativeai>=0.3.0`
- Added `psutil>=5.9.0`

**.env**
- Added `GEMINI_API_KEY` placeholder

**app/templates/classify.html**
- XAI results now display automatically
- Performance metrics shown to admins
- User sees friendly explanation cards

**app/templates/admin_dashboard.html**
- Added link to XAI Analytics Dashboard

---

## 🔧 How It Works (Technical)

### XAI Pipeline Orchestration

```python
pipeline = XAIPipeline()

result = pipeline.process_classification(
    article_text="User's article...",
    predict_fn=predict_fake_news,
    user_id=123
)
```

### What Happens Inside

1. **MetricsTracker** starts timing
2. **ML prediction** runs
3. **MetricsTracker** stops, captures CPU/time
4. **GeminiService** checks: `confidence < 60%?`
   - Yes → Generate explanations
   - No → Skip Gemini
5. **InsightService** saves to database
6. **XAIPipeline.format_for_display()** formats for UI

### Error Handling

- Gemini API fails? → Show ML only (non-blocking)
- Database fails? → Still show results to user
- Metrics fail? → Return 0 values
- Everything fails gracefully

---

## 📊 Admin Dashboard Features

Visit: `/admin/xai_analytics`

**Metrics Cards:**
- Total Classifications
- Average Confidence Score
- Avg Processing Time (ms)
- Avg CPU Usage (%)

**Charts:**
- Confidence Distribution (histogram)
- Processing Time Trend (line chart)

**Stats:**
- Fake vs Real count
- Gemini verification count
- Decision source breakdown

**Recent Classifications Table:**
- Article preview
- Prediction + confidence
- Verification status
- Decision source
- Performance metrics
- Timestamp

---

## 🧪 Testing

### Test via UI
1. Go to /classify
2. Paste an article
3. Click "Classify"
4. See automatic explanation

### Test Gemini (Low Confidence)
1. Create test article with mixed/ambiguous signals
2. If confidence < 60% → Gemini will be triggered
3. See verification badge in results

### Test Admin Dashboard
1. Login as admin
2. Go to /admin
3. Click "XAI Analytics"
4. See all metrics and charts

### Test Database
```python
from app.models import ClassificationInsight
insights = ClassificationInsight.query.limit(5).all()
for i in insights:
    print(f"{i.prediction_label} ({i.confidence_score}%) - {i.decision_source}")
```

---

## 🔐 Security Notes

- Gemini API key in .env (not in code)
- Admin-only dashboard at `/admin/xai_analytics`
- CPU metrics only shown to admins
- User data properly isolated

---

## ⚠️ Important: Do NOT

❌ Modify existing routes (they still work as before)  
❌ Rename existing functions  
❌ Remove ArticleResult table (still used for compatibility)  
❌ Change the "Classify" button behavior  

---

## 🆘 Troubleshooting

### "GEMINI_API_KEY not found"
- Check .env file is in root
- Check spelling: `GEMINI_API_KEY=`
- Restart Flask app

### No explanations showing
- Check Gemini API key is valid
- Check internet connection
- Check logs for errors
- Classification still works

### Database migration fails
- Use manual SQL from MIGRATION.md
- Check MySQL is running
- Check database permissions

### High processing times
- First inference: slower (~2-5s with Gemini)
- Subsequent: faster (~500ms ML only)
- Check `/admin/xai_analytics` for trends

---

## 📚 Full Documentation

For complete technical details, see:
- `XAI_IMPLEMENTATION.md` - Full architecture & API docs
- `MIGRATION.md` - Database setup options
- Service docstrings - Inline documentation

---

## ✨ Key Features

✅ **One-Click XAI** - Everything runs automatically  
✅ **Conditional Verification** - Gemini only when needed (confidence < 60%)  
✅ **Non-Blocking Fallback** - Works without Gemini API  
✅ **Performance Metrics** - CPU & time tracking  
✅ **Admin Analytics** - Beautiful dashboard  
✅ **Database Persistence** - Full audit trail  
✅ **Backward Compatible** - Existing code untouched  

---

## 🎯 Next Steps

1. ✅ Install dependencies (`pip install -r requirements.txt`)
2. ✅ Add Gemini API key to .env
3. ✅ Run database migration (`flask db upgrade`)
4. ✅ Restart Flask app
5. ✅ Test classification
6. ✅ Check admin dashboard
7. ✅ Done! 🎉

---

**Questions?** Check XAI_IMPLEMENTATION.md for detailed API docs.
