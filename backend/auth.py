import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

from database import users_collection
from models import UserCreate, UserLogin, TokenResponse, UserResponse

load_dotenv()

router = APIRouter()
security = HTTPBearer()

JWT_SECRET: str = os.getenv("JWT_SECRET", "insecure_default_secret")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRY_DAYS: int = 7


# ─────────────────────────────────────────────
# Password utilities
# ─────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─────────────────────────────────────────────
# JWT utilities
# ─────────────────────────────────────────────

def create_access_token(user_id: str, email: str) -> str:
    """Create a signed JWT containing user identity claims."""
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT; raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject.",
            )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(exc)}",
        )


# ─────────────────────────────────────────────
# Dependency: current user from Bearer token
# ─────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency that extracts and validates the Bearer JWT.
    Returns the decoded token payload (sub, email).
    """
    payload = decode_access_token(credentials.credentials)
    return payload


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(body: UserCreate):
    """
    Create a new user account.

    - Checks for duplicate email.
    - Hashes password with bcrypt.
    - Saves the user document to MongoDB.
    - Returns a signed JWT alongside the created user's info.
    """
    # Duplicate check
    existing = await users_collection.find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    hashed_pw = hash_password(body.password)
    now = datetime.now(timezone.utc)

    user_doc = {
        "email": body.email,
        "hashed_password": hashed_pw,
        "created_at": now,
    }

    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_access_token(user_id=user_id, email=body.email)

    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, email=body.email, created_at=now),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
async def login(body: UserLogin):
    """
    Authenticate an existing user.

    - Looks up user by email.
    - Verifies bcrypt password hash.
    - Returns a fresh signed JWT.
    """
    user_doc = await users_collection.find_one({"email": body.email})

    # Intentionally generic error to avoid user enumeration
    if not user_doc or not verify_password(body.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_id = str(user_doc["_id"])
    token = create_access_token(user_id=user_id, email=user_doc["email"])

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user_doc["email"],
            created_at=user_doc["created_at"],
        ),
    )
