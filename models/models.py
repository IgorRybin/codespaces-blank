import hashlib
import secrets
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

# Utility for password hashing
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    try:
        parts = stored_hash.split('$')
        if len(parts) != 3:
            return False
        method_details, salt, key_hex = parts
        details = method_details.split(':')
        iterations = int(details[2])
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    color = Column(String(20), default="blue") # Tailwind color for badges
    is_active = Column(Boolean, default=True)

class SubStage(Base):
    __tablename__ = "sub_stages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0)
    default_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    default_assignee = relationship("User")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="new") # "new", "in_progress", "completed"
    sub_stage_id = Column(Integer, ForeignKey("sub_stages.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(String(10), nullable=True) # YYYY-MM-DD
    completed_at = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium") # "low", "medium", "high"
    
    creator = relationship("User", foreign_keys=[creator_id], backref="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_tasks")
    sub_stage = relationship("SubStage", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan", order_by="desc(Comment.created_at)")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan", order_by="desc(TaskHistory.created_at)")

SubStage.tasks = relationship("Task", order_by=Task.created_at, back_populates="sub_stage")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="comments")
    author = relationship("User")

class TaskHistory(Base):
    __tablename__ = "task_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # e.g. "Создание задачи", "Изменение статуса"
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="history")
    user = relationship("User")
