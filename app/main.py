from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
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
    return templates.TemplateResponse("3.html", {"request":req})

@app.get("/home", response_class=HTMLResponse)
async def landing(req: Request):
    return templates.TemplateResponse("home.html", {"request":req})

@app.get("/register", response_class=HTMLResponse)
async def register(req: Request):
    return templates.TemplateResponse("register.html", {"request":req})

@app.get("/login", response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse("login.html", {"request":req})
@app.get("/loaderio-f76114f7f153da931515ecee87dda3d5/")
async def l(req:Request):
    return FileResponse("dev_api/app/loaderio-f76114f7f153da931515ecee87dda3d5.txt")
   # решить вопрос с навигацией(убрать даблклик) -
   # добавить удаление ученика(перерабоать кнопку написать логику)
   # добавить прокрут до сегодняшнего расписания
   # на дашборде показывать сколько сегодня уроков осталось и через сколько селдующий урок и с кем
   # создать изменени и модалку для распиасния
   # перерабоатть карточки расписания - 

   #             
               
               
               

