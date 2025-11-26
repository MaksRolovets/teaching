from fastapi import APIRouter, HTTPException
from typing import List
from app.test import StudentCreate, StudentResponse, select_users, create_table, select_student, insert_student

router = APIRouter()

@router.get("/", response_model=List[StudentResponse])
async def get_all_students():
    try:
        result = await select_users()
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return result

@router.get("/get/{user_id}")
async def get_student(user_id : int):
    try:
        result = await select_student(user_id)
    except:
        raise HTTPException(status_code=500, detail="Запрос в бд выбил ошибку")
    return result

@router.post("/create")
async def create_students(data : StudentCreate):
    try:
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

@router.get("/stud")
async def get_stud():
    data = [{"name":"Максончик епта","age":15, "id":1},
            {"name":"Максончик no епта","age":15, "id":2},
    ]
    return data
@router.get("/{id}")
async def get_student_id(id : int):
    if id == 1:
        data = {"name":"Макс",
                "age":12,
                "info":"алкоголик"}
    else:
        data = {"name":"Макс2",
                "age":123,
                "info":"алкоголик2"}
    return data