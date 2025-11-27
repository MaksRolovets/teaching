from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def get_lessons():
    data = [{"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"},
            {"date":"09-05-2007",
            "title":"Урок матана",
            "start":"9:00",
            "end":"10:00",
            "student":"Максончик епта"}]
    return data