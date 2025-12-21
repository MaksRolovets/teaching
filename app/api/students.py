from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.test import StudentCreate, StudentResponse, select_users, select_user_id, select_student, insert_student, update_student_orm, delete_student_orm, count_lessons,count_students
from app.security.security_app import decode_user_from_jwt_access

router = APIRouter()

@router.get("/", response_model=List[StudentResponse])
async def get_all_students(payload = Depends(decode_user_from_jwt_access)):
    if payload.get("type") == "access":
        user_id = int(payload.get("sub"))
        user = await select_user_id(user_id)
        if user:
            try:
                try:
                    result = await select_users(user_id)
                except:
                    raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
                return result
            except:
                HTTPException(status_code=500)


@router.post("/create")
async def create_students(data : StudentCreate, payload= Depends(decode_user_from_jwt_access)):
    if payload.get("type") == "access":
        # try:
        if data.descriptions is None:
            data.descriptions = ""
        if data.contacts is None:
            data.contacts = ""
        result = await insert_student(data, int(payload.get("sub")))
        # except:
        #     raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
        return {"message":f"{data.name} добавлен успешно"}
    else:
        raise HTTPException(status_code=401)

@router.get("/info")
async def get_info_students(payload= Depends(decode_user_from_jwt_access)):
    user_id = int(payload.get("sub"))
    les = await count_lessons(user_id)
    stud = await count_students(user_id)
    data={"studentsCount":stud,
          "lessonsCount":les,
          "attendance":0,
          "revenue":0}
    return data

@router.get("/{user_id}",dependencies=[Depends(decode_user_from_jwt_access)])
async def get_student(user_id : int):
    try:
        result = await select_student(user_id)
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return result

@router.put("/update/{id}",dependencies=[Depends(decode_user_from_jwt_access)])
async def update_student(id : int,data : dict):
    try:
        result = await update_student_orm(data=data, user_id=id)
    except:
        raise HTTPException(status_code=500, detail="ошибка со стоороны бд")
    return {"message":"Информация обновлена!"}

@router.delete("/{id}",dependencies=[Depends(decode_user_from_jwt_access)])
async def delete_student(id : int):
    try:
        result = await delete_student_orm(id)
    except:
        raise HTTPException(status_code=500, detail="DB error")
    return result