import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from src.database import SessionLocal, User, LearningPath, Task, Progress

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auth.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create blueprint
auth_api = Blueprint('auth_api', __name__, url_prefix='/api/auth')

# Token management (simple version - consider using JWT in production)
active_tokens = {}  # Maps token -> user_id

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def generate_token():
    return secrets.token_hex(32)

def get_user_from_token(token):
    """Get user from token"""
    if token in active_tokens:
        user_id = active_tokens[token]
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user
        finally:
            db.close()
    return None

@auth_api.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Thiếu trường {field}"}), 400
                
        # Get data
        username = data['username']
        email = data['email']
        password = data['password']
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create user
        db = get_db()
        try:
            # Check if user exists
            existing_user = db.query(User).filter(
                or_(
                    User.username == username,
                    User.email == email
                )
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    return jsonify({"error": "Tên người dùng đã tồn tại"}), 400
                else:
                    return jsonify({"error": "Email đã tồn tại"}), 400
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                created_at=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Generate token
            token = generate_token()
            active_tokens[token] = new_user.id
            
            # Return user data
            return jsonify({
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "created_at": new_user.created_at.isoformat()
                },
                "token": token
            }), 201
            
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "Tên người dùng hoặc email đã tồn tại"}), 400
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi đăng ký: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Lỗi đăng ký: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_api.route('/login', methods=['POST'])
def login():
    """Login and get token"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Thiếu trường {field}"}), 400
                
        # Get data
        username = data['username']
        password = data['password']
        
        # Get user
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if not user or not check_password_hash(user.hashed_password, password):
                return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401
            
            # Generate token
            token = generate_token()
            active_tokens[token] = user.id
            
            # Return user data
            return jsonify({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                },
                "token": token
            }), 200
            
        except Exception as e:
            logger.error(f"Lỗi đăng nhập: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Lỗi đăng nhập: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_api.route('/logout', methods=['POST'])
def logout():
    """Logout and invalidate token"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Không có token"}), 401
            
        token = auth_header.split(' ')[1]
        
        # Invalidate token
        if token in active_tokens:
            del active_tokens[token]
            
        return jsonify({"message": "Đăng xuất thành công"}), 200
        
    except Exception as e:
        logger.error(f"Lỗi đăng xuất: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_api.route('/me', methods=['GET'])
def get_me():
    """Get current user info"""
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Không có token"}), 401
            
        token = auth_header.split(' ')[1]
        
        # Get user from token
        user = get_user_from_token(token)
        if not user:
            return jsonify({"error": "Token không hợp lệ hoặc đã hết hạn"}), 401
            
        # Return user data
        return jsonify({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi lấy thông tin người dùng: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_api.route('/users/<username>/exists', methods=['GET'])
def check_username_exists(username):
    """Check if username exists"""
    try:
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            return jsonify({"exists": user is not None}), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Lỗi kiểm tra tên người dùng: {str(e)}")
        return jsonify({"error": str(e)}), 500 