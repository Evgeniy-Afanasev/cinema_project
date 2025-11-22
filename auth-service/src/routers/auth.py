from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres import get_session
from schemas.auth import UserRegister, UserLogin, UserRead, TokenPair, RefreshRequest, UserUpdate, LoginHistoryRead
from services.auth_service import AuthService
from utils.jwt import decode_token

router = APIRouter()
service = AuthService()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_session)):
    try:
        user = await service.register(db, user_in.email, user_in.login, user_in.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenPair)
async def login(user_in: UserLogin, request: Request, db: AsyncSession = Depends(get_session)):
    ip = request.client.host if request.client else None
    ua = request.headers.get("User-Agent")
    try:
        access, refresh, exp = await service.login(db, user_in.login, user_in.password, ip, ua)
        return TokenPair(access_token=access, refresh_token=refresh, expires_in=exp)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=TokenPair)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_session)):
    try:
        access, refresh_value, exp = await service.refresh(db, req.refresh_token)
        return TokenPair(access_token=access, refresh_token=refresh_value, expires_in=exp)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(req: RefreshRequest, db: AsyncSession = Depends(get_session)):
    await service.logout(db, req.refresh_token)
    return {"detail": "Logged out"}

@router.put("/profile", response_model=UserRead)
async def update_profile(
    payload: UserUpdate,
    authorization: str | None = None,
    db: AsyncSession = Depends(get_session),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Требуется access-токен")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    try:
        user = await service.update_profile(db, int(claims["sub"]), payload.login, payload.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=list[LoginHistoryRead])
async def get_history(
    authorization: str | None = None,
    db: AsyncSession = Depends(get_session),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Требуется access-токен")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    entries = await service.history(db, int(claims["sub"]))
    return entries
