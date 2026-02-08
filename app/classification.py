import os
import pickle
import logging
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    current_app,
    Response,
)
from urllib.parse import urlparse
from .models import ArticleResult
from .database import db
from flask_login import current_user, login_required
from .utils import sanitize_text, allowed_file, explain_prediction
from .services.xai_pipeline import XAIPipeline

logger = logging.getLogger(__name__)

classify_bp = Blueprint('classify', __name__, template_folder='templates')

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')


def get_trending_news():
    """Fetch real trending news from NewsAPI.org with live source URLs.
    Falls back to mocked data if the API fails or is not configured.
    
    Requires: NEWSAPI_KEY environment variable (get free key from https://newsapi.org)
    Optional: NEWS_COUNTRY (default 'us'), NEWS_CATEGORY (default 'general')
    """
    try:
        import requests
        api_key = os.environ.get('NEWSAPI_KEY')
        
        if api_key:
            # Call NewsAPI.org for real trending headlines
            country = os.environ.get('NEWS_COUNTRY', 'us')
            category = os.environ.get('NEWS_CATEGORY', 'general')
            
            url = f'https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}'
            resp = requests.get(url, timeout=5)
            
            if resp.ok:
                data = resp.json()
                articles = data.get('articles', [])
                headlines = []
                
                for a in articles[:5]:
                    title = a.get('title', '')
                    desc = a.get('description', '')
                    source_url = a.get('url', '#')
                    source_name = a.get('source', {}).get('name', 'Unknown')
                    image = a.get('urlToImage', '')
                    
                    text = f"{title}\n\n{desc}" if desc else title
                    headlines.append({
                        'title': title,
                        'text': text,
                        'url': source_url,
                        'source': source_name,
                        'image': image
                    })
                
                if headlines:
                    logger.info(f"Fetched {len(headlines)} real articles from NewsAPI")
                    return headlines
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch news from NewsAPI: {e}")
    except Exception as e:
        logger.warning(f"Error in get_trending_news: {e}")
    
    # Fallback: mocked headlines
    logger.info("Using fallback mocked trending news")
    return [
        {
            'title': 'Global Markets Rally on Economic Optimism',
            'text': 'Global stock markets rallied today amid signs of improved economic activity. Investors are showing renewed confidence in growth prospects.',
            'url': 'https://example.com/markets',
            'source': 'Financial Times',
            'image': ''
        },
        {
            'title': 'New Study Reveals Health Benefits of Walking',
            'text': 'A recent comprehensive study found walking 30 minutes daily reduces cardiovascular risks by up to 35%.',
            'url': 'https://example.com/health',
            'source': 'Health Today',
            'image': ''
        },
        {
            'title': 'Tech Giant Releases Latest Smartphone',
            'text': 'The tech giant announced its new flagship smartphone with improved battery life and advanced camera capabilities.',
            'url': 'https://example.com/tech',
            'source': 'Tech News Daily',
            'image': ''
        },
        {
            'title': 'Local Community Garden Wins Award',
            'text': 'A community garden in the city center received recognition for sustainability efforts and community engagement.',
            'url': 'https://example.com/community',
            'source': 'Local News',
            'image': ''
        },
        {
            'title': 'Scientists Detect Signals from Deep Space',
            'text': 'Researchers reported detecting unusual radio signals that warrant further investigation and analysis.',
            'url': 'https://example.com/science',
            'source': 'Science Weekly',
            'image': ''
        },
    ]


@classify_bp.route('/image_proxy')
def image_proxy():
    """Proxy an external image URL to avoid CORS/hotlinking issues.

    Basic safety checks: require http/https and a non-empty netloc; disallow obvious localhost/private hosts.
    """
    url = request.args.get('url', '')
    if not url:
        return ('Missing url parameter', 400)

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return ('Invalid URL', 400)

    hostname = parsed.hostname or ''
    # Simple private/loopback host blocking
    lowered = hostname.lower()
    if lowered.startswith('localhost') or lowered.startswith('127.') or lowered.startswith('10.') or lowered.startswith('192.168.') or lowered.startswith('172.'):
        return ('Forbidden host', 403)

    try:
        import requests
        resp = requests.get(url, timeout=6, stream=True)
        if not resp.ok:
            return ('Upstream error', resp.status_code)

        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        data = resp.content
        headers = {
            'Cache-Control': 'public, max-age=3600',
        }
        return Response(data, mimetype=content_type, headers=headers)
    except Exception as e:
        logger.warning(f"image_proxy failed for {url}: {e}")
        return ('Error fetching image', 502)

