from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.test import LessonCreate,LessonGet, create_lesson_orm, get_lessons_all, delete_lessons_orm, update_lessons_orm, LessonUpdateInput, select_user_id
from app.security.security_app import decode_user_from_jwt_access

router = APIRouter()

@router.get("/", response_model=List[LessonGet])
async def get_lessons(payload = Depends(decode_user_from_jwt_access)):
    if payload.get("type") == "access":
        user_id = int(payload.get("sub"))
        user = await select_user_id(user_id)
        if user:
            result = await get_lessons_all(user_id)
            return result   
        else:
            raise HTTPException(status_code=401, detail="")
#     try:
#         result = await get_lessons()
#     except:
#         raise HTTPException(status_code=500, detail="Проблема с запросом в бд")
#     return result
    

@router.post("/create", dependencies=[Depends(decode_user_from_jwt_access)])
async def create_lesson(data: LessonCreate):
    if data is None:
        raise HTTPException(status_code=404, detail="Данные с фронта не поступили")
    if data.notes is None:
            data.notes = ""
    result = await create_lesson_orm(data)

    return {"message":result}

@router.put("/{lesson_id}",dependencies=[Depends(decode_user_from_jwt_access)])
async def update_lesson(lesson_id : int, data : LessonUpdateInput):
    if data is None:
        raise HTTPException(status_code=404, detail="Данные с фронта не поступили")
    if data.notes is None:
            data.notes = ""
    result = await update_lessons_orm(lesson_id, data)
    return {"message":result}

@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id : int):
    try:
        await delete_lessons_orm(lesson_id=lesson_id)
    except:
        raise HTTPException(status_code=404, detail="пользоватеоь не найден")
    
#сюда написать энд для обновления студента