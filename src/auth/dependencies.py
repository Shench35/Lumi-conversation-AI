from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import List, Any
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.rag_db.redis import token_in_blocklist
from src.rag_db.main import get_session
from .services import UserService
from src.rag_db.models import User

user_service = UserService()

class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)



    def token_valid(self, token:str)-> bool:
        # Token validation is now handled in __call__ method
        # This method is kept for backward compatibility but should be removed
        token_data = decode_token(token)
        return True if token_data is not None else False
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in the child classes")
    

    async def __call__(self, request:Request)->HTTPAuthorizationCredentials|None:
        cred = await super().__call__(request)

        token = cred.credentials

        token_data = decode_token(token)
        
        if token_data is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error":"This token is invalid or revoked",
                "resolution":"get a new token"
            })
        
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error":"This token has been revoked",
                "resolution":"get a new token"
            })
        
        self.verify_token_data(token_data)
        
        return token_data


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data:dict)-> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a valid access token")
        
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict)-> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a valid refresh token")


async def get_current_user(token_details:dict=Depends(AccessTokenBearer()),
                     session:AsyncSession=Depends(get_session)
                     ):
     user_email = token_details["user"]["email"]

     user = await user_service.get_user_by_email(user_email, session)

     return user

class RoleChecker:
    def __init__(self, allowed_role:List[str])-> None:
        
        self.allowed_roles = allowed_role


    async def __call__(self, current_user: User=Depends(get_current_user))->Any:

        if current_user.role in self.allowed_roles:
            return True
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="operation not permitted")
