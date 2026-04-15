import email

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.rag_db.models import User
from src.auth.schema import CreateUserModel
from src.auth.utils import hash_password

import random
from datetime import datetime, timedelta

from fastapi import Depends

from src.rag_db.redis import save_otp, get_otp, delete_otp

# In-memory OTP storage removed for production readiness

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exist(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_account(self, user_data: CreateUserModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        # Remove 'password' from dict before creating User instance as User model doesn't have it
        password = user_data_dict.pop("password")
        
        new_user = User(**user_data_dict)
        new_user.password_hash = hash_password(password)
        new_user.role = "user"
        new_user.is_verified = False  # Set as verified after OTP verification

        session.add(new_user)

        await session.commit()

        await session.refresh(new_user)

        return new_user

    async def generate_otp(self, email: str) -> str:
        """Generate OTP and store it in Redis with 10-minute expiry"""
        otp = str(random.randint(100000, 999999))
        await save_otp(email, otp, expiry_seconds=120)  # 3 minutes
        return otp

    async def verify_otp_input(self, email: str, user_otp: str) -> tuple[bool, str]:
        """Verify the OTP submitted by user using Redis"""
        stored_otp = await get_otp(email)
        
        if stored_otp is None:
            return False, "No OTP found or OTP has expired."
        
        if user_otp != stored_otp:
            return False, "Invalid OTP."
        
        # Clean up after successful verification
        await delete_otp(email)
        return True, "OTP verified successfully."

    async def verify_user(self, user: User, session: AsyncSession):
        """Mark user as verified in database"""
        user.is_verified = True
        session.add(user)
        await session.commit()
