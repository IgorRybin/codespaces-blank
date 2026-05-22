from fastapi import APIRouter, Depends, Form, Request, HTTPException, Body, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os

from database import get_db
from models import User, SubStage, Task, Comment, TaskHistory
from routers.auth import get_current_user
from services.excel_service import export_tasks_to_excel
from services.backup_service import create_backup, list_backups
from config import Config
from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader("templates"))
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Helper to log history
def log_history(db: Session, task_id: int, user_id: int, action: str, details: str):
    history_entry = TaskHistory(
        task_id=task_id,
        user_id=user_id,
        action=action,
        details=details,
        created_at=datetime.utcnow()
    )
    db.add(history_entry)
    db.commit()

def get_redirect_with_token(request: Request, url: str = "/") -> RedirectResponse:
    token = request.query_params.get("token")
    if token:
        connector = "&" if "?" in url else "?"
        return RedirectResponse(url=f"{url}{connector}token={token}", status_code=303)
    return RedirectResponse(url=url, status_code=303)

@router.post("/create")
def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    priority: str = Form("medium"),
    due_date: str = Form(None),
    assignee_id: str = Form(None),
    sub_stage_id: str = Form(None),
    status: str = Form("new"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    # Process Assignee
    parsed_assignee_id = None
    if assignee_id and assignee_id != "none":
        parsed_assignee_id = int(assignee_id)
        
    # Process SubStage
    parsed_sub_stage_id = None
    if status == "in_progress":
        if sub_stage_id and sub_stage_id != "none":
            parsed_sub_stage_id = int(sub_stage_id)
        else:
            # Fallback to first available sub-stage if placing in Work
            first_stage = db.query(SubStage).order_by(SubStage.display_order.asc()).first()
            if first_stage:
                parsed_sub_stage_id = first_stage.id
                
    completed_at = datetime.utcnow() if status == "completed" else None
    
    # Create Task
    task = Task(
        title=title.strip(),
        description=description.strip() if description else None,
        priority=priority,
        due_date=due_date if due_date else None,
        assignee_id=parsed_assignee_id,
        status=status,
        sub_stage_id=parsed_sub_stage_id,
        creator_id=current_user.id,
        completed_at=completed_at,
        created_at=datetime.utcnow()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Setup history log
    log_history(
        db=db,
        task_id=task.id,
        user_id=current_user.id,
        action="Создание задачи",
        details=f"Задача создана со статусом '{status}'."
    )
    
    # Auto-assign if entering sub-stage immediately and default assignee exists
    if status == "in_progress" and parsed_sub_stage_id and not parsed_assignee_id:
        sub_stage = db.query(SubStage).filter(SubStage.id == parsed_sub_stage_id).first()
        if sub_stage and sub_stage.default_assignee_id:
            task.assignee_id = sub_stage.default_assignee_id
            db.commit()
            log_history(
                db=db,
                task_id=task.id,
                user_id=current_user.id,
                action="Смена исполнителя",
                details=f"Исполнитель назначен автоматически (по умолчанию для этапа '{sub_stage.name}'): {sub_stage.default_assignee.full_name}"
            )
            
    return get_redirect_with_token(request, "/")


@router.get("/{id}")
def get_task_details(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provides complete task details to render inside the slide-over or modal."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
        
    users = db.query(User).filter(User.is_active == True).all()
    sub_stages = db.query(SubStage).order_by(SubStage.display_order.asc()).all()
    
    template = templates_env.get_template("partials/task_details.html")
    return HTMLResponse(template.render(
        task=task,
        users=users,
        sub_stages=sub_stages,
        current_user=current_user
    ))


@router.post("/{id}/edit")
def edit_task(
    id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    priority: str = Form("medium"),
    due_date: str = Form(None),
    assignee_id: str = Form(None),
    status: str = Form("new"),
    sub_stage_id: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
        
    # Store old values for intelligent history logging
    changes = []
    
    # 1. Title change
    if task.title != title.strip():
        changes.append(f"Заголовок: '{task.title}' ➝ '{title.strip()}'")
        task.title = title.strip()
        
    # 2. Description change
    old_desc = task.description or ""
    new_desc = description.strip() if description else ""
    if old_desc != new_desc:
        changes.append("Описание было обновлено")
        task.description = new_desc if new_desc else None
        
    # 3. Priority change
    priority_map = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}
    if task.priority != priority:
        changes.append(f"Приоритет: {priority_map.get(task.priority, task.priority)} ➝ {priority_map.get(priority, priority)}")
        task.priority = priority
        
    # 4. Due date change
    old_due = task.due_date or "Не указано"
    new_due = due_date if due_date else "Не указано"
    if old_due != new_due:
        changes.append(f"Срок: {old_due} ➝ {new_due}")
        task.due_date = due_date if due_date else None
        
    # 5. Assignee change
    parsed_assignee_id = None
    if assignee_id and assignee_id != "none":
        parsed_assignee_id = int(assignee_id)
        
    if task.assignee_id != parsed_assignee_id:
        old_user = task.assignee.full_name if task.assignee else "Не назначен"
        new_user = "Не назначен"
        if parsed_assignee_id:
            db_user = db.query(User).filter(User.id == parsed_assignee_id).first()
            if db_user:
                new_user = db_user.full_name
        changes.append(f"Исполнитель: {old_user} ➝ {new_user}")
        task.assignee_id = parsed_assignee_id
        
    # 6. Status and SubStage transition check
    old_status = task.status
    old_sub_stage_id = task.sub_stage_id
    
    parsed_sub_stage_id = None
    if status == "in_progress":
        if sub_stage_id and sub_stage_id != "none":
            parsed_sub_stage_id = int(sub_stage_id)
        else:
            first_stage = db.query(SubStage).order_by(SubStage.display_order.asc()).first()
            if first_stage:
                parsed_sub_stage_id = first_stage.id
                
    task.sub_stage_id = parsed_sub_stage_id
    task.status = status
    
    # Handle completion timestamp
    if status == "completed" and old_status != "completed":
        task.completed_at = datetime.utcnow()
    elif status != "completed" and old_status == "completed":
        task.completed_at = None
        
    status_map = {"new": "Новая", "in_progress": "В работе", "completed": "Завершено"}
    if old_status != status:
        changes.append(f"Статус: {status_map.get(old_status, old_status)} ➝ {status_map.get(status, status)}")
    elif status == "in_progress" and old_sub_stage_id != parsed_sub_stage_id:
        old_stage = db.query(SubStage).filter(SubStage.id == old_sub_stage_id).first() if old_sub_stage_id else None
        new_stage = db.query(SubStage).filter(SubStage.id == parsed_sub_stage_id).first() if parsed_sub_stage_id else None
        old_stage_name = old_stage.name if old_stage else "Нет"
        new_stage_name = new_stage.name if new_stage else "Нет"
        changes.append(f"Этап в работе: {old_stage_name} ➝ {new_stage_name}")
        
    db.commit()
    
    # Log any findings 
    if changes:
        log_history(
            db=db,
            task_id=task.id,
            user_id=current_user.id,
            action="Редактирование задачи",
            details="; ".join(changes)
        )
        
    return get_redirect_with_token(request, "/")


@router.post("/{id}/move")
def move_task(
    id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dynamic Drag-And-Drop endpoint supporting state transitions with history log.
    
    Expects JSON like: {"status": "in_progress", "sub_stage_id": 3}
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
        
    status = payload.get("status", "new")
    sub_stage_id = payload.get("sub_stage_id")
    
    old_status = task.status
    old_sub_stage_id = task.sub_stage_id
    
    task.status = status
    
    # Handle completed timestamp
    if status == "completed":
        task.sub_stage_id = None
        if old_status != "completed":
            task.completed_at = datetime.utcnow()
    elif status == "new":
        task.sub_stage_id = None
        task.completed_at = None
    elif status == "in_progress":
        task.completed_at = None
        if sub_stage_id:
            task.sub_stage_id = int(sub_stage_id)
        else:
            # automatic select first sub-stage
            first_stage = db.query(SubStage).order_by(SubStage.display_order.asc()).first()
            if first_stage:
                task.sub_stage_id = first_stage.id
                
    db.commit()
    
    # Create descriptive log of drag modifications
    action_description = ""
    status_map = {"new": "Новая", "in_progress": "В работе", "completed": "Завершено"}
    
    if old_status != task.status:
        action_description = f"Перемещено из '{status_map.get(old_status)}' в '{status_map.get(task.status)}'"
        if task.status == "in_progress" and task.sub_stage_id:
            stage = db.query(SubStage).filter(SubStage.id == task.sub_stage_id).first()
            if stage:
                action_description += f" (Этап: {stage.name})"
    elif task.status == "in_progress" and old_sub_stage_id != task.sub_stage_id:
        old_stage = db.query(SubStage).filter(SubStage.id == old_sub_stage_id).first() if old_sub_stage_id else None
        new_stage = db.query(SubStage).filter(SubStage.id == task.sub_stage_id).first() if task.sub_stage_id else None
        old_name = old_stage.name if old_stage else "Нет"
        new_name = new_stage.name if new_stage else "Нет"
        action_description = f"Перемещено по этапам в работе: {old_name} ➝ {new_name}"
        
    if action_description:
        log_history(
            db=db,
            task_id=task.id,
            user_id=current_user.id,
            action="Смена статуса (drag-n-drop)",
            details=action_description
        )
        
    # Trigger auto-assign if entering a sub_stage and currently unassigned
    if task.status == "in_progress" and task.sub_stage_id and not task.assignee_id:
        sub_stage = db.query(SubStage).filter(SubStage.id == task.sub_stage_id).first()
        if sub_stage and sub_stage.default_assignee_id:
            task.assignee_id = sub_stage.default_assignee_id
            db.commit()
            log_history(
                db=db,
                task_id=task.id,
                user_id=current_user.id,
                action="Смена исполнителя",
                details=f"Исполнитель назначен автоматически по умолчанию для этапа '{sub_stage.name}': {sub_stage.default_assignee.full_name}"
            )
            
    return {"status": "success", "task_id": task.id}


@router.post("/{id}/comments")
def add_comment(
    id: int,
    request: Request,
    text: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    if not text.strip():
        return get_redirect_with_token(request, "/")
        
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
        
    comment = Comment(
        task_id=id,
        author_id=current_user.id,
        text=text.strip(),
        created_at=datetime.utcnow()
    )
    db.add(comment)
    db.commit()
    
    log_history(
        db=db,
        task_id=id,
        user_id=current_user.id,
        action="Добавление комментария",
        details=f'Добавлен комментарий: "{text.strip()[:60]}..."'
    )
    
    return get_redirect_with_token(request, "/")


@router.post("/{id}/delete")
def delete_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
        
    db.delete(task)
    db.commit()
    return get_redirect_with_token(request, "/")


@router.get("/action/export-excel")
def export_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates excel sheet of all tasks and downloads it."""
    if not current_user:
        return RedirectResponse(url="/auth/login")
        
    tasks = db.query(Task).order_by(Task.id.desc()).all()
    
    try:
        file_path = export_tasks_to_excel(tasks)
        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel: {e}")
