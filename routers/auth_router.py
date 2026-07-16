from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import (
    get_user_by_email, create_user, verify_password,
    create_session, get_current_user, COOKIE, MAX_AGE
)

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def page_login(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def do_login(
    request: Request,
    response: Response,
    email: str = Form(...),
    senha: str = Form(...),
):
    user = get_user_by_email(email)
    if not user or not verify_password(senha, user["password"]):
        return templates.TemplateResponse(
            "login.html", {"request": request, "erro": "E-mail ou senha incorretos."}
        )
    token = create_session(user["id"])
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(COOKIE, token, max_age=MAX_AGE, httponly=True, samesite="lax")
    return resp


@router.get("/cadastro", response_class=HTMLResponse)
async def page_cadastro(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("cadastro.html", {"request": request})


@router.post("/cadastro", response_class=HTMLResponse)
async def do_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
):
    if get_user_by_email(email):
        return templates.TemplateResponse(
            "cadastro.html",
            {"request": request, "erro": "E-mail já cadastrado."},
        )
    uid = create_user(email, senha, nome)
    token = create_session(uid)
    resp = RedirectResponse("/planos", status_code=302)
    resp.set_cookie(COOKIE, token, max_age=MAX_AGE, httponly=True, samesite="lax")
    return resp


@router.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie(COOKIE)
    return resp


@router.get("/planos", response_class=HTMLResponse)
async def page_planos(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("planos.html", {"request": request, "user": user})


@router.get("/vendas", response_class=HTMLResponse)
async def page_vendas(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("vendas.html", {"request": request, "user": user})
