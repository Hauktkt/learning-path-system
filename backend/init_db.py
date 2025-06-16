from src.database import Base, engine, SessionLocal, User
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create test user
        db = SessionLocal()
        try:
            # Check if test user exists
            test_user = db.query(User).filter(User.username == "admin").first()
            if not test_user:
                # Create test user
                hashed_password = generate_password_hash("admin123")
                test_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=hashed_password,
                    created_at=datetime.utcnow()
                )
                db.add(test_user)
                db.commit()
                logger.info("Test user 'admin' created with password 'admin123'")
            else:
                logger.info("Test user 'admin' already exists")
        finally:
            db.close()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Initializing database...")
    success = init_db()
    if success:
        logger.info("Database initialization complete")
        
        # Print database file location
        db_path = os.path.abspath("learning_path.db")
        logger.info(f"Database file located at: {db_path}")
        
        # Print test user credentials
        logger.info("\nTest User Credentials:")
        logger.info("Username: admin")
        logger.info("Password: admin123")
        logger.info("\nYou can now run the API with: python -m src.api")
    else:
        logger.error("Database initialization failed") 