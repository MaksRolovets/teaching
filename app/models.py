from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from test import Base, uniq_str_an
from sqlalchemy.types import String, DateTime, Integer, Text
from sql_enum import RatingEnum



class User(Base):
    username : Mapped[uniq_str_an] 
    email : Mapped[uniq_str_an]
    password : Mapped[str]
    profile_id : Mapped[int | None] = mapped_column(ForeignKey('profiles.id'))

class Comment(Base):
    content : Mapped[Text]  
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    is_published: Mapped[bool] = mapped_column(default=True, server_default=text("'false'"))
    rating : Mapped[RatingEnum] = mapped_column(default=RatingEnum.FIVE, server_default=text("'SEVEN'"))