from sqlalchemy.types import String
from sqlalchemy import func, ForeignKey,select, Time, Date, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from typing import Optional
import asyncio
import datetime

DATABASE_URL = "postgresql+asyncpg://makspg:1234@localhost/students"

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

from pydantic import BaseModel, ConfigDict, field_serializer

class StudentCreate(BaseModel):
    name: Optional[str] 
    grade: Optional[int] 
    descriptions: Optional[str] 
    contacts: Optional[str] 

class Base(AsyncAttrs, DeclarativeBase):
    pass

class LessonPlan(Base):
    __tablename__ = "lesson_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id : Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    notes : Mapped[str]
    date: Mapped[datetime.date] = mapped_column(Date)
    begin : Mapped[datetime.time] = mapped_column(Time(timezone=False), nullable=False)
    end : Mapped[datetime.time] = mapped_column(Time(timezone=False), nullable=False)

    student = relationship("Student", back_populates="lesson_plans")

class StudentResponse(BaseModel):
    id: int
    name: Optional[str]
    grade: Optional[int]
    descriptions: Optional[str]
    contacts: Optional[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class LessonCreate(BaseModel):
    student_id : int
    notes:Optional[str]
    date:datetime.date
    begin : datetime.time
    end : datetime.time
    recurring : bool

class LessonGet(BaseModel):
    id: Optional[int] = None
    student_id: int
    notes: Optional[str] = None
    date: str
    begin: datetime.time
    end: datetime.time
    name: str
    grade: Optional[int] = None
    recurring: Optional[bool] = None  # если есть в базе

    model_config = ConfigDict(from_attributes=True)
    @field_serializer("begin", "end")
    def serialize_time(self, value: datetime.time):
        return value.strftime("%H:%M")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=True)
    grade : Mapped[int] = mapped_column(nullable=True)
    descriptions : Mapped[str]
    contacts : Mapped[str]
    created_at : Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    lesson_plans = relationship("LessonPlan", back_populates="student", cascade="all, delete")


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
    
async def update_student_orm(user_id : int, data : dict):
    async with async_session_maker() as sessions:
        stat = (
            update(Student)
            .where(Student.id == user_id)
            .values(**data)
        )
        result = await sessions.execute(stat)
        await sessions.commit()
        return {"message":"good"} # сюда написать логику обновления бд
    
async def delete_student_orm(user_id : int):
    async with async_session_maker() as sessions:
        stat = (delete(Student)
                .where(Student.id == user_id))
        await sessions.execute(stat)
        await sessions.commit()
        return {"message":"good"}

async def create_lesson_orm(data: LessonCreate):
    async with async_session_maker() as sessions:
        lesson = LessonPlan(
            student_id=data.student_id,
            notes=data.notes,
            date=data.date,
            begin=data.begin,
            end=data.end
        )
        sessions.add(lesson)
        await sessions.commit()
        return {"message":f"Занятие добавлено"}
    
async def get_lessons_all():
    async with async_session_maker() as sessions:
        result = await sessions.execute(
            select(LessonPlan).options(selectinload(LessonPlan.student))
        )
        lessons = result.scalars().unique().all()

        lessons_scheme = [
            LessonGet(
                id=lesson.id,
                student_id=lesson.student_id,
                notes=lesson.notes,
                date=lesson.date.strftime("%Y-%m-%d"),
                begin=lesson.begin,
                end=lesson.end,
                name=lesson.student.name or "Без имени",
                grade=lesson.student.grade,
                recurring=False  # или lesson.recurring, если есть поле
            )
            for lesson in lessons
        ]

        return [u.model_dump() for u in lessons_scheme]