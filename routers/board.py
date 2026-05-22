from datetime import datetime
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, SubStage, Task
from routers.auth import get_current_user
from services.backup_service import run_backup_if_needed
from jinja2 import Environment, FileSystemLoader

templates_env = Environment(loader=FileSystemLoader("templates"))
router = APIRouter(tags=["board"])

@router.get("/", response_class=HTMLResponse)
def get_board(
    request: Request,
    q: str = Query(None, description="Search query"),
    assignee_id: str = Query(None, description="Assignee filter"),
    priority: str = Query(None, description="Priority filter"),
    sort_by: str = Query("created_desc", description="Sorting filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    # Check if backup needs to run automatically
    try:
        run_backup_if_needed()
    except Exception as e:
        print(f"Auto-backup warning: {e}")
        
    # Fetch lists of users and sub-stages
    users = db.query(User).filter(User.is_active == True).all()
    sub_stages = db.query(SubStage).order_by(SubStage.display_order.asc()).all()
    
    # Base task query
    task_query = db.query(Task)
    
    # Filter by search string
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        task_query = task_query.filter(
            (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
        )
        
    # Filter by assignee
    if assignee_id:
        if assignee_id == "none":
            task_query = task_query.filter(Task.assignee_id == None)
        elif assignee_id != "all":
            try:
                task_query = task_query.filter(Task.assignee_id == int(assignee_id))
            except ValueError:
                pass
                
    # Filter by priority
    if priority and priority != "all":
        task_query = task_query.filter(Task.priority == priority)
        
    # Sorting
    if sort_by == "created_asc":
        task_query = task_query.order_by(Task.created_at.asc())
    elif sort_by == "created_desc":
        task_query = task_query.order_by(Task.created_at.desc())
    elif sort_by == "due_asc":
        # Put null due dates at the end
        task_query = task_query.order_by(Task.due_date.asc().nulls_last())
    elif sort_by == "due_desc":
        task_query = task_query.order_by(Task.due_date.desc().nulls_last())
    elif sort_by == "priority_desc":
        # Manual priority order could be sorted, let's sorting by ordering
        # low < medium < high, in SQL we can do case statement, let's keep it simple
        # or just sort in Python, or sort by standard string
        task_query = task_query.order_by(Task.priority.desc())
    else:
        task_query = task_query.order_by(Task.created_at.desc())
        
    all_filtered_tasks = task_query.all()
    
    # Categorize tasks for the board
    tasks_new = [t for t in all_filtered_tasks if t.status == "new"]
    tasks_completed = [t for t in all_filtered_tasks if t.status == "completed"]
    
    # Map each sub-stage ID to its list of tasks
    tasks_by_sub_stage = {stage.id: [] for stage in sub_stages}
    tasks_in_progress_no_stage = [] # fallback
    
    for t in all_filtered_tasks:
        if t.status == "in_progress":
            if t.sub_stage_id in tasks_by_sub_stage:
                tasks_by_sub_stage[t.sub_stage_id].append(t)
            else:
                tasks_in_progress_no_stage.append(t)
                
    # If a task is in progress but has NO sub_stage assigned, auto-assign it to the first sub-stage
    if tasks_in_progress_no_stage and sub_stages:
        first_stage_id = sub_stages[0].id
        for t in tasks_in_progress_no_stage:
            t.sub_stage_id = first_stage_id
            tasks_by_sub_stage[first_stage_id].append(t)
        db.commit()

    today_str = datetime.now().strftime("%Y-%m-%d")
    template = templates_env.get_template("board.html")
    return HTMLResponse(template.render(
        request=request,
        current_user=current_user,
        users=users,
        sub_stages=sub_stages,
        tasks_new=tasks_new,
        tasks_completed=tasks_completed,
        tasks_by_sub_stage=tasks_by_sub_stage,
        q=q or "",
        assignee_id=assignee_id or "all",
        priority=priority or "all",
        sort_by=sort_by or "created_desc",
        today_str=today_str
    ))
