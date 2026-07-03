from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import cpf, cnpj, cep, score
from routers.auth_router import router as auth_router
from routers.webhook import router as webhook_router
from database import init_db
from auth import get_current_user

init_db()

app = FastAPI(title="FNX Consultas", version="2.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rotas públicas
app.include_router(auth_router)
app.include_router(webhook_router)

# Rotas protegidas
app.include_router(cpf.router)
app.include_router(cnpj.router)
app.include_router(cep.router)
app.include_router(score.router)

# Rotas que exigem assinatura ativa
ROTAS_PROTEGIDAS = ["/cpf", "/cnpj", "/cep", "/score"]


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    protegida = any(path.startswith(r) for r in ROTAS_PROTEGIDAS)

    if protegida:
        user = get_current_user(request)
        if not user:
            return RedirectResponse("/login", status_code=302)
        if not user["ativo"]:
            return RedirectResponse("/planos", status_code=302)

    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/vendas", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
