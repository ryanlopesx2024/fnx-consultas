from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.hub_api import consultar_cep

router = APIRouter(prefix="/cep", tags=["CEP"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def form_cep(request: Request):
    return templates.TemplateResponse("cep.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def resultado_cep(request: Request, cep: str = Form(...)):
    cep_limpo = "".join(filter(str.isdigit, cep))

    try:
        dados = await consultar_cep(cep_limpo)
        resultado = dados if dados.get("return") == "OK" else None
        erro = None if resultado else dados.get("message", "CEP não encontrado.")
    except Exception as e:
        resultado = None
        erro = str(e)

    return templates.TemplateResponse(
        "cep.html",
        {"request": request, "resultado": resultado, "erro": erro, "cep": cep},
    )
