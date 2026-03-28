from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from src.auth.schema import CreateUserModel, LoginModel
from src.rag_db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.services import UserService
from src.mail import mail, create_message
from src.auth.schema import EmailModel
from src.auth.utils import create_verification_token, decode_verification_token
from itsdangerous import SignatureExpired, BadSignature


auth_router = APIRouter(prefix="/auth", tags=["auth"])
service = UserService()


@auth_router.post("/CreateUser")
async def create_user(user_data: CreateUserModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await service.user_exist(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exist")

    new_user = await service.create_account(user_data, session)

    # send verification email
    token = create_verification_token(new_user.email)
    verify_link = f"http://127.0.0.1:5500/verify.html?token={token}"

    html = f"""
        <h2>Welcome to ORBITAL, {new_user.first_name}!</h2>
        <p>Click the link below to verify your account:</p>
        <a href="{verify_link}">VERIFY ACCOUNT</a>
        <p>This link expires in 1 hour.</p>
    """

    message = create_message(
        recipients=[new_user.email],
        subject="Verify your ORBITAL account",
        body=html
    )
    await mail.send_message(message)

    return {"message": "Account created. Check your email to verify."}


@auth_router.get("/verify/{token}")
async def verify_account(token: str, session: AsyncSession = Depends(get_session)):
    try:
        email = decode_verification_token(token)
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link has expired.")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")

    user = await service.get_user_by_email(email, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_verified:
        return {"message": "Account already verified."}

    await service.verify_user(user, session)

    return {"message": "Account verified successfully."}

@auth_router.post("/Login")
async def login(login_data: LoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await service.get_user_by_email(email, session)

    if not user or not user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return {"message": "Login successful"}