from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from typing import Optional
import sqlite3
from contextlib import asynccontextmanager
from app.models import Snippet, Collaborator, Task

DATABASE_FILE = "/opt/render/project/src/app_data.db"
#DATABASE_FILE = "/home/BrnLng/snippet_flow_app/app_data.db" <   File "/opt/render/project/src/main.py", line 24, in get_db_connection

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        );
    """)
    # Adiciona um usuário de teste se não existir
    cursor.execute("SELECT * FROM users WHERE username = 'bruno'")
    if not cursor.fetchone():
        hashed_password = pwd_context.hash("senhak") # Senha de teste
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", ('bruno', hashed_password))
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando o aplicativo...")
    init_db()
    yield  # O aplicativo roda aqui
    print("Desligando o aplicativo...")


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_from_db(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


# "Middleware" de autenticação simplificado (para uso em Depends)
async def get_current_user(request: Request) -> Optional[dict]:
    session_id = request.cookies.get("session_id") # Um cookie simples para simular sessão
    if session_id == "logged_in": # Apenas um placeholder; em app real, seria um JWT ou DB lookup
        return {"username": "bruno"} # Mock de usuário logado
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")


# ############## ROTAS DA APLICAÇÃO ################

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.cookies.get("session_id") == "logged_in":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})


@app.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_data = get_user_from_db(username)

    if not user_data or not verify_password(password, user_data["hashed_password"]):
        # Retorna o formulário com mensagem de erro se a autenticação falhar
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Usuário ou senha inválidos."},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Sucesso no login - redireciona para o dashboard
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value="logged_in", httponly=True, max_age=3600) # Simula sessão
    return response


@app.post("/logout", response_class=RedirectResponse)
async def process_logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": current_user["username"]})


@app.get("/api/data")
async def get_data(current_user: dict = Depends(get_current_user)):
    return {"message": f"Bem-vindo, {current_user['username']}! Seus dados secretos aqui."}


@app.get("/ping")
async def ping():
    return {"status": "pong"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
