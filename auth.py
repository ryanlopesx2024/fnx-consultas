import os
from typing import Optional
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from database import get_conn

load_dotenv()

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "dev-secret"))

COOKIE = "fnx_session"
MAX_AGE = 60 * 60 * 24 * 7  # 7 dias


# ── Senha ────────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ── Sessão (cookie assinado) ──────────────────────────────────────────────────

def create_session(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})


def decode_session(token: str) -> Optional[int]:
    try:
        data = serializer.loads(token, max_age=MAX_AGE)
        return data["uid"]
    except Exception:
        return None


# ── Usuário ───────────────────────────────────────────────────────────────────

def get_user_by_id(user_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def create_user(email: str, password: str, nome: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (email, password, nome) VALUES (?, ?, ?)",
            (email.lower().strip(), hash_password(password), nome),
        )
        return cur.lastrowid


def get_current_user(request) -> Optional[dict]:
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    uid = decode_session(token)
    if not uid:
        return None
    return get_user_by_id(uid)
