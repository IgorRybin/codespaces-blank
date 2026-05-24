import os
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from config import Config
from models import User, SubStage, hash_password
from routers import auth, board, tasks, admin

# Auto create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kanban Board API",
    description="Kanban Board for small teams",
    version="1.0.0"
)

# Create static folder if not exists
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)
    
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database seeding logic on startup
def seed_database():
    db = SessionLocal()
    try:
        # Seed Users
        if db.query(User).count() == 0:
            print("[Seed] No users found. Initializing seed users...")
            seed_users = [
                {"username": "admin", "full_name": "Иван Иванов (Админ)", "color": "indigo"},
                {"username": "pavel", "full_name": "Павел Петров (Разработчик)", "color": "emerald"},
                {"username": "elena", "full_name": "Елена Сидорова (Дизайнер)", "color": "rose"},
                {"username": "dmitry", "full_name": "Дмитрий Козлов (Тестировщик)", "color": "amber"},
                {"username": "anna", "full_name": "Анна Морозова (Менеджер)", "color": "violet"}
            ]
            for u_data in seed_users:
                # Password equals to username
                hashed_pw = hash_password(u_data["username"])
                user = User(
                    username=u_data["username"],
                    password_hash=hashed_pw,
                    full_name=u_data["full_name"],
                    color=u_data["color"],
                    is_active=True
                )
                db.add(user)
            db.commit()
            print("[Seed] Seed users loaded successfully.")
            
        # Seed SubStages inside "В работе"
        if db.query(SubStage).count() == 0:
            print("[Seed] No sub-stages found. Initializing sub-stages...")
            
            # Retrieve generated users to link default assignees
            elena = db.query(User).filter(User.username == "elena").first()
            pavel = db.query(User).filter(User.username == "pavel").first()
            dmitry = db.query(User).filter(User.username == "dmitry").first()
            
            seed_stages = [
                {"name": "Дизайн", "display_order": 10, "default_assignee_id": elena.id if elena else None},
                {"name": "Разработка", "display_order": 20, "default_assignee_id": pavel.id if pavel else None},
                {"name": "Проверка кода", "display_order": 30, "default_assignee_id": pavel.id if pavel else None},
                {"name": "Тестирование", "display_order": 40, "default_assignee_id": dmitry.id if dmitry else None}
            ]
            for s_data in seed_stages:
                stage = SubStage(
                    name=s_data["name"],
                    display_order=s_data["display_order"],
                    default_assignee_id=s_data["default_assignee_id"]
                )
                db.add(stage)
            db.commit()
            print("[Seed] Default sub-stages inside 'В работе' built.")
            
    except Exception as e:
        print(f"[Seed] Error seeding database: {e}")
    finally:
        db.close()

seed_database()

# Register Routers
app.include_router(auth.router)
app.include_router(board.router)
app.include_router(tasks.router)
app.include_router(admin.router)

# Basic Redirect root to Board
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
