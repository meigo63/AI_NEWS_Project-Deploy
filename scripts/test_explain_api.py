import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
import json

app = create_app()
with app.test_client() as c:
    test_text = 'This is a short test about vaccine safety and unverified claims. Many people believe false information online.'
    resp = c.post('/get_explanation', json={'text': test_text})
    print('status:', resp.status_code)
    data = resp.get_json()
    print('\nResponse keys:', list(data.keys()) if data else None)
    print('has explanation_html:', 'explanation_html' in data if data else False)
    print('has top_words:', 'top_words' in data if data else False)
    if 'top_words' in data:
        print('top_words count:', len(data['top_words']))
        print('first 3 words:', data['top_words'][:3])
    if 'explanation_html' in data:
        print('explanation_html length:', len(data['explanation_html']))
        print('first 200 chars:', data['explanation_html'][:200])
    if 'error' in data:
        print('ERROR:', data['error'])

