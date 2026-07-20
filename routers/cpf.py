import asyncio
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.hub_api import (
    consultar_cpf,
    consultar_cpf_enderecos,
    consultar_cpf_basico_hub,
)

router = APIRouter(prefix="/cpf", tags=["CPF"])
templates = Jinja2Templates(directory="templates")


def _normalizar(dados9: dict, dados3: dict) -> dict | None:
    if dados9.get("status") != 1:
        return None
    enderecos = []
    for e in dados3.get("enderecos", []):
        enderecos.append({
            "logradouro": e.get("logradouro", ""),
            "numero":     e.get("numero", ""),
            "complemento": e.get("complemento", ""),
            "bairro":     e.get("bairro", ""),
            "cidade":     e.get("cidade", ""),
            "uf":         e.get("uf", ""),
            "cep":        e.get("cep", ""),
        })
    genero_raw = dados9.get("genero", "")
    genero = "Masculino" if genero_raw == "M" else ("Feminino" if genero_raw == "F" else genero_raw)
    return {
        "nomeCompleto":    dados9.get("nome", ""),
        "documento":       dados9.get("cpf", ""),
        "genero":          genero,
        "dataDeNascimento": dados9.get("nascimento", ""),
        "nomeDaMae":       dados9.get("mae", ""),
        "situacao":        dados9.get("situacao", ""),
        "listaEnderecos":  enderecos,
        "listaTelefones":  [],
        "listaEmails":     [],
    }


# ── CPF Principal ─────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def form_cpf(request: Request):
    return templates.TemplateResponse("cpf_dados.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def resultado_cpf(request: Request, cpf: str = Form(...)):
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    try:
        dados9, dados3 = await asyncio.gather(
            consultar_cpf(cpf_limpo),
            consultar_cpf_enderecos(cpf_limpo),
        )
        resultado = _normalizar(dados9, dados3)
        erro = None if resultado else dados9.get("message", "CPF não encontrado.")
    except Exception as e:
        resultado = None
        erro = str(e)
    return templates.TemplateResponse(
        "cpf_dados.html",
        {"request": request, "resultado": resultado, "erro": erro, "cpf": cpf},
    )


# ── CPF Situação Cadastral (Hub — validação com data de nascimento) ───────────

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


# ── /cpf/dados redireciona para / ────────────────────────────────────────────

@router.get("/dados", response_class=HTMLResponse)
async def form_cpf_dados(request: Request):
    return templates.TemplateResponse("cpf_dados.html", {"request": request})


@router.post("/dados", response_class=HTMLResponse)
async def resultado_cpf_dados(request: Request, cpf: str = Form(...)):
    return await resultado_cpf(request=request, cpf=cpf)
