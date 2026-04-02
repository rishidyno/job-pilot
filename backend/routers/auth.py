"""Auth API — register, login, get current user."""

import re
import os
from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import get_collection
from models.user import UserCreate, UserLogin
from services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user_id,
)
from utils.helpers import utc_now

router = APIRouter(prefix="/api/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address, enabled=os.environ.get("TESTING") != "1")

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _validate_registration(data: UserCreate):
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
@limiter.limit("3/minute")
async def register(request: Request, data: UserCreate):
    _validate_registration(data)
    users = get_collection("users")
    if await users.find_one({"email": data.email.lower()}):
        raise HTTPException(status_code=422, detail={"field_errors": {"email": "This email is already registered"}})

    doc = {
        "email": data.email.lower().strip(),
        "password_hash": hash_password(data.password),
        "full_name": data.full_name.strip(),
        "created_at": utc_now(),
    }
    result = await users.insert_one(doc)
    token = create_access_token(str(result.inserted_id))
    return {"token": token, "user": {"id": str(result.inserted_id), "email": doc["email"], "full_name": doc["full_name"]}}


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin):
    users = get_collection("users")
    user = await users.find_one({"email": data.email.lower().strip()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user["_id"]))
    return {"token": token, "user": {"id": str(user["_id"]), "email": user["email"], "full_name": user["full_name"]}}


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    users = get_collection("users")
    from bson import ObjectId
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(user["_id"]), "email": user["email"], "full_name": user["full_name"]}
