from fastapi import APIRouter, HTTPException
from typing import List
from app.test import LessonCreate,LessonGet, create_lesson_orm, get_lessons_all

router = APIRouter()

@router.get("/", response_model=List[LessonGet])
async def get_lessons():
    result = await get_lessons_all()
    return result
#     try:
#         result = await get_lessons()
#     except:
#         raise HTTPException(status_code=500, detail="Проблема с запросом в бд")
#     return result
    

@router.post("/create")
async def create_lesson(data: LessonCreate):
    if data is None:
        raise HTTPException(status_code=404, detail="Данные с фронта не поступили")
    if data.recurring:
        print("recurring")
    else:
        if data.notes is None:
            data.notes = ""
        result = await create_lesson_orm(data)

    return {"message":result}

#сюда написать энд для обновления студента