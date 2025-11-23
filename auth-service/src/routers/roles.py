from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres import get_session
from schemas.auth import RoleCreate, RoleRead, PermissionCheckRequest
from services.role_service import RoleService

router = APIRouter()
service = RoleService()


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(payload: RoleCreate, db: AsyncSession = Depends(get_session)):
    try:
        role = await service.create_role(db, payload)
        return role
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[RoleRead])
async def list_roles(db: AsyncSession = Depends(get_session)):
    roles = await service.list_roles(db)
    return roles


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(role_id: int, payload: RoleCreate, db: AsyncSession = Depends(get_session)):
    try:
        role = await service.update_role(db, role_id, payload)
        return role
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_session)):
    try:
        await service.delete_role(db, role_id)
        return {"detail": "Deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/assign")
async def assign_role(req: PermissionCheckRequest, db: AsyncSession = Depends(get_session)):
    try:
        await service.assign_role(db, req.login, req.required_role)
        return {"detail": "Роль назначена"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/revoke")
async def revoke_role(req: PermissionCheckRequest, db: AsyncSession = Depends(get_session)):
    try:
        await service.revoke_role(db, req.login, req.required_role)
        return {"detail": "Роль отобрана"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/check")
async def check_access(req: PermissionCheckRequest, db: AsyncSession = Depends(get_session)):
    try:
        allowed = await service.check_access(db, req.login, req.required_role)
        return {"login": req.login, "required_role": req.required_role, "allowed": allowed}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
