from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField, SelectField, URLField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, URL
from app.models import User, Category

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ], render_kw={'placeholder': 'Enter your username', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={'placeholder': 'Enter your password', 'class': 'form-control'})
    
    remember_me = BooleanField('Remember Me', render_kw={'class': 'form-check-input'})
    submit = SubmitField('Sign In', render_kw={'class': 'btn btn-primary'})

class RegistrationForm(FlaskForm):
    """Registration form"""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ], render_kw={'placeholder': 'Enter your first name', 'class': 'form-control'})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ], render_kw={'placeholder': 'Enter your last name', 'class': 'form-control'})
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ], render_kw={'placeholder': 'Choose a username', 'class': 'form-control'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ], render_kw={'placeholder': 'Enter your email', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ], render_kw={'placeholder': 'Create a password', 'class': 'form-control'})
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm your password', 'class': 'form-control'})
    
    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary'})
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class PostForm(FlaskForm):
    """Enhanced post creation/editing form"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters')
    ], render_kw={'placeholder': 'Enter post title', 'class': 'form-control'})
    
    category_id = SelectField('Category', coerce=int, validators=[
        Optional()
    ], render_kw={'class': 'form-select'})
    
    excerpt = TextAreaField('Excerpt', validators=[
        Optional(),
        Length(max=500, message='Excerpt cannot exceed 500 characters')
    ], render_kw={'placeholder': 'Brief description of your post (optional)', 'class': 'form-control', 'rows': 3})
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=10, message='Content must be at least 10 characters long')
    ], render_kw={'placeholder': 'Write your post content...', 'class': 'form-control', 'rows': 15})
    
    meta_description = StringField('Meta Description', validators=[
        Optional(),
        Length(max=160, message='Meta description should not exceed 160 characters')
    ], render_kw={'placeholder': 'SEO meta description (optional)', 'class': 'form-control'})
    
    meta_keywords = StringField('Meta Keywords', validators=[
        Optional(),
        Length(max=255, message='Meta keywords should not exceed 255 characters')
    ], render_kw={'placeholder': 'SEO keywords separated by commas (optional)', 'class': 'form-control'})
    
    # Media upload fields
    image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ], render_kw={'class': 'form-control', 'accept': 'image/*'})
    
    video = FileField('Featured Video', validators=[
        Optional(),
        FileAllowed(['mp4', 'mov', 'avi', 'webm', 'mkv'], 'Only video files are allowed!')
    ], render_kw={'class': 'form-control', 'accept': 'video/*'})
    
    is_published = BooleanField('Publish Post', default=True, render_kw={'class': 'form-check-input'})
    is_featured = BooleanField('Featured Post', default=False, render_kw={'class': 'form-check-input'})
    allow_comments = BooleanField('Allow Comments', default=True, render_kw={'class': 'form-check-input'})
    
    submit = SubmitField('Save Post', render_kw={'class': 'btn btn-primary'})
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, 'Select Category')] + [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]

class UserProfileForm(FlaskForm):
    """User profile editing form"""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ], render_kw={'class': 'form-control'})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ], render_kw={'class': 'form-control'})
    
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio cannot exceed 500 characters')
    ], render_kw={'placeholder': 'Tell us about yourself...', 'class': 'form-control', 'rows': 4})
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100, message='Location cannot exceed 100 characters')
    ], render_kw={'placeholder': 'Your location', 'class': 'form-control'})
    
    website = URLField('Website', validators=[
        Optional(),
        URL(message='Please enter a valid URL')
    ], render_kw={'placeholder': 'https://your-website.com', 'class': 'form-control'})
    
    twitter_handle = StringField('Twitter Handle', validators=[
        Optional(),
        Length(max=50, message='Twitter handle cannot exceed 50 characters')
    ], render_kw={'placeholder': 'your_handle (without @)', 'class': 'form-control'})
    
    github_handle = StringField('GitHub Handle', validators=[
        Optional(),
        Length(max=50, message='GitHub handle cannot exceed 50 characters')
    ], render_kw={'placeholder': 'your_github_username', 'class': 'form-control'})
    
    linkedin_handle = StringField('LinkedIn Handle', validators=[
        Optional(),
        Length(max=50, message='LinkedIn handle cannot exceed 50 characters')
    ], render_kw={'placeholder': 'your-linkedin-profile', 'class': 'form-control'})
    
    email_notifications = BooleanField('Email Notifications', render_kw={'class': 'form-check-input'})
    
    submit = SubmitField('Update Profile', render_kw={'class': 'btn btn-primary'})

class CommentForm(FlaskForm):
    """Comment form"""
    content = TextAreaField('Comment', validators=[
        DataRequired(message='Comment is required'),
        Length(min=5, max=1000, message='Comment must be between 5 and 1000 characters')
    ], render_kw={'placeholder': 'Share your thoughts...', 'class': 'form-control', 'rows': 4})
    
    submit = SubmitField('Post Comment', render_kw={'class': 'btn btn-primary'})

class CategoryForm(FlaskForm):
    """Category management form (admin only)"""
    name = StringField('Category Name', validators=[
        DataRequired(message='Category name is required'),
        Length(min=2, max=80, message='Category name must be between 2 and 80 characters')
    ], render_kw={'class': 'form-control'})
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description cannot exceed 500 characters')
    ], render_kw={'placeholder': 'Category description...', 'class': 'form-control', 'rows': 3})
    
    color = StringField('Color', validators=[
        Optional(),
        Length(min=7, max=7, message='Color must be a valid hex code')
    ], render_kw={'type': 'color', 'class': 'form-control form-control-color', 'value': '#6c757d'})
    
    submit = SubmitField('Save Category', render_kw={'class': 'btn btn-primary'})

class SearchForm(FlaskForm):
    """Enhanced search form"""
    query = StringField('Search', validators=[
        Length(min=1, max=100, message='Search query must be between 1 and 100 characters')
    ], render_kw={'placeholder': 'Search posts...', 'class': 'form-control'})
    
    category_id = SelectField('Category', coerce=int, validators=[
        Optional()
    ], render_kw={'class': 'form-select'})
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, 'All Categories')] + [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ], render_kw={'class': 'form-control'})
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ], render_kw={'class': 'form-control'})
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ], render_kw={'class': 'form-control'})
    
    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'}) 