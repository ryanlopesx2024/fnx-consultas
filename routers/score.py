from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.hub_api import consultar_score

router = APIRouter(prefix="/score", tags=["Score"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def form_score(request: Request):
    return templates.TemplateResponse("score.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def resultado_score(request: Request, documento: str = Form(...)):
    doc_limpo = "".join(filter(str.isdigit, documento))

    try:
        dados = await consultar_score(doc_limpo)
        resultado = dados if dados.get("status") == 1 else None
        erro = None if resultado else dados.get("erro", "Documento não encontrado.")
    except Exception as e:
        resultado = None
        erro = str(e)

    return templates.TemplateResponse(
        "score.html",
        {"request": request, "resultado": resultado, "erro": erro, "documento": documento},
    )
