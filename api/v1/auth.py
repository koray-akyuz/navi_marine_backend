from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.users import User
from schemas.users import UserCreate, UserLogin, Token, UserOut, GoogleLogin
from services.auth_service import get_password_hash, verify_password, create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests

from api.v1.deps import get_current_user

router = APIRouter()

GOOGLE_CLIENT_ID = "98982516649-80pe47qppqivq8e6eebluq7ubo2g3ucj.apps.googleusercontent.com"

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Email veya Nickname var mı kontrol et
    query = select(User).where((User.email == user_in.email) | (User.nickname == user_in.nickname))
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta veya lakap zaten kullanımda."
        )
    
    db_user = User(
        name=user_in.name,
        surname=user_in.surname,
        email=user_in.email,
        nickname=user_in.nickname,
        password=get_password_hash(user_in.password),
        city=user_in.city,
        district=user_in.district
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.nickname == user_in.nickname)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı lakap veya şifre.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "nickname": user.nickname}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nickname": user.nickname,
        "user_id": user.id
    }

@router.post("/google", response_model=Token)
async def google_login(google_in: GoogleLogin, db: AsyncSession = Depends(get_db)):
    try:
        # Google Token'ı doğrula
        idinfo = id_token.verify_oauth2_token(google_in.id_token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo['email']
        name = idinfo.get('given_name', 'Bilinmeyen')
        surname = idinfo.get('family_name', 'Kaptan')
        
        # Email ile kullanıcı var mı bak
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            # Yeni kullanıcı oluştur (Google ile ilk giriş)
            # Nickname olarak email'in ilk kısmını alalım (veya rastgele bişey)
            base_nickname = email.split('@')[0]
            nickname = base_nickname
            
            # Nickname çakışması kontrolü
            nick_query = select(User).where(User.nickname == nickname)
            nick_result = await db.execute(nick_query)
            if nick_result.scalars().first():
                nickname = f"{base_nickname}_{idinfo['sub'][:5]}"

            user = User(
                name=name,
                surname=surname,
                email=email,
                nickname=nickname,
                password=None # Google ile giriş yapanların şifresi yok
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Standart JWT üret
        access_token = create_access_token(
            data={"sub": str(user.id), "nickname": user.nickname}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "nickname": user.nickname,
            "user_id": user.id
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz Google Token."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google girişi sırasında hata: {str(e)}"
        )
