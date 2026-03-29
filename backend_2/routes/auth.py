### this file handles authentication and user login functionality using jwt tokens and password hashing.
from models.models import * 
from pydantic import BaseModel, Field
from typing import Optional
router_auth = APIRouter(tags=["🛡️Authentication "])


@router_auth.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection() 
    try:
        with conn.cursor() as cur:
            # Query the Odoo users table
            cur.execute(
                "SELECT id, login, password, team_id, role FROM users WHERE login = %s",
                (form_data.username,)
            )
            user = cur.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Password verification using Passlib PBKDF2-SHA512
            if not pwd_context.verify(form_data.password, user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            access_token = create_access_token(
                data={
                    "sub": form_data.username,
                    "user_id": user["id"],
                    "team_id": user["team_id"],
                    "role": user["role"]
                }
            )
            return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()

@router_auth.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


# Visible users for filters (RBAC):
# - Admin: all users
# - Manager: only users in same team
# - Employee: only users in same team
@router_auth.get("/users/visible", summary="List users visible to current user")
async def list_visible_users(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if current_user["role"] == "admin":
                cur.execute("""
                    SELECT id, login, team_id, role
                    FROM users
                    ORDER BY team_id, login
                """)
            else:
                cur.execute("""
                    SELECT id, login, team_id, role
                    FROM users
                    WHERE team_id = %s
                    ORDER BY team_id, login
                """, (current_user["team_id"],))
            return cur.fetchall()
    finally:
        conn.close()


# --- Admin-only: create user with PBKDF2-SHA512 password hashing ---
class CreateUserRequest(BaseModel):
    login: str
    password: str = Field(min_length=6)
    team_id: str
    role: str  # 'employee' | 'manager' | 'admin'
    is_active: Optional[bool] = True


# --- Public signup endpoint with PBKDF2-SHA512 password hashing ---
class SignupRequest(BaseModel):
    # Accept frontend fields
    email: Optional[str] = Field(None, description="User email (used as login if provided)")
    username: Optional[str] = Field(None, description="Username (used as login if email not provided)")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="Full name (optional)")
    # Backend fields with defaults
    team_id: Optional[str] = Field(default="USER", description="Team ID (default: 'USER')")
    role: Optional[str] = Field(default="user", description="User role (default: 'user')")
    is_active: Optional[bool] = True


@router_auth.post("/auth/register", summary="Register a new user")
async def register(payload: SignupRequest):
    """
    Register a new user with PBKDF2-SHA512 password hashing (25000 iterations).
    Uses the same encryption method as the seed data in models.py.
    
    Accepts frontend fields: email, username, password, full_name
    Maps email to login field in database.
    """
    # Determine login: use email if provided, otherwise use username
    if payload.email:
        login = payload.email
    elif payload.username:
        login = payload.username
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username must be provided"
        )
    
    # Hash password using PBKDF2-SHA512 with 25000 iterations
    password_hash = pwd_context.hash(payload.password)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE login = %s", (login,))
            existing_user = cur.fetchone()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email/username already exists"
                )
            
            # Insert new user
            cur.execute(
                """
                INSERT INTO users (login, password, team_id, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, login, team_id, role
                """,
                (login, password_hash, payload.team_id, payload.role, payload.is_active),
            )
            new_user = cur.fetchone()
            conn.commit()
            
            return {
                "id": new_user["id"],
                "login": new_user["login"],
                "team_id": new_user["team_id"],
                "role": new_user["role"],
                "message": "User registered successfully"
            }
    except HTTPException:
        # Re-raise HTTP exceptions
        conn.rollback()
        raise
    except Exception as e:
        # Handle other DB errors
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        conn.close()


# --- Admin-only: create user with PBKDF2-SHA512 password hashing ---
class CreateUserRequest(BaseModel):
    login: str
    password: str = Field(min_length=6)
    team_id: str
    role: str  # 'employee' | 'manager' | 'admin'
    is_active: Optional[bool] = True


@router_auth.post("/admin/users", summary="Create a new user (admin only)")
async def admin_create_user(payload: CreateUserRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    if payload.role not in ("employee", "manager", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    password_hash = pwd_context.hash(payload.password)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (login, password, team_id, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (payload.login, password_hash, payload.team_id, payload.role, payload.is_active),
            )
            new_id = cur.fetchone()["id"]
            conn.commit()
            return {"id": new_id, "login": payload.login, "team_id": payload.team_id, "role": payload.role}
    except Exception as e:
        # Handle duplicate login or other DB errors
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

