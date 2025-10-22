from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, abort, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User, Post, Category, Comment
from app.forms import (LoginForm, RegistrationForm, PostForm, SearchForm, 
                      UserProfileForm, CommentForm, CategoryForm, ChangePasswordForm)
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
import os
import uuid

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__)

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder_type='images'):
    """Save uploaded file and return the filename"""
    if file and file.filename:
        # Get file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Determine upload folder
        if folder_type == 'images':
            upload_folder = current_app.config['UPLOAD_FOLDER_IMAGES']
        elif folder_type == 'videos':
            upload_folder = current_app.config['UPLOAD_FOLDER_VIDEOS']
        else:
            upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def delete_uploaded_file(filename, folder_type='images'):
    """Delete uploaded file"""
    if filename:
        if folder_type == 'images':
            upload_folder = current_app.config['UPLOAD_FOLDER_IMAGES']
        elif folder_type == 'videos':
            upload_folder = current_app.config['UPLOAD_FOLDER_VIDEOS']
        else:
            upload_folder = current_app.config['UPLOAD_FOLDER']
        
        file_path = os.path.join(upload_folder, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Enhanced home page with categories and featured posts"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', 0, type=int)
    
    query = Post.query.filter_by(is_published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    featured_posts = Post.query.filter_by(is_published=True, is_featured=True).limit(3).all()
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False)
    
    categories = Category.query.order_by(Category.name).all()
    
    search_form = SearchForm()
    return render_template('index.html', title='Home', posts=posts, 
                         featured_posts=featured_posts, categories=categories, 
                         search_form=search_form, current_category=category_id)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Enhanced user dashboard with analytics"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    total_posts = Post.query.filter_by(user_id=current_user.id).count()
    published_posts = Post.query.filter_by(user_id=current_user.id, is_published=True).count()
    draft_posts = total_posts - published_posts
    total_views = db.session.query(db.func.sum(Post.view_count)).filter_by(user_id=current_user.id).scalar() or 0
    total_comments = Comment.query.join(Post).filter(Post.user_id == current_user.id).count()
    
    analytics = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views,
        'total_comments': total_comments
    }
    
    return render_template('user/dashboard.html', title='Dashboard', posts=posts, analytics=analytics)

@main_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Enhanced post creation with categories and SEO"""
    form = PostForm()
    if form.validate_on_submit():
        # Handle image (upload or URL)
        image_filename = None
        image_url = None
        if form.image.data:
            image_filename = save_uploaded_file(form.image.data, 'images')
        elif form.image_url.data:
            image_url = form.image_url.data
        
        # Handle video (upload or URL)
        video_filename = None
        video_url = None
        if form.video.data:
            video_filename = save_uploaded_file(form.video.data, 'videos')
        elif form.video_url.data:
            video_url = form.video_url.data
        
        post = Post(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data and current_user.is_admin,
            allow_comments=form.allow_comments.data,
            user_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data else None,
            image_filename=image_filename,
            video_filename=video_filename,
            image_url=image_url,
            video_url=video_url
        )
        
        post.slug = post.generate_slug()
        post.calculate_reading_time()
        
        if post.is_published:
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('user/create_post.html', title='Create Post', form=form)

@main_bp.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """Enhanced post editing"""
    post = Post.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = PostForm()
    
    if form.validate_on_submit():
        # Handle image (upload or URL)
        if form.image.data:
            # Delete old image if exists
            if post.image_filename:
                delete_uploaded_file(post.image_filename, 'images')
            # Save new image
            post.image_filename = save_uploaded_file(form.image.data, 'images')
            post.image_url = None  # Clear URL if uploading file
        elif form.image_url.data:
            post.image_url = form.image_url.data
            post.image_filename = None  # Clear filename if using URL
        
        # Handle video (upload or URL)
        if form.video.data:
            # Delete old video if exists
            if post.video_filename:
                delete_uploaded_file(post.video_filename, 'videos')
            # Save new video
            post.video_filename = save_uploaded_file(form.video.data, 'videos')
            post.video_url = None  # Clear URL if uploading file
        elif form.video_url.data:
            post.video_url = form.video_url.data
            post.video_filename = None  # Clear filename if using URL
        
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        post.is_published = form.is_published.data
        post.is_featured = form.is_featured.data and current_user.is_admin
        post.allow_comments = form.allow_comments.data
        post.category_id = form.category_id.data if form.category_id.data else None
        post.updated_at = datetime.utcnow()
        
        post.slug = post.generate_slug()
        post.calculate_reading_time()
        
        if post.is_published and not post.published_at:
            post.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.excerpt.data = post.excerpt
        form.meta_description.data = post.meta_description
        form.meta_keywords.data = post.meta_keywords
        form.is_published.data = post.is_published
        form.is_featured.data = post.is_featured
        form.allow_comments.data = post.allow_comments
        form.category_id.data = post.category_id
    
    return render_template('user/edit_post.html', title='Edit Post', form=form, post=post)

@main_bp.route('/delete_post/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    """Delete a post (author or admin)"""
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Delete associated media files
    if post.image_filename:
        delete_uploaded_file(post.image_filename, 'images')
    if post.video_filename:
        delete_uploaded_file(post.video_filename, 'videos')
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    next_url = request.referrer or url_for('main.dashboard')
    return redirect(next_url)

@main_bp.route('/post/<slug>')
@main_bp.route('/post/<int:id>')
def view_post(slug=None, id=None):
    """Enhanced post view with comments and engagement"""
    if slug:
        post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    else:
        post = Post.query.filter_by(id=id, is_published=True).first_or_404()
    
    post.increment_views()
    
    comments = Comment.query.filter_by(post_id=post.id, is_approved=True).order_by(Comment.created_at.desc()).all()
    
    comment_form = CommentForm()
    
    related_posts = Post.query.filter(
        Post.id != post.id,
        Post.is_published == True,
        Post.category_id == post.category_id if post.category_id else True
    ).order_by(Post.view_count.desc()).limit(3).all()
    
    return render_template('post_detail.html', title=post.title, post=post, 
                         comments=comments, comment_form=comment_form, related_posts=related_posts)

@main_bp.route('/post/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Add comment to post"""
    post = Post.query.filter_by(id=id, is_published=True).first_or_404()
    
    if not post.allow_comments:
        flash('Comments are disabled for this post.', 'warning')
        return redirect(url_for('main.view_post', id=post.id))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
    else:
        flash('Error adding comment. Please check your input.', 'error')
    
    return redirect(url_for('main.view_post', id=post.id))

