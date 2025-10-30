"""Authentication endpoints."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from citrature.database import get_db
from citrature.models import User
from citrature.config_simple import get_settings
from citrature.schemas.auth import UserCreate, UserResponse, Token, GoogleAuthRequest
import httpx

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


async def verify_google_token(id_token: str) -> Optional[dict]:
    """Verify Google ID token and return user info."""
    try:
        # Get Google's public keys for token verification
        async with httpx.AsyncClient() as client:
            # Get Google's public keys
            response = await client.get("https://www.googleapis.com/oauth2/v3/certs")
            response.raise_for_status()
            keys = response.json()
            
            # Verify the token (simplified - in production, use proper JWT verification)
            # For now, we'll make a request to Google's tokeninfo endpoint
            tokeninfo_response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            tokeninfo_response.raise_for_status()
            token_info = tokeninfo_response.json()
            
            # Verify the audience matches our client ID
            if token_info.get("aud") != settings.google_client_id:
                logger.error(f"Token audience mismatch: {token_info.get('aud')} != {settings.google_client_id}")
                return None
            
            return {
                "email": token_info.get("email"),
                "name": token_info.get("name"),
                "picture": token_info.get("picture"),
                "sub": token_info.get("sub")
            }
            
    except Exception as exc:
        logger.error(f"Google token verification failed: {exc}", exc_info=True)
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/google", response_model=Token)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth."""
    try:
        # Verify Google ID token
        google_user_info = await verify_google_token(request.id_token)
        if not google_user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == google_user_info["email"]).first()
        
        if not user:
            # Create new user
            user = User(
                email=google_user_info["email"],
                name=google_user_info["name"],
                picture_url=google_user_info.get("picture"),
                plan="free"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user info
            user.name = google_user_info["name"]
            user.picture_url = google_user_info.get("picture")
            db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
        
    except Exception as exc:
        logger.error(f"Google authentication failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        picture_url=current_user.picture_url,
        plan=current_user.plan,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user (clear token)."""
    # In a real implementation, you might want to blacklist the token
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}
