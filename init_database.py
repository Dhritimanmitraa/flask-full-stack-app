#!/usr/bin/env python3
"""
Database Initialization Script for Flask Blog on Vercel
This script creates all database tables and populates initial data
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize database with tables and default data"""
    
    # Set the DATABASE_URL environment variable for production
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set your Neon PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://username:password@hostname:port/database'")
        return False
    
    try:
        # Import after setting environment variables
        from app import create_app, db
        from app.models import User, Category, Post, Comment
        
        print("🚀 Initializing Flask Blog Database...")
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            print("📋 Creating database tables...")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if data already exists
            if User.query.count() > 0:
                print("📊 Database already has data. Skipping initial data creation.")
                return True
            
            print("📝 Creating default categories...")
            
            # Create default categories
            default_categories = [
                {
                    'name': 'Technology', 
                    'description': 'Latest tech news, tutorials, and insights', 
                    'slug': 'technology', 
                    'color': '#007bff'
                },
                {
                    'name': 'Programming', 
                    'description': 'Programming tips, tutorials, and best practices', 
                    'slug': 'programming', 
                    'color': '#28a745'
                },
                {
                    'name': 'Web Development', 
                    'description': 'Frontend and backend development tutorials', 
                    'slug': 'web-development', 
                    'color': '#17a2b8'
                },
                {
                    'name': 'AI & Machine Learning', 
                    'description': 'Artificial Intelligence and ML topics', 
                    'slug': 'ai-ml', 
                    'color': '#6f42c1'
                },
                {
                    'name': 'Career', 
                    'description': 'Career advice and professional development', 
                    'slug': 'career', 
                    'color': '#fd7e14'
                },
                {
                    'name': 'General', 
                    'description': 'General discussions and miscellaneous topics', 
                    'slug': 'general', 
                    'color': '#6c757d'
                }
            ]
            
            categories = []
            for cat_data in default_categories:
                category = Category(**cat_data)
                db.session.add(category)
                categories.append(category)
            
            db.session.commit()
            print(f"✅ Created {len(categories)} categories")
            
            print("👤 Creating admin user...")
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                bio='Administrator of this Flask blog. Welcome to our platform!',
                location='Digital World',
                is_admin=True,
                is_verified=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Created admin user (username: admin, password: admin123)")
            
            print("📝 Creating sample blog posts...")
            
            # Create sample posts
            sample_posts = [
                {
                    'title': 'Welcome to Your New Blog!',
                    'content': '''# Welcome to Your Flask Blog!

Congratulations! Your Flask blog has been successfully deployed on Vercel. This is your first blog post to get you started.

## What's Next?

1. **Customize Your Profile**: Update your admin profile with your real information
2. **Create Categories**: Add more categories that match your interests
3. **Write Your First Post**: Share your thoughts with the world
4. **Invite Others**: Let people know about your new blog

## Features Available

- ✅ User authentication and profiles
- ✅ Rich text blog posts with categories
- ✅ Comment system for engagement
- ✅ Admin panel for management
- ✅ Responsive design for all devices
- ✅ SEO-friendly URLs

## Getting Started

To create a new post, simply:
1. Log in with your admin account
2. Click "Create Post" in the dashboard
3. Write your content using Markdown
4. Publish when ready!

Happy blogging! 🚀
''',
                    'excerpt': 'Welcome to your new Flask blog! This post will help you get started with your blogging journey.',
                    'is_published': True,
                    'is_featured': True,
                    'allow_comments': True,
                    'meta_description': 'Welcome to your new Flask blog deployed on Vercel. Get started with blogging today!',
                    'meta_keywords': 'flask, blog, vercel, python, web development',
                    'category_id': 1,  # Technology
                    'published_at': datetime.utcnow()
                },
                {
                    'title': 'How to Deploy Flask Apps on Vercel',
                    'content': '''# Deploying Flask Applications on Vercel

Vercel is an excellent platform for deploying Flask applications with its serverless architecture. Here's what you need to know.

## Why Vercel?

- **Free tier** with generous limits
- **Global CDN** for fast content delivery
- **Automatic HTTPS** certificates
- **Git-based deployments**
- **Zero configuration** for many use cases

## Key Configuration Files

### vercel.json
This file tells Vercel how to build and deploy your Flask app:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### api/index.py
Your Flask app entry point for Vercel's serverless functions.

## Environment Variables

Don't forget to set your environment variables:
- `SECRET_KEY` - For Flask session management
- `DATABASE_URL` - Your PostgreSQL connection string

## Best Practices

1. Use PostgreSQL for production databases
2. Optimize for serverless cold starts
3. Handle static files properly
4. Set up proper error handling

Happy deploying! 🚀
''',
                    'excerpt': 'Learn how to deploy Flask applications on Vercel with this comprehensive guide.',
                    'is_published': True,
                    'is_featured': False,
                    'allow_comments': True,
                    'meta_description': 'Complete guide to deploying Flask applications on Vercel serverless platform.',
                    'meta_keywords': 'flask, vercel, deployment, serverless, python',
                    'category_id': 3,  # Web Development
                    'published_at': datetime.utcnow()
                }
            ]
            
            for post_data in sample_posts:
                post = Post(**post_data)
                post.user_id = admin_user.id
                post.slug = post.generate_slug()
                post.calculate_reading_time()
                db.session.add(post)
            
            db.session.commit()
            print(f"✅ Created {len(sample_posts)} sample posts")
            
            print("\n🎉 Database initialization completed successfully!")
            print("\n📊 Summary:")
            print(f"   👥 Users: {User.query.count()}")
            print(f"   📂 Categories: {Category.query.count()}")
            print(f"   📝 Posts: {Post.query.count()}")
            print(f"   💬 Comments: {Comment.query.count()}")
            
            print("\n🔐 Admin Login:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change the admin password after first login!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == '__main__':
    print("🗄️  Flask Blog Database Initialization")
    print("=" * 50)
    
    # Check if running in production
    if os.environ.get('DATABASE_URL'):
        print("🌐 Production mode detected (DATABASE_URL found)")
    else:
        print("🔧 Development mode - make sure to set DATABASE_URL")
        print("\nFor Neon database, use:")
        print("postgresql://username:password@hostname:port/database")
        sys.exit(1)
    
    success = init_database()
    
    if success:
        print("\n✅ Database setup complete! Your blog is ready to use.")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")
        sys.exit(1)
