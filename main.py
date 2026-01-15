from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from typing import Optional
import sqlite3
from contextlib import asynccontextmanager

#app = FastAPI()

# 1. Configuração de Templates (Jinja2)
templates = Jinja2Templates(directory="templates")

# 2. Configuração de Hashing de Senha
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 3. Configuração do Banco de Dados SQLite
# Usaremos um arquivo SQLite simples. Para produção, considere PostGreSQL ou MySQL.
DATABASE_FILE = "app_data.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Para acessar colunas por nome
    return conn

# Função para inicializar o banco de dados (criar tabela de usuários)
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

# Inicializa o banco de dados na inicialização da aplicação -- OBSOLETO
# @app.on_event("startup")
# async def startup_event():
    # init_db()

# NOVO: Gerenciamento de Ciclo de Vida da Aplicação (Substitui @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que roda na inicialização (startup)
    print("Inicializando o banco de dados...") # Para depuração
    init_db()
    yield # O aplicativo roda aqui
    # Código que roda no desligamento (shutdown)
    print("Desligando o aplicativo...") # Para depuração

app = FastAPI(lifespan=lifespan) # NOVO: Passe o lifespan para a instância do FastAPI


# Funções de autenticação
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


# ROTAS DA APLICAÇÃO

# Rota inicial - redireciona para login ou dashboard
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.cookies.get("session_id") == "logged_in":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

# Página de Login (GET)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

# Endpoint de Login (POST, com HTMX)
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

# Endpoint de Logout (POST, com HTMX ou GET simples)
@app.post("/logout", response_class=RedirectResponse)
async def process_logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response

# Página do Dashboard (Protegida)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": current_user["username"]})


# Endpoint de API de Teste (Protegido)
@app.get("/api/data")
async def get_data(current_user: dict = Depends(get_current_user)):
    return {"message": f"Bem-vindo, {current_user['username']}! Seus dados secretos aqui."}

# Endpoint simples para verificar que o uvicorn está rodando
@app.get("/ping")
async def ping():
    return {"status": "pong"}




# from typing import Optional

# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Test Hello World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}