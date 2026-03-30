from fastapi import APIRouter, Depends

from sqlmodel.ext.asyncio.session import AsyncSession
from src.rag_db.main import get_session
from src.app.admin.service import AdminService
from src.app.admin.schema import NewRole

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
service = AdminService()

# View all users
@admin_router.get("/admin-get-all-user ")
async def admin_get_all_user(session: AsyncSession = Depends(get_session)):
        users = await service.get_all_users(session)
        return users

# Verify/unverify users
@admin_router.patch("/admin-verify-and-unverify-user/{uid}")
async def admin_verify_and_unverify_user(uid:str, session: AsyncSession = Depends(get_session)):
        await service.verify_and_unverify_user(uid, session)
        return {"message": "User verification status toggled successfully"}

# Delete users,
@admin_router.delete("/admin-delete-user/{uid}")
async def admin_delete_user(uid:str, session: AsyncSession = Depends(get_session)):
        await service.delete_user(uid, session)
        return {"message": "User deleted successfully"}

# Change user roles
@admin_router.patch("/admin-change-user-role/{uid}")
async def admin_change_user_role(uid:str, new_role:NewRole, session: AsyncSession = Depends(get_session)):
        await service.change_user_role(uid, new_role.role, session)
        return {"message": f"User role changed to {new_role.role} successfully"}

# View query logs 
@admin_router.get("/admin-get-query-logs")
async def admin_get_query_logs(session: AsyncSession = Depends(get_session)):
        logs = await service.get_query_logs(session)
        return logs