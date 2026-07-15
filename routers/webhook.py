import json
import os
import secrets
import string
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database import get_conn
from auth import get_user_by_email, create_user
from services.email_service import enviar_credenciais, enviar_acesso_reativado

router = APIRouter(tags=["Webhook"])

# Payt V1 status → ativar acesso
STATUS_ATIVAR = {
    "subscription_activated",   # nova assinatura confirmada
    "subscription_renewed",     # renovação mensal paga
    "subscription_reactivated", # reativada após atraso
    "paid",                     # venda avulsa paga
}

# Payt V1 status → bloquear acesso
STATUS_BLOQUEAR = {
    "subscription_canceled",    # cancelada (cliente, admin, atraso)
    "subscription_overdue",     # em atraso
    "canceled",                 # pedido cancelado
}

PAYT_KEY = os.getenv("PAYT_INTEGRATION_KEY", "")


def _gerar_senha(n: int = 10) -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(chars) for _ in range(n))


def _log(conn, evento: str, payload: dict):
    conn.execute(
        "INSERT INTO webhook_logs (evento, payload) VALUES (?, ?)",
        (evento, json.dumps(payload, ensure_ascii=False)),
    )


def _ativar(uid: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET ativo = 1, plano = 'mensal' WHERE id = ?", (uid,)
        )


def _bloquear(uid: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET ativo = 0, plano = 'free' WHERE id = ?", (uid,)
        )


def _upsert_assinatura(uid, email: str, order_id: str, status: str, valor):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM assinaturas WHERE payt_order_id = ?", (order_id,)
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE assinaturas SET status=?, atualizado_em=datetime('now') WHERE payt_order_id=?",
                (status, order_id),
            )
        else:
            conn.execute(
                "INSERT INTO assinaturas (user_id, payt_email, payt_order_id, status, valor) VALUES (?,?,?,?,?)",
                (uid, email, order_id, status, valor),
            )


@router.post("/webhook/payt")
async def webhook_payt(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # Log imediato
    with get_conn() as conn:
        _log(conn, payload.get("status", "unknown"), payload)

    # Validar integration_key (só se PAYT_INTEGRATION_KEY estiver configurada)
    if PAYT_KEY and payload.get("integration_key") != PAYT_KEY:
        return JSONResponse({"ok": False, "msg": "chave invalida"}, status_code=401)

    # Ignorar testes silenciosamente (mas logar)
    if payload.get("test") is True:
        return JSONResponse({"ok": True, "msg": "teste ignorado"})

    status = payload.get("status", "")
    customer = payload.get("customer", {})
    email = customer.get("email", "").lower().strip()
    nome = customer.get("name", "")
    fake_email = customer.get("fake_email", False)
    order_id = payload.get("transaction_id") or payload.get("cart_id", "")
    valor = payload.get("transaction", {}).get("total_price", 0)

    if not email or fake_email:
        return JSONResponse({"ok": True, "msg": "sem email valido"})

    # ── ATIVAR ──────────────────────────────────────────────────────────────────
    if status in STATUS_ATIVAR:
        user = get_user_by_email(email)

        if not user:
            # Criar conta automaticamente
            senha = _gerar_senha()
            uid = create_user(email=email, password=senha, nome=nome)
            _ativar(uid)
            _upsert_assinatura(uid, email, order_id, "ativa", valor)
            # Enviar credenciais por email
            enviar_credenciais(nome=nome, email=email, senha=senha)
            return JSONResponse({"ok": True, "msg": "conta criada e ativada"})

        uid = user["id"]
        _ativar(uid)
        _upsert_assinatura(uid, email, order_id, "ativa", valor)

        # Notificar renovação apenas se já tinha conta
        if status in {"subscription_renewed", "subscription_reactivated"}:
            enviar_acesso_reativado(nome=nome or user.get("nome", ""), email=email)

        return JSONResponse({"ok": True, "msg": "usuario ativado"})

    # ── BLOQUEAR ─────────────────────────────────────────────────────────────────
    if status in STATUS_BLOQUEAR:
        user = get_user_by_email(email)
        if user:
            _bloquear(user["id"])
            _upsert_assinatura(user["id"], email, order_id, "cancelada", valor)
        return JSONResponse({"ok": True, "msg": "usuario bloqueado"})

    # Qualquer outro status — só loga
    return JSONResponse({"ok": True, "msg": f"status {status!r} ignorado"})
