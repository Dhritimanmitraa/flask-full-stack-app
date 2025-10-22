from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    """Enhanced User model for authentication and profiles"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    twitter_handle = db.Column(db.String(50))
    github_handle = db.Column(db.String(50))
    linkedin_handle = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self):
        return self.get_full_name() if self.first_name and self.last_name else self.username
    
    def get_initials(self):
        return f"{self.first_name[0].upper()}{self.last_name[0].upper()}" if self.first_name and self.last_name else self.username[0].upper()
    
    def get_post_count(self):
        return Post.query.filter_by(user_id=self.id, is_published=True).count()
    
    def get_comment_count(self):
        return Comment.query.filter_by(user_id=self.id).count()
    
    def update_last_active(self):
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'display_name': self.get_display_name(),
            'initials': self.get_initials(),
            'bio': self.bio,
            'location': self.location,
            'website': self.website,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'post_count': self.get_post_count(),
            'comment_count': self.get_comment_count()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Category model for organizing posts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#6c757d')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='category', lazy=True)
    
    def get_post_count(self):
        return Post.query.filter_by(category_id=self.id, is_published=True).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'color': self.color,
            'post_count': self.get_post_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    """Enhanced Post model with categories, tags, and engagement metrics"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    
    reading_time = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def generate_slug(self):
        import re
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def calculate_reading_time(self):
        word_count = len(self.content.split())
        self.word_count = word_count
        self.reading_time = max(1, round(word_count / 200))
    
    def generate_excerpt(self, length=150):
        if len(self.content) <= length:
            return self.content
        return self.content[:length].rsplit(' ', 1)[0] + '...'
    
    def increment_views(self):
        self.view_count += 1
        db.session.commit()
    
    def get_comment_count(self):
        return Comment.query.filter_by(post_id=self.id).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt or self.generate_excerpt(),
            'reading_time': self.reading_time,
            'word_count': self.word_count,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.get_comment_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category.to_dict() if self.category else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'display_name': self.author.get_display_name(),
                'initials': self.author.get_initials()
            } if self.author else None
        }
    
    def __repr__(self):
        return f'<Post {self.title}>'

class Comment(db.Model):
    """Comment model for post interactions"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': {
                'id': self.author.id,
                'display_name': self.author.get_display_name(),
                'initials': self.author.get_initials()
            } if self.author else None,
            'reply_count': len(self.replies)
        }
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>' 