import base64
from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, verify_password, hash_password
from config import Config
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 templates for routes
templates_env = Environment(loader=FileSystemLoader("templates"))

router = APIRouter(prefix="/auth", tags=["auth"])

def encode_user_session(user_id: int) -> str:
    """Safely encodes user ID into custom session cookie."""
    return base64.b64encode(str(user_id).encode("utf-8")).decode("utf-8")

def decode_user_session(cookie_value: str) -> int | None:
    """Safely decodes user ID from custom session cookie."""
    if not cookie_value:
        return None
    try:
        decoded = base64.b64decode(cookie_value.encode("utf-8")).decode("utf-8")
        return int(decoded)
    except Exception:
        return None

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Dependency to retrieve the currently logged in user based on query params, headers, or cookies."""
    token = request.query_params.get("token")
    if not token:
        token = request.headers.get("X-Kanban-Token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get(Config.SESSION_COOKIE_NAME)
        
    if not token:
        return None
    user_id = decode_user_session(token)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()

@router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request, next: str = "/", current_user: User = Depends(get_current_user)):
    if current_user:
        redirect_url = next if next else "/"
        if "token" not in redirect_url and "?" not in redirect_url:
            cookie = request.cookies.get(Config.SESSION_COOKIE_NAME)
            if cookie:
                redirect_url = f"{redirect_url}?token={cookie}"
        return RedirectResponse(url=redirect_url, status_code=303)
    template = templates_env.get_template("login.html")
    return HTMLResponse(template.render(request=request, error=None, next_url=next))

@router.post("/login", response_class=HTMLResponse)
def handle_login(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username.strip().lower()).first()
    if not user or not verify_password(user.password_hash, password):
        template = templates_env.get_template("login.html")
        return HTMLResponse(template.render(request=request, error="Неверное имя пользователя или пароль", username=username, next_url=next))
    
    # Successful login, create simple session token
    session_val = encode_user_session(user.id)
    
    # Build redirect URL that propagates the token
    redirect_path = next if next else "/"
    if "?" in redirect_path:
        redirect_url = f"{redirect_path}&token={session_val}"
    else:
        redirect_url = f"{redirect_path}?token={session_val}"
        
    redirect_resp = RedirectResponse(url=redirect_url, status_code=303)
    
    # Detect if request is secure over HTTPS and set fallback cookies
    is_secure = request.headers.get("x-forwarded-proto") == "https" or request.url.scheme == "https"
    samesite_val = "none" if is_secure else "lax"
    
    redirect_resp.set_cookie(
        key=Config.SESSION_COOKIE_NAME,
        value=session_val,
        max_age=30 * 24 * 60 * 60, # 30 days
        httponly=True,
        samesite=samesite_val,
        secure=is_secure
    )
    return redirect_resp

@router.get("/logout")
def handle_logout(request: Request):
    # Redirect to login page with clear signal to wipe localStorage of the token
    redirect_resp = RedirectResponse(url="/auth/login?logout=1", status_code=303)
    
    is_secure = request.headers.get("x-forwarded-proto") == "https" or request.url.scheme == "https"
    samesite_val = "none" if is_secure else "lax"
    
    redirect_resp.delete_cookie(
        key=Config.SESSION_COOKIE_NAME,
        samesite=samesite_val,
        secure=is_secure
    )
    return redirect_resp
