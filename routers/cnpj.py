from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.hub_api import consultar_cnpj

router = APIRouter(prefix="/cnpj", tags=["CNPJ"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def form_cnpj(request: Request):
    return templates.TemplateResponse("cnpj.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def resultado_cnpj(request: Request, cnpj: str = Form(...)):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))

    try:
        dados = await consultar_cnpj(cnpj_limpo)
        empresa = dados if dados.get("status") == 1 else None
        erro = None if empresa else dados.get("erro", "CNPJ não encontrado.")
    except Exception as e:
        empresa = None
        erro = str(e)

    return templates.TemplateResponse(
        "cnpj.html",
        {"request": request, "empresa": empresa, "erro": erro, "cnpj": cnpj},
    )
