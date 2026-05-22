from fastapi import APIRouter, Depends, Form, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
import os

from database import get_db
from models import User, SubStage, Task, hash_password
from routers.auth import get_current_user
from services.backup_service import create_backup, list_backups
from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader("templates"))
router = APIRouter(prefix="/admin", tags=["admin"])

def get_redirect_with_token(request: Request, url: str = "/") -> RedirectResponse:
    token = request.query_params.get("token")
    if token:
        connector = "&" if "?" in url else "?"
        return RedirectResponse(url=f"{url}{connector}token={token}", status_code=303)
    return RedirectResponse(url=url, status_code=303)

@router.get("", response_class=HTMLResponse)
def get_admin_dashboard(
    request: Request,
    message: str = None,
    error: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    users = db.query(User).all()
    sub_stages = db.query(SubStage).order_by(SubStage.display_order.asc()).all()
    backups = list_backups()
    
    template = templates_env.get_template("admin.html")
    return HTMLResponse(template.render(
        request=request,
        current_user=current_user,
        users=users,
        sub_stages=sub_stages,
        backups=backups,
        message=message,
        error=error
    ))


@router.post("/users/create")
def admin_create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    color: str = Form("blue"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    username_cleaned = username.strip().lower()
    if not username_cleaned or not password.strip() or not full_name.strip():
        return get_redirect_with_token(request, "/admin?error=Все поля обязательны для заполнения")
        
    # Check if username exists
    existing = db.query(User).filter(User.username == username_cleaned).first()
    if existing:
        return get_redirect_with_token(request, "/admin?error=Пользователь с таким логином уже существует")
        
    # Create user
    new_user = User(
        username=username_cleaned,
        password_hash=hash_password(password.strip()),
        full_name=full_name.strip(),
        color=color,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    
    return get_redirect_with_token(request, "/admin?message=Пользователь успешно создан!")


@router.post("/sub-stages/create")
def admin_create_sub_stage(
    request: Request,
    name: str = Form(...),
    display_order: int = Form(0),
    default_assignee_id: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    name = name.strip()
    if not name:
        return get_redirect_with_token(request, "/admin?error=Название этапа не может быть пустым")
        
    parsed_assignee_id = None
    if default_assignee_id and default_assignee_id != "none":
        parsed_assignee_id = int(default_assignee_id)
        
    new_stage = SubStage(
        name=name,
        display_order=display_order,
        default_assignee_id=parsed_assignee_id
    )
    db.add(new_stage)
    db.commit()
    
    return get_redirect_with_token(request, "/admin?message=Подэтап в работе успешно создан!")


@router.post("/sub-stages/{id}/edit")
def admin_edit_sub_stage(
    id: int,
    request: Request,
    name: str = Form(...),
    display_order: int = Form(0),
    default_assignee_id: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    stage = db.query(SubStage).filter(SubStage.id == id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Этап не найден")
        
    name = name.strip()
    if not name:
        return get_redirect_with_token(request, "/admin?error=Название этапа не может быть пустым")
        
    parsed_assignee_id = None
    if default_assignee_id and default_assignee_id != "none":
        parsed_assignee_id = int(default_assignee_id)
        
    stage.name = name
    stage.display_order = display_order
    stage.default_assignee_id = parsed_assignee_id
    
    db.commit()
    return get_redirect_with_token(request, "/admin?message=Этап успешно отредактирован!")


@router.post("/sub-stages/{id}/delete")
def admin_delete_sub_stage(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    stage = db.query(SubStage).filter(SubStage.id == id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Этап не найден")
        
    # Re-assign or orphan any task that belongs to this stage
    db.query(Task).filter(Task.sub_stage_id == id).update({Task.sub_stage_id: None, Task.status: "new"})
    db.delete(stage)
    db.commit()
    
    return get_redirect_with_token(request, "/admin?message=Подэтап удален. Задачи перенесены в статус 'Новые'")


@router.post("/backup/create")
def trigger_admin_backup(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
        
    try:
        path = create_backup("database.db")
        return get_redirect_with_token(request, f"/admin?message=Резервная копия успешно создана в: {os.path.basename(path)}")
    except Exception as e:
        return get_redirect_with_token(request, f"/admin?error=Ошибка резервного копирования: {str(e)}")


@router.get("/backup/download/{filename}")
def download_backup_file(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/auth/login")
        
    # Security prevent directory traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("backups", safe_filename)
    
    if os.path.exists(filepath):
        return FileResponse(
            path=filepath,
            filename=safe_filename,
            media_type="application/octet-stream"
        )
    raise HTTPException(status_code=404, detail="Backup file not found")
