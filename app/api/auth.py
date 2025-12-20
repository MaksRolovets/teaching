from fastapi import APIRouter, HTTPException, Response, Depends
from passlib.context import CryptContext
from pydantic import BaseModel
from app.security.security_app import create_jwt_access, decode_user_from_jwt_access,decode_user_from_jwt_refresh, create_jwt_refresh
from app.test import select_user, insert_user, insert_token_orm, revoke_token_orm, select_token_orm
import logging

# Получаем логгер uvicorn
logger = logging.getLogger("uvicorn")

class LoginRequest(BaseModel):
    password : str
    email : str

class RegisterUser(BaseModel):
    email : str
    password : str

myctx = CryptContext(schemes=["bcrypt"])

router = APIRouter()

@router.post("/register")
async def register_api(data : RegisterUser):
    if await select_user(data.email) is None:
        data.password = myctx.hash(data.password)
        result = await insert_user(data)
        return result
    else:
        raise HTTPException(status_code=409, detail="email already exists")
@router.post("/logout")
async def logout_api(response : Response, payload = Depends(decode_user_from_jwt_refresh)):
    a= await select_token_orm(payload.get("jti"))
    response.delete_cookie(key="refresh_token",
        httponly=True,
        secure=True)   
    logging.info(a)
    await revoke_token_orm(payload.get("jti"))

    return {"message":"отозван"}

@router.post("/login")
async def login_api(data: LoginRequest, response: Response):
    user = await select_user(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователя с таким email не существует")
    
    if not myctx.verify(data.password,user["password"]):
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")
    
    access_token = create_jwt_access(user["id"])
    refresh_token = create_jwt_refresh(user["id"])
    await insert_token_orm(refresh_token[1], user["id"])

    response.set_cookie(
        key="refresh_token",
        value=refresh_token[0],
        httponly=True,
        secure=True,          # False только локально
        samesite="lax",
        max_age=2678400 ,
        path="/auth"
    )
    # написать занесение в базу
        # Возвращаем JSON с токеном
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Успешный вход"
    }

@router.post("/refresh")
async def refresh(response: Response, payload = Depends(decode_user_from_jwt_refresh)):
    try:
        token = payload.get("sub")
        a= await select_token_orm(payload.get("jti"))   
        logging.info(a)
        await revoke_token_orm(payload.get("jti"))
        new_access = create_jwt_access(token)
        new_refresh = create_jwt_refresh(token)
        await insert_token_orm(new_refresh[1], token)
        response.set_cookie(
            key="refresh_token",
            value=new_refresh[0],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=2678400,
            path="/auth"
    )

        return {
            "access_token": new_access
        }
    except:
        raise HTTPException(status_code=405)