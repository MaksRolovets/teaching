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
    return templates.TemplateResponse("2.html", {"request":req})
               
               
               
               
               
               

