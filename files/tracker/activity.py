from flask import session, request
from sqlalchemy import text

def log_activity(action, target=None, status="success"):
    """Log user activity to database using SQLAlchemy."""
    # Import here to avoid circular imports
    from app import db

    user_id = session.get("user_id")
    if not user_id:
        return

    try:
        db.session.execute(text("""
            INSERT INTO activity_logs
            (user_id, action, target, status, ip_address, user_agent)
            VALUES (:user_id, :action, :target, :status, :ip_address, :user_agent)
        """), {
            "user_id": user_id,
            "action": action,
            "target": target,
            "status": status,
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent")
        })
        db.session.commit()
    except Exception as e:
        # Don't let logging failures break the app
        print(f"Activity logging failed: {e}")
        db.session.rollback()
