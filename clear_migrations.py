#!/usr/bin/env python
"""Clear broken migration history from database."""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Create minimal app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{os.environ.get('MYSQL_USER','root')}:{os.environ.get('MYSQL_PASSWORD','')}@{os.environ.get('MYSQL_HOST','localhost')}/{os.environ.get('MYSQL_DB','news_ai_system')}"
)

db = SQLAlchemy(app)

with app.app_context():
    try:
        # Check existing migrations
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        rows = result.fetchall()
        
        if rows:
            print("Current revisions in alembic_version table:")
            for row in rows:
                print(f"  - {row[0]}")
            
            # Clear them
            db.session.execute(text("DELETE FROM alembic_version"))
            db.session.commit()
            print("\n✓ Cleared all migrations from database")
        else:
            print("✓ No migrations in database (already clean)")
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        print("This might be OK - alembic_version table may not exist yet")
        sys.exit(0)
