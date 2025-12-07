from fastapi import APIRouter, HTTPException
from typing import List
from app.test import StudentCreate, StudentResponse, select_users, create_table, select_student, insert_student, update_student_orm, delete_student_orm

router = APIRouter()

@router.get("/", response_model=List[StudentResponse])
async def get_all_students():
    try:
        result = await select_users()
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return result

@router.get("/{user_id}")
async def get_student(user_id : int):
    try:
        result = await select_student(user_id)
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return result

@router.post("/create")
async def create_students(data : StudentCreate):
    try:
        if data.descriptions is None:
            data.descriptions = ""
        result = await insert_student(data)
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return {"message":f"{data.name} добавлен успешно"}

@router.get("/info")
async def get_info_students():
    data={"studentsCount":100,
          "lessonsCount":50,
          "attendance":500,
          "revenue":0}
    return data

@router.put("/update/{id}")
async def update_student(id : int,data : dict):
    try:
        result = await update_student_orm(data=data, user_id=id)
    except:
        raise HTTPException(status_code=500, detail="ошибка со стоороны бд")
    return {"message":"Информация обновлена!"}

@router.delete("/{id}")
async def delete_student(id : int):
    try:
        result = await delete_student_orm(id)
    except:
        raise HTTPException(status_code=500, detail="DB error")
    return result