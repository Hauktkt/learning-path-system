import os
import json
import time
import sys
import io
import secrets
import logging
from datetime import datetime, timedelta
from flask import Flask, Blueprint, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import joinedload
from dotenv import load_dotenv

from src.database import SessionLocal, User, LearningPath, Task, Progress
from src.rag_system import LearningPathRAG

# Cấu hình encoding cho console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Tạo Flask app
app = Flask(__name__)
# Cấu hình CORS cho tất cả các routes
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True, "allow_headers": ["Content-Type", "Authorization"]}})

# In thông báo về cấu hình CORS để debug
print("=== CORS Configuration ===")
print("Origins: '*' (Allow all)")
print("Headers: 'Content-Type', 'Authorization'")
print("Credentials: True")
print("==========================")

# Token management (simple version - consider using JWT in production)
active_tokens = {}  # Maps token -> user_id

# Load biến môi trường
load_dotenv()

# Thiết lập GOOGLE_API_KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    # Sử dụng Google API key cố định để test
    print("CẢNH BÁO: Không tìm thấy GOOGLE_API_KEY hợp lệ. Vui lòng đặt API key trong file .env")
    
    # Nếu không có key thật, hãy sử dụng key test
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        if "GOOGLE_API_KEY=" not in content or "GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE" in content:
            with open(".env", "a", encoding="utf-8") as f:
                f.write("\n# Thêm API key thật của bạn vào đây\nGOOGLE_API_KEY=AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4\n")
            print("Đã thêm API key test vào file .env. Vui lòng thay thế bằng API key thật của bạn.")
            os.environ["GOOGLE_API_KEY"] = "AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4"
    else:
        with open(".env", "w", encoding="utf-8") as f:
            f.write("COHERE_API_KEY=" + os.getenv("COHERE_API_KEY", "") + "\n")
            f.write("GOOGLE_API_KEY=AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4\n")
        print("Đã tạo file .env với API key test. Vui lòng thay thế bằng API key thật của bạn.")
        os.environ["GOOGLE_API_KEY"] = "AIzaSyDaRTFCx2MrGqaqVE_l0AB8TX-iu1Xu0V4"
else:
    print(f"Đã tìm thấy GOOGLE_API_KEY: {GOOGLE_API_KEY[:5]}...")

# Khởi tạo RAG system
try:
    rag_system = LearningPathRAG(cohere_api_key=os.getenv("COHERE_API_KEY"))
    print("Khởi tạo RAG system thành công!")
except Exception as e:
    print(f"Lỗi khởi tạo RAG system: {str(e)}")
    rag_system = None

# Helper functions
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

