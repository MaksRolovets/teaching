from sqlalchemy.types import String
from sqlalchemy import func, ForeignKey,select, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from typing import Optional
import asyncio
import datetime

DATABASE_URL = "postgresql+asyncpg://makspg:1234@localhost/students"

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

from pydantic import BaseModel, ConfigDict

class StudentCreate(BaseModel):
    name: Optional[str] 
    grade: Optional[int] 
    descriptions: Optional[str] 
    contacts: Optional[str] 

class StudentResponse(BaseModel):
    id: int
    name: Optional[str]
    grade: Optional[int]
    descriptions: Optional[str]
    contacts: Optional[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class LessonCreate(BaseModel):
    pass


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=True)
    grade : Mapped[int] = mapped_column(nullable=True)
    descriptions : Mapped[str]
    contacts : Mapped[str]
    created_at : Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    lesson_plans = relationship("LessonPlan", back_populates="student", cascade="all, delete")

class LessonPlan(Base):
    __tablename__ = "lesson_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bio: Mapped[str | None] = mapped_column(String(255))
    student_id : Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    topic : Mapped[str] = mapped_column(nullable=False)
    subtopic : Mapped[str]
    notes : Mapped[str]
    date: Mapped[datetime.date] = mapped_column(Date)
    begin : Mapped[datetime.datetime]
    student = relationship("Student", back_populates="lesson_plans")

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def insert_student(data : StudentCreate):
    async with async_session_maker() as sessions:
        sessions.add(Student(**data.model_dump()))
        await sessions.commit()
        return {"message":f"Студент {data.name} добавлен"}

async def select_users():
    async with async_session_maker() as sessions:
        result = await sessions.scalars(select(Student))
        users = result.all()
        users_schema = [StudentResponse.model_validate(u) for u in users]
        return [u.model_dump() for u in users_schema]

async def select_student(user_id : int):
    async with async_session_maker() as sessions:
        result = await sessions.scalars(select(Student).where(Student.id == user_id))
        user = StudentResponse.model_validate(result.one()).model_dump()
        return user
    
if __name__ == "__main__":
    asyncio.run(create_table())



