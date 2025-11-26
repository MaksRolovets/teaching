from fastapi import APIRouter
from app.api import students
from app.api import lessons


api_router = APIRouter()

api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])