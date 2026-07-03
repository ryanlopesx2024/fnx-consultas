import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database import get_conn

router = APIRouter(tags=["Webhook"])

# Eventos que ATIVAM o acesso
EVENTOS_APROVADOS = {"Finalizada/Aprovada", "finalizada", "aprovada", "Aprovada"}

# Eventos que BLOQUEIAM o acesso
EVENTOS_CANCELADOS = {
    "Cancelada", "cancelada",
    "Cancelada - Chargeback", "chargeback",
    "Cancelada - Reembolsada", "reembolsada",
    "Solicitação de Reembolso",
}


@router.post("/webhook/payt")
async def webhook_payt(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    evento = payload.get("status") or payload.get("evento") or payload.get("event", "")
    email = (
        payload.get("customer", {}).get("email")
        or payload.get("email")
        or payload.get("buyer_email", "")
    )
    order_id = payload.get("order_id") or payload.get("id", "")
    valor = payload.get("value") or payload.get("valor") or 0

    # Logar sempre
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO webhook_logs (evento, payload) VALUES (?, ?)",
            (evento, json.dumps(payload, ensure_ascii=False)),
        )

    if not email:
        return JSONResponse({"ok": True, "msg": "sem email"})

    # Buscar usuário pelo e-mail
    with get_conn() as conn:
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()

    if not user:
        # Registra assinatura pendente mesmo sem usuário (pode se cadastrar depois)
        _upsert_assinatura(None, email, order_id, evento, valor)
        return JSONResponse({"ok": True, "msg": "usuario nao encontrado"})

    uid = user["id"]

    if evento in EVENTOS_APROVADOS:
        _ativar_usuario(uid)
        _upsert_assinatura(uid, email, order_id, "ativa", valor)

    elif evento in EVENTOS_CANCELADOS:
        _desativar_usuario(uid)
        _upsert_assinatura(uid, email, order_id, "cancelada", valor)

    else:
        _upsert_assinatura(uid, email, order_id, evento, valor)

    return JSONResponse({"ok": True})


def _ativar_usuario(uid: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET ativo = 1, plano = 'mensal' WHERE id = ?", (uid,)
        )


def _desativar_usuario(uid: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET ativo = 0, plano = 'free' WHERE id = ?", (uid,)
        )


def _upsert_assinatura(uid, email, order_id, status, valor):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM assinaturas WHERE payt_order_id = ?", (order_id,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE assinaturas SET status = ?, atualizado_em = datetime('now') WHERE payt_order_id = ?",
                (status, order_id),
            )
        else:
            conn.execute(
                "INSERT INTO assinaturas (user_id, payt_email, payt_order_id, status, valor) VALUES (?,?,?,?,?)",
                (uid, email, order_id, status, valor),
            )