def get_authenticated_user():
    """Helper to get authenticated user from request"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
        
    token = auth_header.split(' ')[1]
    return get_user_from_token(token)

def auth_required(f):
    """Decorator for routes that require authentication"""
    def decorated(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return f(user, *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# -----------------
# Auth API Routes
# -----------------

@app.route('/api/auth/register', methods=['POST'])
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

@app.route('/api/auth/login', methods=['POST'])
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

@app.route('/api/auth/logout', methods=['POST'])
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

@app.route('/api/auth/me', methods=['GET'])
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

@app.route('/api/auth/users/<username>/exists', methods=['GET'])
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

# -----------------
# Progress API Routes
# -----------------

@app.route('/api/progress/learning-paths', methods=['GET'])
@auth_required
def get_learning_paths(user):
    """Get all learning paths for the current user"""
    try:
        db = get_db()
        try:
            # Get learning paths
            learning_paths = db.query(LearningPath).filter(
                LearningPath.user_id == user.id
            ).order_by(
                desc(LearningPath.created_at)
            ).all()
            
            # Format response
            result = []
            for path in learning_paths:
                # Count completed tasks
                total_tasks = db.query(func.count(Task.id)).filter(
                    Task.learning_path_id == path.id
                ).scalar()
                
                completed_tasks = db.query(func.count(Task.id)).filter(
                    and_(
                        Task.learning_path_id == path.id,
                        Task.completed == True
                    )
                ).scalar()
                
                # Get progress
                progress_items = db.query(Progress).filter(
                    Progress.learning_path_id == path.id
                ).all()
                
                progress_data = []
                for p in progress_items:
                    progress_data.append({
                        "id": p.id,
                        "skill_name": p.skill_name,
                        "progress_percentage": p.progress_percentage,
                        "last_updated": p.last_updated.isoformat() if p.last_updated else None
                    })
                
                # Format path
                result.append({
                    "id": path.id,
                    "field": path.field,
                    "level": path.level,
                    "duration": path.duration,
                    "daily_hours": path.daily_hours,
                    "total_hours": path.total_hours,
                    "created_at": path.created_at.isoformat(),
                    "progress": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "completion_percentage": round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                        "skills": progress_data
                    }
                })
            
            return jsonify({"learning_paths": result}), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting learning paths: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress/learning-paths/<int:path_id>', methods=['GET'])
@auth_required
def get_learning_path(user, path_id):
    """Get a specific learning path with tasks and progress"""
    try:
        db = get_db()
        try:
            # Get learning path
            path = db.query(LearningPath).filter(
                and_(
                    LearningPath.id == path_id,
                    LearningPath.user_id == user.id
                )
            ).first()
            
            if not path:
                return jsonify({"error": "Lộ trình học tập không tồn tại hoặc không thuộc về bạn"}), 404
                
            # Get tasks grouped by phase
            tasks_by_phase = {}
            tasks = db.query(Task).filter(
                Task.learning_path_id == path.id
            ).order_by(
                Task.date
            ).all()
            
            for task in tasks:
                phase = task.phase
                if phase not in tasks_by_phase:
                    tasks_by_phase[phase] = []
                
                tasks_by_phase[phase].append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "date": task.date.isoformat() if task.date else None
                })
            
            # Get progress
            progress_items = db.query(Progress).filter(
                Progress.learning_path_id == path.id
            ).all()
            
            progress_data = []
            for p in progress_items:
                progress_data.append({
                    "id": p.id,
                    "skill_name": p.skill_name,
                    "progress_percentage": p.progress_percentage,
                    "last_updated": p.last_updated.isoformat() if p.last_updated else None
                })
            
            # Format response
            result = {
                "id": path.id,
                "field": path.field,
                "level": path.level,
                "duration": path.duration,
                "daily_hours": path.daily_hours,
                "total_hours": path.total_hours,
                "created_at": path.created_at.isoformat(),
                "tasks_by_phase": tasks_by_phase,
                "progress": progress_data
            }
            
            return jsonify({"learning_path": result}), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting learning path: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress/learning-paths/<int:path_id>/save', methods=['POST'])
@auth_required
def save_learning_path(user, path_id):
    """Save a learning path from RAG output to database"""
    try:
        data = request.json
        if 'learning_path' not in data:
            return jsonify({"error": "Missing learning_path data"}), 400
            
        path_data = data['learning_path']
        
        # Check if path exists or create new one
        db = get_db()
        try:
            # Check if we're updating an existing path or creating a new one
            existing_path = None
            if path_id > 0:
                existing_path = db.query(LearningPath).filter(
                    and_(
                        LearningPath.id == path_id,
                        LearningPath.user_id == user.id
                    )
                ).first()
                
            if existing_path:
                # Update existing path
                learning_path = existing_path
            else:
                # Create new path
                learning_path = LearningPath(
                    user_id=user.id,
                    created_at=datetime.utcnow()
                )
                db.add(learning_path)
            
            # Update path data
            learning_path.field = path_data.get('field', '')
            learning_path.level = path_data.get('level', '')
            learning_path.duration = path_data.get('duration', 0)
            learning_path.daily_hours = path_data.get('daily_hours', 0)
            
            # Calculate total hours
            total_days = len(path_data.get('daily_plan', []))
            total_hours = total_days * learning_path.daily_hours
            learning_path.total_hours = total_hours
            learning_path.total_days = total_days
            
            # Save path to get ID if new
            db.commit()
            db.refresh(learning_path)
            
            # Save tasks
            if existing_path:
                # Delete existing tasks
                db.query(Task).filter(Task.learning_path_id == learning_path.id).delete()
            
            # Process daily plan to create tasks
            daily_plan = path_data.get('daily_plan', [])
            phases = path_data.get('phases', [])
            phase_map = {}
            
            # Build phase map
            for i, phase in enumerate(phases):
                phase_map[i] = phase.get('name', f'Phase {i+1}')
            
            # Create tasks from daily plan
            for day in daily_plan:
                date_str = day.get('date')
                try:
                    task_date = datetime.fromisoformat(date_str)
                except (ValueError, TypeError):
                    # If date is invalid, use current date + days
                    task_date = datetime.utcnow() + timedelta(days=daily_plan.index(day))
                
                # Determine phase based on date
                phase_index = min(len(phases) - 1, daily_plan.index(day) // (total_days // max(len(phases), 1)))
                phase_name = phase_map.get(phase_index, f'Phase {phase_index+1}')
                
                # Create tasks for this day
                for task_desc in day.get('tasks', []):
                    task = Task(
                        learning_path_id=learning_path.id,
                        user_id=user.id,
                        title=task_desc[:50] if len(task_desc) > 50 else task_desc,
                        description=task_desc,
                        completed=False,
                        date=task_date,
                        phase=phase_name,
                        created_at=datetime.utcnow()
                    )
                    db.add(task)
            
            # Save skills progress placeholders
            if existing_path:
                # Only create new if none exist
                existing_progress = db.query(Progress).filter(
                    Progress.learning_path_id == learning_path.id
                ).count()
                
                if existing_progress == 0:
                    # Create initial progress entries for skills
                    for phase in phases:
                        progress = Progress(
                            user_id=user.id,
                            learning_path_id=learning_path.id,
                            skill_name=phase.get('name', 'Unknown skill'),
                            progress_percentage=0,
                            last_updated=datetime.utcnow()
                        )
                        db.add(progress)
            else:
                # Create initial progress entries for skills
                for phase in phases:
                    progress = Progress(
                        user_id=user.id,
                        learning_path_id=learning_path.id,
                        skill_name=phase.get('name', 'Unknown skill'),
                        progress_percentage=0,
                        last_updated=datetime.utcnow()
                    )
                    db.add(progress)
            
            db.commit()
            
            return jsonify({
                "message": "Lộ trình học tập đã được lưu thành công",
                "path_id": learning_path.id
            }), 200
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving learning path: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error saving learning path: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress/tasks/<int:task_id>/toggle', methods=['POST'])
@auth_required
def toggle_task(user, task_id):
    """Toggle task completion status"""
    try:
        db = get_db()
        try:
            # Get task
            task = db.query(Task).filter(
                and_(
                    Task.id == task_id,
                    Task.user_id == user.id
                )
            ).first()
            
            if not task:
                return jsonify({"error": "Task không tồn tại hoặc không thuộc về bạn"}), 404
                
            # Toggle completion
            task.completed = not task.completed
            db.commit()
            
            # Update skill progress
            # Get all tasks for this phase
            tasks_in_phase = db.query(Task).filter(
                and_(
                    Task.learning_path_id == task.learning_path_id,
                    Task.phase == task.phase
                )
            ).all()
            
            # Calculate completion percentage
            total_tasks = len(tasks_in_phase)
            completed_tasks = sum(1 for t in tasks_in_phase if t.completed)
            completion_percentage = round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Update progress
            progress = db.query(Progress).filter(
                and_(
                    Progress.learning_path_id == task.learning_path_id,
                    Progress.skill_name == task.phase
                )
            ).first()
            
            if progress:
                progress.progress_percentage = completion_percentage
                progress.last_updated = datetime.utcnow()
            else:
                # Create new progress
                progress = Progress(
                    user_id=user.id,
                    learning_path_id=task.learning_path_id,
                    skill_name=task.phase,
                    progress_percentage=completion_percentage,
                    last_updated=datetime.utcnow()
                )
                db.add(progress)
                
            db.commit()
            
            return jsonify({
                "task": {
                    "id": task.id,
                    "completed": task.completed
                },
                "progress": {
                    "skill_name": task.phase,
                    "progress_percentage": completion_percentage
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error toggling task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress/tasks/<int:task_id>/notes', methods=['POST'])
@auth_required
def update_task_notes(user, task_id):
    """Update task notes"""
    try:
        data = request.json
        if 'notes' not in data:
            return jsonify({"error": "Missing notes field"}), 400
            
        db = get_db()
        try:
            # Get task
            task = db.query(Task).filter(
                and_(
                    Task.id == task_id,
                    Task.user_id == user.id
                )
            ).first()
            
            if not task:
                return jsonify({"error": "Task không tồn tại hoặc không thuộc về bạn"}), 404
                
            # Update notes - add to description
            notes = data['notes']
            if task.description and not task.description.endswith(notes):
                task.description = f"{task.description}\n\nGhi chú: {notes}"
            else:
                task.description = f"{task.description or ''}\n\nGhi chú: {notes}"
                
            db.commit()
            
            return jsonify({
                "task": {
                    "id": task.id,
                    "description": task.description
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating task notes: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress/stats/weekly', methods=['GET'])
@auth_required
def get_weekly_stats(user):
    """Get weekly learning stats"""
    try:
        db = get_db()
        try:
            # Calculate dates for the past week
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)
            
            # Get completed tasks by day
            stats_by_day = []
            for i in range(7):
                date = week_ago + timedelta(days=i+1)
                day_start = datetime.combine(date, datetime.min.time())
                day_end = datetime.combine(date, datetime.max.time())
                
                # Count tasks completed on this day
                completed_count = db.query(func.count(Task.id)).filter(
                    and_(
                        Task.user_id == user.id,
                        Task.completed == True,
                        Task.date >= day_start,
                        Task.date <= day_end
                    )
                ).scalar()
                
                stats_by_day.append({
                    "date": date.isoformat(),
                    "day_of_week": date.strftime("%A"),
                    "completed_tasks": completed_count
                })
            
            # Calculate overall stats
            total_paths = db.query(func.count(LearningPath.id)).filter(
                LearningPath.user_id == user.id
            ).scalar()
            
            total_tasks = db.query(func.count(Task.id)).filter(
                Task.user_id == user.id
            ).scalar()
            
            completed_tasks = db.query(func.count(Task.id)).filter(
                and_(
                    Task.user_id == user.id,
                    Task.completed == True
                )
            ).scalar()
            
            # Get streak (consecutive days with completed tasks)
            streak = 0
            current_date = today
            while True:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                
                completed = db.query(func.count(Task.id)).filter(
                    and_(
                        Task.user_id == user.id,
                        Task.completed == True,
                        Task.date >= day_start,
                        Task.date <= day_end
                    )
                ).scalar()
                
                if completed > 0:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return jsonify({
                "daily_stats": stats_by_day,
                "overall_stats": {
                    "total_paths": total_paths,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_percentage": round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    "current_streak": streak
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting weekly stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

# -----------------
# Learning Path API Routes
# -----------------

@app.route('/api/learning-path', methods=['POST'])
def create_learning_path():
    """API endpoint để tạo lộ trình học tập"""
    try:
        # Kiểm tra RAG system
        if rag_system is None:
            return jsonify({"error": "RAG system chưa được khởi tạo"}), 500
        
        # Lấy dữ liệu từ request
        data = request.json
        username = request.args.get('username', 'anonymous')
        
        # Kiểm tra dữ liệu
        required_fields = ['field', 'level', 'duration', 'daily_hours', 'interests']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Thiếu trường {field}"}), 400
        
        print(f"Nhận được yêu cầu tạo lộ trình học tập từ {username}: {data['field']}, {data['level']}")
        
        # Gọi RAG system để tạo lộ trình
        start_time = time.time()
        learning_path = rag_system.create_learning_path(
            field=data['field'],
            level=data['level'],
            duration=data['duration'],
            daily_hours=data['daily_hours'],
            interests=data['interests']
        )
        elapsed_time = time.time() - start_time
        print(f"Tạo lộ trình học tập hoàn tất trong {elapsed_time:.2f} giây")
        
        # Lưu kết quả vào file để debug
        try:
            save_path = f"learning_path_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(learning_path, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu lộ trình học tập vào file {save_path}")
        except Exception as e:
            print(f"Không thể lưu lộ trình học tập: {str(e)}")
        
        # Kiểm tra xem có phải là fallback không
        if "learning_path" in learning_path and learning_path["learning_path"].get("is_fallback", False):
            print(f"Cảnh báo: Sử dụng lộ trình dự phòng - {learning_path['learning_path'].get('fallback_reason', 'Unknown')}")
        
        return jsonify(learning_path), 200
        
    except Exception as e:
        print(f"Lỗi xử lý request: {str(e)}")
        return jsonify({"error": str(e)}), 500

# -----------------
# Utility API Routes
# -----------------

@app.route('/health', methods=['GET'])
def health_check():
    """API endpoint để kiểm tra trạng thái"""
    return jsonify({
        "status": "ok", 
        "rag_system": rag_system is not None,
        "version": "1.1.0",
        "features": ["authentication", "learning_path", "progress_tracking"]
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Trang chủ"""
    return """
    <html>
        <head>
            <title>API Tạo Lộ Trình Học Tập</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                code { background: #f8f8f8; padding: 2px 4px; border-radius: 4px; }
                pre { background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
                button { background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
                button:hover { background: #2980b9; }
                #result { white-space: pre-wrap; background: #f8f8f8; padding: 10px; border-radius: 4px; display: none; }
                .endpoint { border-left: 4px solid #3498db; padding-left: 15px; margin-bottom: 20px; }
                .new { background-color: #e8f7f0; border-radius: 4px; padding: 2px 5px; color: #27ae60; font-size: 12px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>API Tạo Lộ Trình Học Tập</h1>
            <p>Hệ thống API cung cấp các tính năng tạo lộ trình học tập cá nhân hóa, quản lý tài khoản và theo dõi tiến độ học tập.</p>
            
            <h2>1. Lộ Trình Học Tập</h2>
            <div class="endpoint">
                <p><code>POST /api/learning-path</code> - Tạo lộ trình học tập mới</p>
                <pre>
{
  "field": "Python programming",
  "level": "Beginner",
  "duration": 3,
  "daily_hours": 2,
  "interests": ["Web Development", "Data Science"]
}
                </pre>
            </div>
            
            <h2>2. Xác Thực</h2>
            <div class="endpoint">
                <p><code>POST /api/auth/register</code> - Đăng ký tài khoản mới</p>
                <pre>
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password"
}
                </pre>
            </div>
            <div class="endpoint">
                <p><code>POST /api/auth/login</code> - Đăng nhập</p>
                <pre>
{
  "username": "example_user",
  "password": "secure_password"
}
                </pre>
            </div>
            <div class="endpoint">
                <p><code>POST /api/auth/logout</code> - Đăng xuất</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            
            <h2>3. Theo Dõi Tiến Độ</h2>
            <div class="endpoint">
                <p><code>GET /api/progress/learning-paths</code> - Lấy danh sách lộ trình của người dùng</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>GET /api/progress/learning-paths/{path_id}</code> - Xem chi tiết một lộ trình cụ thể</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>POST /api/progress/tasks/{task_id}/toggle</code> - Đánh dấu hoàn thành/chưa hoàn thành</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            <div class="endpoint">
                <p><code>GET /api/progress/stats/weekly</code> - Xem thống kê học tập theo tuần</p>
                <p>Yêu cầu header: <code>Authorization: Bearer {token}</code></p>
            </div>
            
            <h2>Test nhanh:</h2>
            <button onclick="testAPI()">Tạo lộ trình Python cho người mới</button>
            <div id="loading" style="display:none; margin-top: 10px;">Đang xử lý, vui lòng đợi...</div>
            <pre id="result"></pre>
            
            <script>
                function testAPI() {
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('result').style.display = 'none';
                    
                    fetch('/api/learning-path?username=test_user', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            field: "Python programming",
                            level: "Beginner",
                            duration: 3,
                            daily_hours: 2,
                            interests: ["Web Development", "Data Science"]
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                    })
                    .catch(error => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').textContent = 'Error: ' + error;
                    });
                }
            </script>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("=== Khởi động Unified API Service ===")
    print(f"GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY', 'NOT_SET')[:5]}...")
    print(f"COHERE_API_KEY: {os.environ.get('COHERE_API_KEY', 'NOT_SET')[:5]}...")
    print("Có thể truy cập API tại: http://localhost:5000")
    print("Các tính năng: Xác thực người dùng, Lộ trình học tập, Theo dõi tiến độ")
    app.run(debug=True, port=5000, host='0.0.0.0') 