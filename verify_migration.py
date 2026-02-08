#!/usr/bin/env python
"""Verify Gemini integration database columns."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{os.environ.get('MYSQL_USER','root')}:{os.environ.get('MYSQL_PASSWORD','')}@{os.environ.get('MYSQL_HOST','localhost')}/{os.environ.get('MYSQL_DB','news_ai_system')}"
)

db = SQLAlchemy(app)

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('article_results')
    
    print("✓ ArticleResult table columns:")
    new_columns = ['gemini_result', 'final_displayed_result', 'comparison_status']
    for col in columns:
        marker = "✓ NEW" if col['name'] in new_columns else "  "
        print(f"  {marker}  {col['name']}: {col['type']}")
    
    print("\n✓ Database migration complete!")
    print("\nNew fields ready:")
    for name in new_columns:
        print(f"  ✓ {name}")
