from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import User, ArticleResult, Category
from .database import db
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
from .models import Feedback
from .services.insight_service import get_analytics, get_all_insights

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return wrapper

def get_system_stats():
    """Get system performance metrics."""
    total_users = User.query.count()
    total_results = ArticleResult.query.count()
    total_categories = Category.query.count()
    total_feedbacks = Feedback.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    user_count = User.query.filter_by(role='user').count()
    
    # Last 24 hours stats
    last_24h = datetime.utcnow() - timedelta(hours=24)
    results_last_24h = ArticleResult.query.filter(ArticleResult.timestamp >= last_24h).count()
    users_last_24h = User.query.filter(User.created_at >= last_24h).count()
    
    # Get fake vs real count
    fake_count = ArticleResult.query.filter_by(fake_news_label='fake').count()
    real_count = ArticleResult.query.filter_by(fake_news_label='real').count()
    
    return {
        'total_users': total_users,
        'admin_count': admin_count,
        'user_count': user_count,
        'total_results': total_results,
        'results_last_24h': results_last_24h,
        'users_last_24h': users_last_24h,
        'total_categories': total_categories,
        'total_feedbacks': total_feedbacks,
        'fake_count': fake_count,
        'real_count': real_count,
    }

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = get_system_stats()
    users = User.query.all()
    recent_results = ArticleResult.query.order_by(ArticleResult.timestamp.desc()).limit(10).all()
    return render_template('admin_dashboard.html', stats=stats, users=users, recent_results=recent_results)

@admin_bp.route('/users')
@login_required
@admin_required
def users_view():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    if not name or not email or not password:
        flash('Name, email, and password are required', 'danger')
        return redirect(url_for('admin.users_view'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'danger')
        return redirect(url_for('admin.users_view'))
    
    from .utils import hash_password
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.generate_token()
    db.session.add(user)
    db.session.commit()
    logger.info('Admin %s added user %s', current_user.email, user.email)
    flash(f'User {name} added successfully', 'success')
    return redirect(url_for('admin.users_view'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('admin.users_view'))
    user_name = u.name
    db.session.delete(u)
    db.session.commit()
    logger.info('Admin %s deleted user %s', current_user.email, user_name)
    flash(f'User {user_name} deleted', 'info')
    return redirect(url_for('admin.users_view'))

@admin_bp.route('/users/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    u = User.query.get_or_404(user_id)
    role = request.form.get('role')
    if role in ['admin', 'user']:
        u.role = role
        db.session.commit()
        logger.info('Admin %s updated role for user %s to %s', current_user.email, u.email, role)
        flash(f'{u.name} role updated to {role}', 'success')
    else:
        flash('Invalid role', 'danger')
    return redirect(url_for('admin.users_view'))

@admin_bp.route('/results')
@login_required
@admin_required
def results_view():
    results = ArticleResult.query.order_by(ArticleResult.timestamp.desc()).all()
    return render_template('admin_results.html', results=results)

@admin_bp.route('/results/delete/<int:res_id>', methods=['POST'])
@login_required
@admin_required
def delete_result(res_id):
    r = ArticleResult.query.get_or_404(res_id)
    db.session.delete(r)
    db.session.commit()
    logger.info('Admin %s deleted result id=%s', current_user.email, res_id)
    flash('Result deleted', 'info')
    return redirect(url_for('admin.results_view'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories_view():
    categories = Category.query.all()
    return render_template('admin_categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    if Category.query.filter_by(name=name).first():
        flash('Category exists', 'danger')
    else:
        c = Category(name=name, description=description)
        db.session.add(c)
        db.session.commit()
        logger.info('Admin %s added category %s', current_user.email, name)
        flash('Category added', 'success')
    return redirect(url_for('admin.categories_view'))

@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    c = Category.query.get_or_404(cat_id)
    db.session.delete(c)
    db.session.commit()
    logger.info('Admin %s deleted category id=%s', current_user.email, cat_id)
    flash('Category deleted', 'info')
    return redirect(url_for('admin.categories_view'))


@admin_bp.route('/feedback')
@login_required
@admin_required
def feedback_view():
    items = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin_feedback.html', feedbacks=items)


@admin_bp.route('/feedback/delete/<int:fb_id>', methods=['POST'])
@login_required
@admin_required
def delete_feedback(fb_id):
    fb = Feedback.query.get_or_404(fb_id)
    db.session.delete(fb)
    db.session.commit()
    flash('Feedback deleted', 'info')
    return redirect(url_for('admin.feedback_view'))


# ===== NEW: XAI Analytics Dashboard Routes =====

@admin_bp.route('/xai_analytics')
@login_required
@admin_required
def xai_analytics():
    """Main XAI analytics dashboard."""
    analytics = get_analytics()
    insights = get_all_insights(limit=20)
    
    return render_template('admin_xai_analytics.html', 
                          analytics=analytics, 
                          insights=insights)


@admin_bp.route('/api/xai_metrics')
@login_required
@admin_required
def api_xai_metrics():
    """API endpoint for XAI metrics (for charts)."""
    try:
        from .models import ClassificationInsight
        
        # Get all insights for charts
        insights = ClassificationInsight.query.order_by(
            ClassificationInsight.created_at.desc()
        ).limit(100).all()
        
        # Confidence distribution
        confidence_buckets = {
            '0-20': 0, '20-40': 0, '40-60': 0, '60-80': 0, '80-100': 0
        }
        processing_times = []
        
        for insight in insights:
            conf = insight.confidence_score
            if conf < 20:
                confidence_buckets['0-20'] += 1
            elif conf < 40:
                confidence_buckets['20-40'] += 1
            elif conf < 60:
                confidence_buckets['40-60'] += 1
            elif conf < 80:
                confidence_buckets['60-80'] += 1
            else:
                confidence_buckets['80-100'] += 1
            
            if insight.processing_time_ms:
                processing_times.append({
                    'time': insight.processing_time_ms,
                    'timestamp': insight.created_at.isoformat()
                })
        
        return jsonify({
            'confidence_distribution': confidence_buckets,
            'processing_times': processing_times[-20:],  # Last 20
            'total_insights': len(insights)
        })
    except Exception as e:
        logger.exception(f"Error in XAI metrics API: {str(e)}")
        return jsonify({'error': str(e)}), 500
