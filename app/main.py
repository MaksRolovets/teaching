from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(title="Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # разрешаем только эти адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(api_router)
@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    return templates.TemplateResponse("4.html", {"request":req})
               
               
   # решить вопрос с навигацией(убрать даблклик) -
   # добавить удаление ученика(перерабоать кнопку написать логику)
   # добавить прокрут до сегодняшнего расписания
   # на дашборде показывать сколько сегодня уроков осталось и через сколько селдующий урок и с кем
   # создать изменени и модалку для распиасния
   # перерабоатть карточки расписания - 

   #             
               
               
               

