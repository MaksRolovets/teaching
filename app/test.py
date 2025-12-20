from sqlalchemy.types import String, Boolean
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import func, ForeignKey,select, Time, Date, update, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from typing import Optional
import asyncio
import datetime


DATABASE_URL = "postgresql+asyncpg://makspg:1234@localhost/teaching"

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

from pydantic import BaseModel, ConfigDict, field_serializer
class RegisterUser(BaseModel):
    email : str
    password : str

class StudentCreate(BaseModel):
    name: Optional[str] 
    grade: Optional[int] 
    descriptions: Optional[str]  = ""
    contacts: Optional[str] = ""

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

class LessonUpdate(BaseModel):
    student_id: int
    notes: str | None
    date: datetime.date
    begin: datetime.time
    end: datetime.time

class LessonUpdateInput(LessonUpdate):
    recurring : bool

class LessonCreate(BaseModel):
    student_id : int
    notes:Optional[str]
    date:datetime.date
    begin : datetime.time
    end : datetime.time
    recurring : bool
    weeks : Optional[int] = 1

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

class UserResponse(BaseModel):
    id : int
    email: str
    password : str
    created_at : datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password : Mapped[str] = mapped_column(nullable=False)
    created_at : Mapped[datetime.datetime] = mapped_column(server_default=func.now(),nullable=False)
    refresh_tokens: Mapped[list["Tokens"]] = relationship(
        "Tokens",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    students : Mapped[list["Student"]] = relationship("Student", back_populates="user", cascade="all, delete-orphan")

class Tokens(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int]  = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash : Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at : Mapped[datetime.datetime] = mapped_column(server_default=func.now(),nullable=False)
    created_at : Mapped[datetime.datetime] =  mapped_column(server_default=func.now(),nullable=False)
    revoked : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user = relationship(
        "Users",
        back_populates="refresh_tokens"
    )

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    name : Mapped[str] = mapped_column(nullable=True)
    grade : Mapped[int] = mapped_column(nullable=True)
    descriptions : Mapped[str]
    contacts : Mapped[str]
    created_at : Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    lesson_plans = relationship("LessonPlan", back_populates="student", cascade="all, delete")
    user = relationship("Users", back_populates="students") 

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def insert_student(data : StudentCreate, user_id : int):
    async with async_session_maker() as sessions:
        sessions.add(Student(**data.model_dump(), user_id=user_id))
        await sessions.commit()
        return {"message":f"Студент {data.name} добавлен"}

async def select_users(user_id : int):
    async with async_session_maker() as sessions:
        result = await sessions.scalars(select(Student).where(Student.user_id == user_id))
        users = result.all()
        users_schema = [StudentResponse.model_validate(u) for u in users]
        return [u.model_dump() for u in users_schema]

async def select_student(user_id : int):
    async with async_session_maker() as sessions:
        result = await sessions.scalars(select(Student).where(Student.user_id == user_id))
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
        for week in range(data.weeks):
            lesson_date = data.date + datetime.timedelta(weeks=week)
            lesson = LessonPlan(
                student_id=data.student_id,
                notes=data.notes,
                date=lesson_date,
                begin=data.begin,
                end=data.end
            )
            sessions.add(lesson)
        await sessions.commit()
        return {"message":f"Занятие добавлено"}
    
async def get_lessons_all(user_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(LessonPlan)
            .join(LessonPlan.student)
            .where(Student.user_id == user_id)
            .options(selectinload(LessonPlan.student))
        )

        lessons = result.scalars().all()

        return [
            LessonGet(
                id=lesson.id,
                student_id=lesson.student_id,
                notes=lesson.notes,
                date=lesson.date.strftime("%Y-%m-%d"),
                begin=lesson.begin,
                end=lesson.end,
                name=lesson.student.name or "Без имени",
                grade=lesson.student.grade,
                recurring=False
            ).model_dump()
            for lesson in lessons
        ]

async def update_lessons_orm(lesson_id : int, data : LessonUpdateInput):
    async with async_session_maker() as sessions:
        payload = data.model_dump()

        # достаем recurring и одновременно удаляем
        recurring = payload.pop("recurring", None)
        data.date.strftime("%Y-%m-%d")
        stat = (
            update(LessonPlan)
            .where(LessonPlan.id == lesson_id)
            .values(**payload)
        )
        await sessions.execute(stat)
        await sessions.commit()
        return {"message":"update is good"}
    
async def delete_lessons_orm(lesson_id : int):
    async with async_session_maker() as sessions:
        stat = (
            delete(LessonPlan)
            .where(LessonPlan.id == lesson_id)
        )
        await sessions.execute(stat)
        await sessions.commit()
        return {"message":"delete is good"}

async def select_user(email: str):
    async with async_session_maker() as session:
        result = await session.scalars(
            select(Users).where(Users.email == email)
        )

        user = result.first()

        if not user:
            return None  # или raise HTTPException(status_code=404)

        return UserResponse.model_validate(user).model_dump()
    
async def select_user_id(id: int):
    async with async_session_maker() as session:
        result = await session.scalars(
            select(Users).where(Users.id == id)
        )

        user = result.first()

        if not user:
            return None  # или raise HTTPException(status_code=404)

        return UserResponse.model_validate(user)    
    
async def insert_user(data: RegisterUser):
    async with async_session_maker() as session:
        user = Users(
            email=data.email,
            password=data.password,
            created_at=datetime.datetime.now()
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return {
            "id": user.id,
            "message": f"Студент {data.email} добавлен"
        }

async def insert_token_orm(token : str, id : str): # тут тоже jti
    async with  async_session_maker() as session:
        token = Tokens(
            user_id=int(id),
            token_hash=token,
            expires_at=datetime.datetime.now()
        )
        session.add(token)
        await session.commit()
        return {"message":"Токен Добавлен"}
    
async def select_token_orm(jti : str):
    async with async_session_maker() as session:
        result = await session.scalars(
            select(Tokens).where(Tokens.token_hash == jti)#ЗАМЕНИТЬ на jti
        )

        user = result.first()

        if not user:
            return None
        return user
    
async def revoke_token_orm(jti : str): # ЗАМЕНИТЬ
    async with async_session_maker() as session:
        stat = (
            update(Tokens)
            .where(Tokens.token_hash == jti)
            .values(revoked = True)
        )
        await session.execute(stat)
        await session.commit()
        return {"message":"update is good"}