# --- الكلاسات والدوال الأصلية (بدون تغيير) ---
class SimpleWrapper:
    def __init__(self, pipeline=None):
        self.pipeline = pipeline
    def predict(self, texts):
        if isinstance(texts, str): texts = [texts]
        out = []
        for t in texts:
            try:
                r = self.pipeline(t)
                if isinstance(r, list) and len(r) > 0:
                    first = r[0]
                    out.append(first['label'] if isinstance(first, dict) else first)
                else: out.append(r['label'] if isinstance(r, dict) else r)
            except Exception: out.append(None)
        return out
    def predict_proba(self, texts):
        if isinstance(texts, str): texts = [texts]
        try:
            r = self.pipeline(texts, return_all_scores=True)
            out = []
            for item in r:
                scores_list = item if isinstance(item, list) else [item]
                d = {s.get('label'): float(s.get('score', 0.0)) for s in scores_list if isinstance(s, dict)}
                out.append(d)
            return out
        except Exception: return [{} for _ in texts]

def predict_category(text: str):
    models = current_app.config.get('ML_MODELS', {})
    model = models.get('classifier')
    if not model: return None, 0.0
    label_map = current_app.config.get('CATEGORY_LABEL_MAP', {
        'LABEL_0': 'ArtsAndCulture', 'LABEL_1': 'Business', 'LABEL_2': 'Entertainment',
        'LABEL_3': 'GeneralNews', 'LABEL_4': 'Health', 'LABEL_5': 'Other',
        'LABEL_6': 'Politics', 'LABEL_7': 'Sports', 'LABEL_8': 'Technology',
    })
    try:
        if hasattr(model, 'pipeline'):
            try: res = model.pipeline(text, return_all_scores=True)
            except TypeError: res = model.pipeline(text)
            if isinstance(res, list) and len(res) > 0:
                scores = res[0] if isinstance(res[0], list) else res
                if isinstance(scores, list) and scores and isinstance(scores[0], dict):
                    best = max(scores, key=lambda x: x.get('score', 0.0))
                    return label_map.get(str(best.get('label', '')), str(best.get('label', ''))), float(best.get('score', 0.0))
        out = model.predict([text])
        if out and isinstance(out, list):
            val = out[0]
            if isinstance(val, dict):
                return label_map.get(str(val.get('label', '')), str(val.get('label', ''))), float(val.get('score', 0.0))
            return label_map.get(str(val), str(val)), 0.0
    except Exception: logger.exception('predict_category failed')
    return None, 0.0

def predict_fake_news(text: str):
    models = current_app.config.get('ML_MODELS', {})
    model = models.get('fake')
    if not model: return None, 0.0
    label_map = current_app.config.get('FAKE_LABEL_MAP', {'LABEL_0': 'real', 'LABEL_1': 'fake'})
    try:
        if hasattr(model, 'pipeline'):
            try: res = model.pipeline(text, return_all_scores=True)
            except TypeError: res = model.pipeline(text)
            if isinstance(res, list) and len(res) > 0:
                scores = res[0] if isinstance(res[0], list) else res
                if isinstance(scores, list) and scores and isinstance(scores[0], dict):
                    best = max(scores, key=lambda x: x.get('score', 0.0))
                    mapped = label_map.get(str(best.get('label', '')))
                    if mapped: return mapped, float(best.get('score', 0.0))
        out = model.predict([text])
        if isinstance(out, list) and out:
            lbl_raw = out[0]
            raw_lbl = lbl_raw.get('label', '') if isinstance(lbl_raw, dict) else lbl_raw
            sc = float(lbl_raw.get('score', 0.0)) if isinstance(lbl_raw, dict) else 0.0
            mapped = label_map.get(str(raw_lbl))
            if mapped: return mapped, sc
    except Exception: logger.exception('predict_fake_news failed')
    return None, 0.0

