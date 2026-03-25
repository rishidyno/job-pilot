"""Auth API — register, login, get current user."""

from fastapi import APIRouter, HTTPException, Depends
from database import get_collection
from models.user import UserCreate, UserLogin, UserResponse
from services.auth_service import (
    hash_password, verify_password, create_access_token, get_current_user_id,
)
from utils.helpers import utc_now

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
async def register(data: UserCreate):
    users = get_collection("users")
    if await users.find_one({"email": data.email.lower()}):
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "full_name": data.full_name,
        "created_at": utc_now(),
    }
    result = await users.insert_one(doc)
    token = create_access_token(str(result.inserted_id))
    return {"token": token, "user": {"id": str(result.inserted_id), "email": doc["email"], "full_name": doc["full_name"]}}


@router.post("/login")
async def login(data: UserLogin):
    users = get_collection("users")
    user = await users.find_one({"email": data.email.lower()})
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
