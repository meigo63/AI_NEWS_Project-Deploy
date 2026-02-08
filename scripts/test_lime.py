import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.utils import explain_prediction

app = create_app()
with app.app_context():
    models = app.config.get('ML_MODELS', {})
    fake = models.get('fake')
    print('fake model loaded:', bool(fake))
    html, top_words = explain_prediction('This is a short test article about election fraud and unverified sources.', fake)
    print('explanation_html present:', bool(html))
    print('top_words sample:', top_words[:5])
