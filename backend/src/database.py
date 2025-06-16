from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Tạo database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./learning_path.db"

# Tạo engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Tạo SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    learning_paths = relationship("LearningPath", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    progress = relationship("Progress", back_populates="user")

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    field = Column(String)
    level = Column(String)
    duration = Column(Integer)
    daily_hours = Column(Integer)
    total_hours = Column(Integer)
    total_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    tasks = relationship("Task", back_populates="learning_path")
    progress = relationship("Progress", back_populates="learning_path")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    date = Column(DateTime)
    phase = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="tasks")
    user = relationship("User", back_populates="tasks")

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    skill_name = Column(String)
    progress_percentage = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    learning_path = relationship("LearningPath", back_populates="progress")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    response = Column(String)
    resources = Column(String)  # JSON string of resources
    created_at = Column(DateTime, default=datetime.utcnow)

# Tạo database
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 