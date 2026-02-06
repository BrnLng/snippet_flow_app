from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from passlib.context import CryptContext
from typing import Optional
from sqlmodel import SQLModel, Session, create_engine, select, or_

from app.models import User, Snippet, SnippetCollaboratorLink  #, SnippetHistory
from app.services import SnippetSerializer


VERSION = "0.138"


DATABASE_FILE = "sqlite:///app_data.db"
engine = create_engine(DATABASE_FILE, echo=True)  # echo=True ajuda a ver o SQL gerado no terminal (bom para debug)

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando o banco de dados...")
    SQLModel.metadata.create_all(engine)  # Cria as tabelas definidas no models.py se não existirem
    yield
    print("Desligando o aplicativo...")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Dependência para pegar o usuário atual baseado no cookie
def get_current_user(request: Request):
    username = request.cookies.get("session_user")
    if not username:
        return None
    
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        return user


@app.get("/", response_class=HTMLResponse)  # GET
async def root(request: Request):
    # Se já tiver cookie, vai pro dashboard, senão login
    if request.cookies.get("session_user"):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)  # GET
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})


@app.post("/login", response_class=HTMLResponse)  # POST -- sent form
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

        if not user or not verify_password(password, user.hashed_password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "message": "Usuário ou senha inválidos."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        # Login Success: Define simple cookie with username while in dev  TODO: proper cookies
        response = Response(status_code=200)
        response.headers["HX-Redirect"] = "/dashboard"
        #response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_user", value=user.username, httponly=True)
        return response


@app.post("/logout", response_class=RedirectResponse)  # POST
async def process_logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_user")
    return response


@app.get("/dashboard", response_class=HTMLResponse)  # GET
async def dashboard_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if (not current_user):  # TODO: if needed -- or (request["detail"] == "Não autenticado"):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    with Session(engine) as session:
        # "Super Query" for snippets where user is AUTHOR or COLABORATOR
        statement = (
            select(Snippet)
            .join(SnippetCollaboratorLink, isouter=True)  # Left join to include snippets without colab
            .where(
                or_(
                    Snippet.created_by_id == current_user.id,           # author
                    SnippetCollaboratorLink.user_id == current_user.id  # colaborator
                )
            )
            .distinct()  # clear duplicates
            .order_by(Snippet.updated_at.desc())  # updated or created TODO: decide
        )

        snippets = session.exec(statement).all()

        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request, 
                "username": current_user.username,
                "user_id": current_user.id,
                "snippets": snippets
            }
        )


@app.post("/snippet/{snippet_id}/save")  # POST
async def save_snippet(
    snippet_id: int, 
    request: Request,
    title: str = Form(...), 
    body: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    with Session(engine) as session:
        snippet = session.get(Snippet, snippet_id)
        if not snippet:
            raise HTTPException(status_code=404, detail="Snippet not found")
            
        snippet.title = title
        snippet.body = body
        # TODO: Aqui entraria lógica extra para atualizar tasks/tags quando virem do form
        
        session.add(snippet)
        session.commit()
        session.refresh(snippet)
        
        # History snapshot++
        full_text = SnippetSerializer.to_markdown(snippet)
        
        # TODO: history log
        # history = SnippetHistory(
        #     snippet_id=snippet.id,
        #     full_markdown=full_text,
        #     changed_by_id=current_user.id
        # )
        # session.add(history)
        session.commit()
        
        return templates.TemplateResponse(
            "partials/snippet_item.html",
            {
                "request": request, 
                "snippet": snippet, 
                "user_id": current_user.id
            }
        )


@app.get("/ping")
async def ping():
    return {"status": "pong", "version": VERSION, "db": "connected"}



@app.get("/admin/seed")
async def trigger_seed(key: str = None, current_user: Optional[User] = Depends(get_current_user)):
    # 1. Proteção básica: Só User.Bruno/admin pode usar ou precisa de uma KEY na URL
    # Ex: /admin/seed?key=vibe123
    if key != "l33tr":
        raise HTTPException(status_code=403, detail="Forbidden")

    import traceback
    from seed import seed_database

    try:

        seed_database()
        return {"status": "success", "message": "Database seeded successfully"}
    except Exception as e:
        #error_trace = traceback.format_exc()
        return {"status": "error", "message": str(e)}  #, "traceback": error_trace}
