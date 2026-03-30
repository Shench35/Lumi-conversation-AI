from src.rag_db.models import User
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.rag_db.models import QueryLog

class AdminService:
    async def get_all_users(self, session: AsyncSession):
        statement = select(User).order_by(desc(User.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def verify_and_unverify_user(self, uid: str, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        user = result.first()
        if not user:
            return {"error": "User not found"}
        
        user.is_verified = not user.is_verified  # Toggle verification status
        session.add(user)
        await session.commit()
        return {"message": f"User {'verified' if user.is_verified else 'unverified'} successfully"}
    
    async def delete_user(self, uid:str, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        user = result.first()
        if not user:
            return {"error": "User not found"}
        await session.delete(user)
        await session.commit()
        return {"message": "User deleted successfully"}
    
    async def change_user_role(self, uid: str, new_role: str, session: AsyncSession):
        statement = select(User).where(User.id == uid)
        result = await session.exec(statement)
        user = result.first()
        if not user:
            return {"error": "User not found"}
        
        user.role = new_role
        session.add(user)
        await session.commit()
        return {"message": f"User role changed to {new_role} successfully"}
    
    async def get_query_logs(self, session: AsyncSession):
        # Assuming there's a QueryLog model that tracks user queries
        statement = select(QueryLog).order_by(desc(QueryLog.timestamp))
        result = await session.exec(statement)
        return result.all()