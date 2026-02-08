import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

app = create_app()
with app.test_client() as c:
    test_text = 'This is a short test about vaccine safety and unverified claims. Many people believe false information online.'
    resp = c.post('/get_explanation', json={'text': test_text})
    print('status:', resp.status_code)
    data = resp.get_json()
    print('\nResponse keys:', list(data.keys()) if data else None)
    if 'error' in data:
        print('ERROR:', data['error'])
    else:
        print('\nPrediction:', data.get('prediction_label'), f"({data.get('confidence_score', 0)*100:.1f}%)")
        print('\nConfidence Explanation:')
        print(data.get('confidence_explanation', 'N/A')[:200])
        print('\nSummary:')
        print(data.get('summary', 'N/A')[:200])
        print('\nExplanation:')
        print(data.get('explanation', 'N/A')[:200])
