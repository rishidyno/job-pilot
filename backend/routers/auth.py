"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Auth API Router                                      ║
║                                                                   ║
║  Endpoints:                                                       ║
║  POST /api/auth/register  → Create account, return JWT           ║
║  POST /api/auth/login     → Verify credentials, return JWT       ║
║  GET  /api/auth/me        → Validate token, return user info     ║
║                                                                   ║
║  Auth flow:                                                       ║
║  1. Client POSTs credentials → receives JWT token                ║
║  2. Client stores token in localStorage                           ║
║  3. All subsequent requests include token in Authorization header ║
║  4. Protected routes call get_current_user_id() dependency        ║
║     which decodes the token and returns the user's MongoDB _id   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import re
from fastapi import APIRouter, HTTPException, Depends
from database import get_collection
from models.user import UserCreate, UserLogin
from services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user_id,
)
from utils.helpers import utc_now

router = APIRouter(prefix="/api/auth", tags=["Auth"])

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _validate_registration(data: UserCreate):
    """
    Validate registration fields before hitting the database.

    Rules enforced:
    - full_name: at least 2 characters
    - email: valid format via regex
    - password: min 8 chars, at least one uppercase letter, at least one digit

    Raises HTTPException 422 with field-level errors so the frontend
    can highlight specific inputs rather than showing a generic message.
    """
    errors = {}
    if not data.full_name or len(data.full_name.strip()) < 2:
        errors["full_name"] = "Name must be at least 2 characters"
    if not EMAIL_RE.match(data.email):
        errors["email"] = "Enter a valid email address"
    if len(data.password) < 8:
        errors["password"] = "Password must be at least 8 characters"
    elif not re.search(r"[A-Z]", data.password):
        errors["password"] = "Password needs at least one uppercase letter"
    elif not re.search(r"[0-9]", data.password):
        errors["password"] = "Password needs at least one number"
    if errors:
        raise HTTPException(status_code=422, detail={"field_errors": errors})


@router.post("/register")
async def register(data: UserCreate):
    """Create a new user account and return a JWT token."""
    _validate_registration(data)
    users = get_collection("users")

    # Reject duplicate emails (unique index also enforces this at the DB level)
    if await users.find_one({"email": data.email.lower()}):
        raise HTTPException(status_code=422, detail={"field_errors": {"email": "This email is already registered"}})

    doc = {
        "email": data.email.lower().strip(),
        "password_hash": hash_password(data.password),  # bcrypt hash, never stored plain
        "full_name": data.full_name.strip(),
        "created_at": utc_now(),
    }
    result = await users.insert_one(doc)

    # Issue a token with the new user's MongoDB _id as the subject claim
    token = create_access_token(str(result.inserted_id))
    return {"token": token, "user": {"id": str(result.inserted_id), "email": doc["email"], "full_name": doc["full_name"]}}


@router.post("/login")
async def login(data: UserLogin):
    """Verify credentials and return a JWT token."""
    users = get_collection("users")
    user = await users.find_one({"email": data.email.lower().strip()})

    # Intentionally give the same error for "user not found" and "wrong password"
    # to prevent email enumeration attacks
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user["_id"]))
    return {"token": token, "user": {"id": str(user["_id"]), "email": user["email"], "full_name": user["full_name"]}}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    """
    Return the current user's info.

    Called by the frontend on page load to check if a stored token
    is still valid and to hydrate the user context. If the token is
    expired or invalid, get_current_user_id() raises 401 before this
    handler runs, which triggers a redirect to /login.
    """
    users = get_collection("users")
    from bson import ObjectId
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(user["_id"]), "email": user["email"], "full_name": user["full_name"]}
