from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.rag_db.models import User
from src.auth.schema import CreateUserModel
from src.auth.utils import hash_password

import random
from datetime import datetime, timedelta

# In-memory OTP storage: email -> (otp, expiry_time)
_otp_store = {}

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

        new_user = User(**user_data_dict)
        new_user.password_hash = hash_password(user_data_dict["password"])
        new_user.role = "user"

        session.add(new_user)

        await session.commit()

        await session.refresh(new_user)

        return new_user

    def generate_otp(self, email: str) -> str:
        """Generate OTP and store it in-memory with 10-minute expiry"""
        otp = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=10)
        _otp_store[email] = (otp, expiry)
        return otp

    def verify_otp_input(self, email: str, user_otp: str) -> tuple[bool, str]:
        """Verify the OTP submitted by user"""
        if email not in _otp_store:
            return False, "No OTP found for this email."
        
        stored_otp, expiry = _otp_store[email]
        
        if datetime.now() > expiry:
            del _otp_store[email]
            return False, "OTP has expired."
        
        if user_otp != stored_otp:
            return False, "Invalid OTP."
        
        # Clean up after successful verification
        del _otp_store[email]
        return True, "OTP verified successfully."

    async def verify_user(self, user: User, session: AsyncSession):
        """Mark user as verified in database"""
        user.is_verified = True
        session.add(user)
        await session.commit()