@classify_bp.route('/classify', methods=['GET', 'POST'])
def classify_page():
    is_authenticated = current_user.is_authenticated
    free_uses = session.get('free_uses', 0)
    max_free = 3
    result = None
    xai_result = None
    auto_gemini = None 

    if request.method == 'POST':
        if not is_authenticated and free_uses >= max_free:
            flash('Free classification limit reached. Please register or login.', 'info')
            return redirect(url_for('auth.login'))

        # Get text from textarea or file upload
        text = sanitize_text(request.form.get('article_text', '').strip())
        
        # Handle file upload if no text provided
        if not text and 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                try:
                    # Validate file type
                    if not allowed_file(file.filename):
                        flash('Invalid file type. Please upload a .txt file.', 'danger')
                        return redirect(url_for('classify.classify_page'))
                    
                    # Validate file size (max 5MB for safety)
                    file_content = file.read()
                    max_size = 5 * 1024 * 1024  # 5MB
                    if len(file_content) > max_size:
                        flash(f'File too large. Maximum size: 5MB. Your file: {len(file_content) / (1024*1024):.1f}MB', 'danger')
                        return redirect(url_for('classify.classify_page'))
                    
                    # Decode file content with proper error handling
                    try:
                        file_text = file_content.decode('utf-8')
                    except UnicodeDecodeError:
                        # Fallback to latin-1 which accepts all byte values
                        logger.warning(f"UTF-8 decode failed for {file.filename}, trying latin-1")
                        file_text = file_content.decode('latin-1')
                    
                    text = sanitize_text(file_text.strip())
                    
                    if not text:
                        flash('Uploaded file is empty or contains no readable text.', 'warning')
                        return redirect(url_for('classify.classify_page'))
                except Exception as e:
                    logger.error(f"File upload error: {str(e)}")
                    flash(f'Error reading file: {str(e)}', 'danger')
                    return redirect(url_for('classify.classify_page'))
        
        # Validate that we have text
        if not text:
            flash('Please provide article text or upload a file.', 'warning')
            return redirect(url_for('classify.classify_page'))

        # 1. تشغيل الموديل المحلي (Local ML)
        xai_pipeline = XAIPipeline()
        def fake_news_predictor(article_text): return predict_fake_news(article_text)
        
        xai_result = xai_pipeline.process_classification(
            article_text=text, predict_fn=fake_news_predictor,
            user_id=current_user.id if is_authenticated else None
        )
        
        cat, cat_conf = predict_category(text)
        local_label = xai_result.get('prediction_label', 'unknown').lower()
        raw_confidence = xai_result.get('confidence_score', 0.0)
        
        if raw_confidence > 1.0: raw_confidence /= 100.0
        fake_conf_percent = round(raw_confidence * 100, 2)
        
        # 2. تشغيل Gemini للمقارنة (The Decision Logic)
        from .services.gemini_service import GeminiService
        gemini_service = GeminiService()
        
        # نطلب التحليل الشامل من Gemini دائماً أو عند ضعف الثقة
        gemini_data = gemini_service.analyze_article_comprehensive(text)
        
        final_label = local_label # الافتراضي هو الموديل المحلي
        
        if gemini_data:
            gemini_verdict = gemini_data['verdict'].lower() # 'real' or 'fake'
            
            # منطق المقارنة: إذا Gemini قال Fake، نعتمد كلامه لأنه الأكثر دقة في المعلومات العامة
            if gemini_verdict == 'fake':
                final_label = 'fake'
            elif gemini_verdict == 'real' and local_label == 'real':
                final_label = 'real'
            elif gemini_verdict == 'real' and local_label == 'fake':
                final_label = 'real'
            elif gemini_verdict == 'fake' and local_label == 'real':
                final_label = 'fake'
            
            # تخزين بيانات Gemini لعرضها في الواجهة
            auto_gemini = {
                'summary': gemini_data['summary'],
                'explanation': gemini_data['explanation'],
                'verdict': gemini_data['verdict']
            }

        # 3. حفظ النتيجة النهائية
        try:
            result = ArticleResult(
                user_id=current_user.id if is_authenticated else None,
                article_text=text, 
                predicted_category=cat,
                fake_news_label=final_label, # النتيجة بعد المقارنة
                category_confidence=cat_conf,
                fake_confidence=raw_confidence,
            )

            if is_authenticated:
                db.session.add(result)
                db.session.commit()
            else:
                session['free_uses'] = free_uses + 1
        except Exception as db_err:
            logger.error(f"Database error saving result: {str(db_err)}")
            try:
                db.session.rollback()
            except:
                pass
            # Continue without saving to DB
            result = None
            if not is_authenticated:
                session['free_uses'] = free_uses + 1

        xai_result_formatted = XAIPipeline.format_for_display(xai_result)
        trending = get_trending_news()
        return render_template('classify.html', 
                               result=result, 
                               xai_result=xai_result_formatted,
                               auto_gemini=auto_gemini, 
                               is_anonymous=not is_authenticated,
                               trending_news=trending)
    
    user_history = ArticleResult.query.filter_by(user_id=current_user.id).order_by(ArticleResult.timestamp.desc()).all() if is_authenticated else []
    remaining = max(0, 3 - session.get('free_uses', 0)) if not is_authenticated else None
    trending = get_trending_news()
    return render_template('classify.html', remaining=remaining, user_history=user_history, trending_news=trending)