@main_bp.route('/profile/<username>')
def user_profile(username):
    """Public user profile page"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(user_id=user.id, is_published=True).order_by(
        Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/profile.html', title=f'{user.get_display_name()}', user=user, posts=posts)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User settings and profile editing"""
    form = UserProfileForm()
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        current_user.twitter_handle = form.twitter_handle.data
        current_user.github_handle = form.github_handle.data
        current_user.linkedin_handle = form.linkedin_handle.data
        current_user.email_notifications = form.email_notifications.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.user_settings'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.website.data = current_user.website
        form.twitter_handle.data = current_user.twitter_handle
        form.github_handle.data = current_user.github_handle
        form.linkedin_handle.data = current_user.linkedin_handle
        form.email_notifications.data = current_user.email_notifications
    
    return render_template('user/settings.html', title='Settings', form=form)

@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed!', 'success')
            return redirect(url_for('main.user_settings'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('user/change_password.html', title='Change Password', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            user.update_last_active()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.get_display_name()}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@api_bp.route('/search')
def search():
    """Enhanced search API endpoint"""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', 0, type=int)
    
    if len(query) < 2:
        return jsonify({'posts': []})
    
    posts_query = Post.query.filter(
        Post.title.contains(query) | Post.content.contains(query),
        Post.is_published == True
    )
    
    if category_id:
        posts_query = posts_query.filter_by(category_id=category_id)
    
    posts = posts_query.order_by(Post.created_at.desc()).limit(10).all()
    
    return jsonify({
        'posts': [post.to_dict() for post in posts]
    })

@api_bp.route('/posts')
def get_posts():
    """Get posts API endpoint with enhanced filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    category_id = request.args.get('category', 0, type=int)
    
    query = Post.query.filter_by(is_published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page,
        'has_next': posts.has_next,
        'has_prev': posts.has_prev
    })

@api_bp.route('/user_stats')
@login_required
def user_stats():
    """Get current user statistics"""
    user_posts = Post.query.filter_by(user_id=current_user.id).count()
    published_posts = Post.query.filter_by(user_id=current_user.id, is_published=True).count()
    draft_posts = user_posts - published_posts
    total_views = db.session.query(db.func.sum(Post.view_count)).filter_by(user_id=current_user.id).scalar() or 0
    total_comments = Comment.query.join(Post).filter(Post.user_id == current_user.id).count()
    
    return jsonify({
        'total_posts': user_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views,
        'total_comments': total_comments,
        'user': current_user.to_dict()
    })

@api_bp.route('/categories')
def get_categories():
    """Get all categories"""
    categories = Category.query.order_by(Category.name).all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    })

@api_bp.route('/validate_username')
def validate_username():
    """Validate username availability via AJAX"""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters'})
    
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'available': False, 'message': 'Username already exists'})
    
    return jsonify({'available': True, 'message': 'Username is available'})

@api_bp.route('/validate_email')
def validate_email():
    """Validate email availability via AJAX"""
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'available': False, 'message': 'Email already registered'})
    
    return jsonify({'available': True, 'message': 'Email is available'})

@api_bp.route('/like_post/<int:id>', methods=['POST'])
@login_required
def like_post(id):
    """Like/unlike a post"""
    post = Post.query.get_or_404(id)
    post.like_count += 1
    db.session.commit()
    return jsonify({'likes': post.like_count})

@admin_bp.route('/categories')
@login_required
def manage_categories():
    """Admin category management"""
    if not current_user.is_admin:
        abort(403)
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', title='Manage Categories', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new category"""
    if not current_user.is_admin:
        abort(403)
    
    form = CategoryForm()
    if form.validate_on_submit():
        import re
        slug = re.sub(r'[^\w\s-]', '', form.name.data.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        
        category = Category(
            name=form.name.data,
            description=form.description.data,
            slug=slug,
            color=form.color.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html', title='Create Category', form=form)

@main_bp.route('/uploads/<folder>/<filename>')
def serve_upload(folder, filename):
    """Serve uploaded files"""
    try:
        if folder == 'images':
            return send_from_directory(current_app.config['UPLOAD_FOLDER_IMAGES'], filename)
        elif folder == 'videos':
            return send_from_directory(current_app.config['UPLOAD_FOLDER_VIDEOS'], filename)
        else:
            abort(404)
    except Exception as e:
        abort(404)

@main_bp.app_errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

@main_bp.app_errorhandler(403)
def forbidden_error(error):
    """403 error handler"""
    return render_template('errors/403.html'), 403