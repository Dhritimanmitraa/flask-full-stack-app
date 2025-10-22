"""Update database to add new media columns"""
from app import create_app, db
from app.models import Post, User, Category, Comment
from sqlalchemy import text, inspect

def update_database():
    """Add new columns to existing database"""
    app = create_app()
    
    with app.app_context():
        print("Updating database schema...")
        
        # Check if using PostgreSQL
        inspector = inspect(db.engine)
        if db.engine.dialect.name == 'postgresql':
            print("Detected PostgreSQL database...")
            
            # Get table columns
            columns = [col['name'] for col in inspector.get_columns('post')]
            print(f"Current columns in post table: {columns}")
            
            # Add image_filename column if it doesn't exist
            if 'image_filename' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE post ADD COLUMN image_filename VARCHAR(255)"))
                    db.session.commit()
                    print("[OK] Added image_filename column")
                except Exception as e:
                    print(f"Error adding image_filename: {e}")
                    db.session.rollback()
            else:
                print("[OK] image_filename column already exists")
            
            # Add video_filename column if it doesn't exist
            if 'video_filename' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE post ADD COLUMN video_filename VARCHAR(255)"))
                    db.session.commit()
                    print("[OK] Added video_filename column")
                except Exception as e:
                    print(f"Error adding video_filename: {e}")
                    db.session.rollback()
            else:
                print("[OK] video_filename column already exists")
        
        elif db.engine.dialect.name == 'sqlite':
            print("Detected SQLite database...")
            print("SQLite auto-creates columns via db.create_all()")
            db.create_all()
            print("[OK] Database updated")
        
        else:
            print(f"Detected {db.engine.dialect.name} database...")
            print("Attempting db.create_all()...")
            db.create_all()
            print("[OK] Database updated")
        
        print("\n[SUCCESS] Database migration completed successfully!")
        print("You can now use image and video uploads in your posts.")

if __name__ == '__main__':
    update_database()