@classify_bp.route('/get_explanation', methods=['POST'])
def get_explanation():
    data = request.get_json()
    text = data.get('text', '')
    if not text: return jsonify({'error': 'No text provided'}), 400

    try:
        xai_pipeline = XAIPipeline()
        def predictor(t): return predict_fake_news(t)
        xai_result = xai_pipeline.process_classification(text, predictor)
        
        from .services.gemini_service import GeminiService
        gemini = GeminiService()
        
        conf_raw = xai_result.get('confidence_score', 0.0)
        if conf_raw > 1.0: conf_raw /= 100.0
        
        summary, expl, conf_expl = gemini.generate_explanation(
            text, xai_result.get('prediction_label', 'unknown').upper(), round(conf_raw * 100, 2)
        )
        
        # التأكد من إرسال نصوص بدلاً من None لمنع خطأ المتصفح
        return jsonify({
            'explanation': str(expl) if expl else "No detailed analysis available.",
            'summary': str(summary) if summary else "No summary available.",
            'confidence_explanation': str(conf_expl) if conf_expl else "N/A",
            'prediction_label': xai_result.get('prediction_label'),
            'confidence_score': conf_raw,
            # هذا السطر تم تأمينه ليبحث عن كل الأسماء المحتملة لـ LIME
            'lime_html': xai_result.get('explanation_html') or xai_result.get('lime_html') or "LIME Analysis Unavailable"
        })
    except Exception as e:
        logger.error(f"Error in get_explanation: {str(e)}")
        return jsonify({'error': str(e)}), 500

# بقية الدوال (history, api_classify, api_xai_result) تبقى كما هي تماماً بدون تغيير
@classify_bp.route('/history')
@login_required
def history_page():
    user_history = ArticleResult.query.filter_by(user_id=current_user.id).order_by(ArticleResult.timestamp.desc()).all()
    return render_template('history.html', user_history=user_history)

@classify_bp.route('/api_classify', methods=['POST'])
def api_classify_route():
    data = request.json or {}
    text = sanitize_text(data.get('text', ''))
    if not text: return jsonify({'error': 'text required'}), 400
    cat, cat_conf = predict_category(text)
    fake_label, fake_conf = predict_fake_news(text)
    return jsonify({
        'category': cat, 'category_confidence': float(cat_conf or 0.0),
        'fake_news_label': fake_label, 'fake_confidence': float(fake_conf or 0.0),
    })

@classify_bp.route('/api/xai_result', methods=['POST'])
@login_required
def api_xai_result():
    data = request.json or {}
    text = data.get('text', '')
    if not text: return jsonify({'error': 'No text provided'}), 400
    try:
        xai_pipeline = XAIPipeline()
        def pred(t): return predict_fake_news(t)
        result = xai_pipeline.process_classification(text, pred, current_user.id)
        return jsonify(XAIPipeline.format_for_display(result))
    except Exception as e:
        logger.exception(f"Error in XAI result API: {str(e)}")
        return jsonify({'error': str(e)}), 500