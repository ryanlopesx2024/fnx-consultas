from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.hub_api import (
    consultar_cpf_completo,
    consultar_cpf_basico_hub,
    consultar_cpf_dados_hub,
)

router = APIRouter(prefix="/cpf", tags=["CPF"])
templates = Jinja2Templates(directory="templates")


# ── CPF Principal (Hub do Desenvolvedor — dados completos) ────────────────────

@router.get("/", response_class=HTMLResponse)
async def form_cpf(request: Request):
    return templates.TemplateResponse("cpf_dados.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def resultado_cpf(request: Request, cpf: str = Form(...)):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    try:
        dados = await consultar_cpf_dados_hub(cpf_limpo)
        resultado = dados.get("result") if dados.get("return") == "OK" else None
        erro = None if resultado else dados.get("message", "Sem dados encontrados.")
    except Exception as e:
        resultado = None
        erro = str(e)

    return templates.TemplateResponse(
        "cpf_dados.html",
        {"request": request, "resultado": resultado, "erro": erro, "cpf": cpf},
    )


# ── CPF Situação Cadastral (Hub) ──────────────────────────────────────────────

@router.get("/basico", response_class=HTMLResponse)
async def form_cpf_basico(request: Request):
    return templates.TemplateResponse("cpf_basico.html", {"request": request})


@router.post("/basico", response_class=HTMLResponse)
async def resultado_cpf_basico(
    request: Request,
    cpf: str = Form(...),
    data_nascimento: str = Form(...),
):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    # converte YYYY-MM-DD (input date) → DD/MM/YYYY
    if "-" in data_nascimento and data_nascimento.index("-") == 4:
        parts = data_nascimento.split("-")
        data_fmt = f"{parts[2]}/{parts[1]}/{parts[0]}"
    else:
        data_fmt = data_nascimento

    try:
        dados = await consultar_cpf_basico_hub(cpf_limpo, data_fmt)
        resultado = dados.get("result") if dados.get("return") == "OK" else None
        erro = None if resultado else dados.get("message", "Sem dados encontrados.")
    except Exception as e:
        resultado = None
        erro = str(e)

    return templates.TemplateResponse(
        "cpf_basico.html",
        {"request": request, "resultado": resultado, "erro": erro, "cpf": cpf},
    )


# ── CPF Dados Completos (Hub) ─────────────────────────────────────────────────

@router.get("/dados", response_class=HTMLResponse)
async def form_cpf_dados(request: Request):
    return templates.TemplateResponse("cpf_dados.html", {"request": request})


@router.post("/dados", response_class=HTMLResponse)
async def resultado_cpf_dados(request: Request, cpf: str = Form(...)):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    try:
        dados = await consultar_cpf_dados_hub(cpf_limpo)
        resultado = dados.get("result") if dados.get("return") == "OK" else None
        erro = None if resultado else dados.get("message", "Sem dados encontrados.")
    except Exception as e:
        resultado = None
        erro = str(e)

    return templates.TemplateResponse(
        "cpf_dados.html",
        {"request": request, "resultado": resultado, "erro": erro, "cpf": cpf},
    )
