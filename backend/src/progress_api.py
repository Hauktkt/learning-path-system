import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import joinedload

from src.database import SessionLocal, User, LearningPath, Task, Progress
from src.auth_api import get_user_from_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('progress.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create blueprint
progress_api = Blueprint('progress_api', __name__, url_prefix='/api/progress')

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

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

@progress_api.route('/learning-paths', methods=['GET'])
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

@progress_api.route('/learning-paths/<int:path_id>', methods=['GET'])
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

@progress_api.route('/learning-paths/<int:path_id>/save', methods=['POST'])
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
                phase_index = min(len(phases) - 1, daily_plan.index(day) // (total_days // len(phases)))
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

@progress_api.route('/tasks/<int:task_id>/toggle', methods=['POST'])
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

@progress_api.route('/tasks/<int:task_id>/notes', methods=['POST'])
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

@progress_api.route('/stats/weekly', methods=['GET'])
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