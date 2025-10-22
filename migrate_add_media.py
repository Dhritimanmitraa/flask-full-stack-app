"""Migration script to add image and video fields to Post model"""
from app import create_app, db
from app.models import Post

def migrate():
    """Add image_filename and video_filename columns to Post table"""
    app = create_app()
    
    with app.app_context():
        # Create the new columns
        try:
            db.engine.execute("ALTER TABLE post ADD COLUMN image_filename VARCHAR(255)")
            print("✓ Added image_filename column")
        except Exception as e:
            print(f"⚠ image_filename column might already exist: {e}")
        
        try:
            db.engine.execute("ALTER TABLE post ADD COLUMN video_filename VARCHAR(255)")
            print("✓ Added video_filename column")
        except Exception as e:
            print(f"⚠ video_filename column might already exist: {e}")
        
        print("\n✓ Migration completed successfully!")
        print("You can now use image and video uploads in your posts.")

if __name__ == '__main__':
    migrate()

