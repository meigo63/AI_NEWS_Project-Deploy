# Database Migration Instructions

## Running Migrations

To apply the new `ClassificationInsight` table to your database, run:

```bash
cd d:\AI_NEWS_Project-app
flask db upgrade
```

### If it's the first time with Flask-Migrate:

```bash
flask db init
flask db migrate -m "Add ClassificationInsight model"
flask db upgrade
```

## Manual SQL (if migrations don't work)

If Flask-Migrate has issues, you can create the table manually using this SQL:

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

## Configuration

Make sure your `.env` file has:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey
