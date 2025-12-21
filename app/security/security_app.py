import jwt
import uuid
from fastapi.security import OAuth2PasswordBearer

import datetime
from fastapi import Cookie
from app.test import revoke_token_orm, select_token_orm
from fastapi import Depends, HTTPException

  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

  

SECRET_KEY = "Asdfjhsergihiaegiaiergoiaeroigjoaerjogjaoeirgjopajero"

ALGHORITM = "HS256"

ACCESS_TOKEN_EXPIRE_MIN = 15
REFRESH_TOKEN_EXPIRE_HOUR = 720

def create_jti()-> str:
    return str(uuid.uuid4())

  

def create_jwt_access(user_id: int) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MIN
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGHORITM)

  

def create_jwt_refresh(user_id:int) ->str:
    jti = create_jti()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=REFRESH_TOKEN_EXPIRE_HOUR)
    payload = {
        "sub": str(user_id),
        "jti":jti,
        "type": "refresh",
        "exp": expire.timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGHORITM), jti

  

def decode_user_from_jwt_access(token : str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGHORITM])
        username = payload.get("sub")
        if not username:

            raise HTTPException(status_code=401, detail="Invalid token payload")

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(status_code=401, detail="Время жизни токена истекло")

    except jwt.InvalidTokenError:

        raise HTTPException(status_code=401, detail="Токен поврежден, изменен или подделан")
    

async def decode_user_from_jwt_refresh(
    refresh_token: str = Cookie(None, alias="refresh_token")
) -> dict:
    # Проверяем refresh token
    try:
        refresh_payload = jwt.decode(
            refresh_token, 
            SECRET_KEY,  # Отдельный секрет для refresh токенов
            algorithms=[ALGHORITM],
            options={"verify_exp":False}
        )
        
        # Проверяем, что это refresh token
        if refresh_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        if datetime.datetime.utcnow().timestamp() > refresh_payload.get("exp"):
            await revoke_token_orm(refresh_payload.get("jti"))
            raise HTTPException(status_code=401, detail="Refresh token expired. Please login again")

        jti = refresh_payload.get("jti")
        token_in_db = await select_token_orm(jti)
        if not token_in_db or token_in_db.revoked:  # предполагаем, что в ORM есть поле revoked
            raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")



        # Возвращаем payload из refresh token (с данными пользователя)
        username = refresh_payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token payload")
        
        return refresh_payload  # Или можно вернуть обновленный payload
        
    # except jwt.ExpiredSignatureError:
    #     raise HTTPException(status_code=401, detail="Refresh token expired. Please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")