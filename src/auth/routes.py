from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta 
from fastapi.exceptions import HTTPException
from src.auth.schema import CreateUserModel, LoginModel, VerifyOTPModel
from src.rag_db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.services import UserService
from src.mail import mail, create_message
from src.auth.schema import EmailModel
from src.auth.utils import verify_password, create_access_token
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker, get_current_user
from src.rag_db.redis import add_jti_to_blocklist
from src.app.services.config import Config


auth_router = APIRouter(prefix="/auth", tags=["auth"])
service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/CreateUser")
async def create_user(user_data: CreateUserModel, session: AsyncSession = Depends(get_session)):

    email = user_data.email
    user_exists = await service.user_exist(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exist")
    
    new_user = await service.create_account(user_data, session)

    # Generate OTP and store user data temporarily
    otp = service.generate_otp(email, user_data=user_data)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Exo 2', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #050810;
                color: #c8dff0;
                margin: 0; padding: 20px;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background: #0a0f1e;
                border: 1px solid #1a2a4a;
                padding: 40px;
                border-radius: 4px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 32px;
                border-bottom: 1px solid #1a2a4a;
                padding-bottom: 24px;
            }}
            .brand {{
                font-family: 'Orbitron', sans-serif;
                font-size: 24px;
                font-weight: 900;
                letter-spacing: 2px;
                color: #fff;
            }}
            .brand span {{ color: #e8725a; }}
            .status {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 10px;
                color: #5a7a9a;
                letter-spacing: 2px;
                margin-top: 8px;
            }}
            h1 {{
                font-family: 'Orbitron', sans-serif;
                font-size: 18px;
                font-weight: 900;
                color: #fff;
                margin: 24px 0 16px 0;
            }}
            .message {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 12px;
                color: #c8dff0;
                line-height: 1.8;
                margin-bottom: 28px;
            }}
            .otp-box {{
                background: #0d1526;
                border: 2px solid #e8725a;
                padding: 24px;
                text-align: center;
                margin: 32px 0;
                border-radius: 2px;
            }}
            .otp-value {{
                font-family: 'Orbitron', sans-serif;
                font-size: 36px;
                font-weight: 900;
                letter-spacing: 8px;
                color: #e8725a;
                word-break: break-all;
            }}
            .timer {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 11px;
                color: #00ff88;
                text-align: center;
                margin: 16px 0;
            }}
            .footer {{
                border-top: 1px solid #1a2a4a;
                padding-top: 20px;
                margin-top: 32px;
                font-family: 'Share Tech Mono', monospace;
                font-size: 10px;
                color: #5a7a9a;
                text-align: center;
                line-height: 1.6;
            }}
            .warning {{
                color: #ff4500;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand">LUMI<span>.</span></div>
                <div class="status">AI COMPANION ACCESS</div>
            </div>
            
            <h1>Welcome, {user_data.first_name}!</h1>
            
            <div class="message">
                Your LUMI account has been created successfully. Your access code is below:
            </div>
            
            <div class="otp-box">
                <div class="otp-value">{otp}</div>
            </div>
            
            <div class="message">
                Enter this code to verify your account and gain full access to the LUMI platform.
            </div>
            
            <div class="timer">
                ⏱️ This code expires in <strong>10 minutes</strong>
            </div>
            
            <div class="footer">
                <p class="warning">⚠️ Security Notice:</p>
                <p>Do not share this code with anyone. LUMI team members will never ask for your verification code.</p>
                <p>If you did not create this account, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    print(user_data.email)
    message = create_message(
        recipients=[user_data.email],
        subject="Verify your LUMI account",
        body=html
    )
    await mail.send_message(message)

    return {"message": "Account created. Check your email to verify."}


@auth_router.post("/verify-otp")
async def verify_otp(otp_data: VerifyOTPModel, session: AsyncSession = Depends(get_session)):
    email = otp_data.email
    otp = otp_data.otp

    is_valid, message = service.verify_otp_input(email, otp)

    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    user = await service.get_user_by_email(email, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_verified:
        return {"message": "Account already verified."}

    await service.verify_user(user, session)

    return {"message": "Account verified successfully."}


@auth_router.post("/resend-otp")
async def resend_otp(email_data: EmailModel, session: AsyncSession = Depends(get_session)):
    email = email_data.email
    user_exists = await service.user_exist(email, session)

    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found. Please register first.")

    # Generate new OTP and store user data temporarily
    otp = service.generate_otp(email)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Exo 2', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #050810;
                color: #c8dff0;
                margin: 0; padding: 20px;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background: #0a0f1e;
                border: 1px solid #1a2a4a;
                padding: 40px;
                border-radius: 4px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 32px;
                border-bottom: 1px solid #1a2a4a;
                padding-bottom: 24px;
            }}
            .brand {{
                font-family: 'Orbitron', sans-serif;
                font-size: 24px;
                font-weight: 900;
                letter-spacing: 2px;
                color: #fff;
            }}
            .brand span {{ color: #e8725a; }}
            .status {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 10px;
                color: #5a7a9a;
                letter-spacing: 2px;
                margin-top: 8px;
            }}
            h1 {{
                font-family: 'Orbitron', sans-serif;
                font-size: 18px;
                font-weight: 900;
                color: #fff;
                margin: 24px 0 16px 0;
            }}
            .message {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 12px;
                color: #c8dff0;
                line-height: 1.8;
                margin-bottom: 28px;
            }}
            .otp-box {{
                background: #0d1526;
                border: 2px solid #e8725a;
                padding: 24px;
                text-align: center;
                margin: 32px 0;
                border-radius: 2px;
            }}
            .otp-value {{
                font-family: 'Orbitron', sans-serif;
                font-size: 36px;
                font-weight: 900;
                letter-spacing: 8px;
                color: #e8725a;
                word-break: break-all;
            }}
            .timer {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 11px;
                color: #00ff88;
                text-align: center;
                margin: 16px 0;
            }}
            .footer {{
                border-top: 1px solid #1a2a4a;
                padding-top: 20px;
                margin-top: 32px;
                font-family: 'Share Tech Mono', monospace;
                font-size: 10px;
                color: #5a7a9a;
                text-align: center;
                line-height: 1.6;
            }}
            .warning {{
                color: #ff4500;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand">LUMI<span>.</span></div>
                <div class="status">AI COMPANION ACCESS</div>
            </div>
            
            <h1>Welcome, {user_exists.first_name}!</h1>
            
            <div class="message">
                Your LUMI account verification code is below:
            </div>
            
            <div class="otp-box">
                <div class="otp-value">{otp}</div>
            </div>
            
            <div class="message">
                Enter this code to verify your account and gain full access to the LUMI platform.
            </div>
            
            <div class="timer">
                ⏱️ This code expires in <strong>10 minutes</strong>
            </div>
            
            <div class="footer">
                <p class="warning">⚠️ Security Notice:</p>
                <p>Do not share this code with anyone. LUMI team members will never ask for your verification code.</p>
                <p>If you did not create this account, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    print(user_exists.email)
    message = create_message(
        recipients=[user_exists.email],
        subject="Verify your LUMI account",
        body=html
    )
    await mail.send_message(message)

    return {"message": "Account created. Check your email to verify."}




@auth_router.post("/login")
async def login_user(login_data: LoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user": str(user.uid), "role":user.role}
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=Config.REFRESH_TOKEN_DAYS),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email,
                              "uid": str(user.uid),
                              "role": user.role}
                }
            )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email or Password")

@auth_router.get("/refresh")
async def get_new_access_token(token_detail:dict=Depends(RefreshTokenBearer())):
    expiry_timestamp = token_detail["exp"]
    
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_detail["user"],
        )
        return JSONResponse(content={
            "access_token": new_access_token,
        })
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")



@auth_router.get("/me")
async def read_current_user(user_details=Depends(get_current_user), _:bool = Depends(role_checker)):
    return user_details


@auth_router.get("/logout")
async def revoke_token(token_detail: dict = Depends(AccessTokenBearer())):
    jti = token_detail.get("jti")
    
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: Missing JTI"
        )

    # Fire and forget or await? Awaiting ensures it's blocked before returning.
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK
    )
