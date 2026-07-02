import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

HUB_TOKEN = os.getenv("HUB_TOKEN")
HUB_BASE = os.getenv("HUB_BASE_URL")

CPFCNPJ_TOKEN = os.getenv("CPFCNPJ_TOKEN")
CPFCNPJ_BASE = os.getenv("CPFCNPJ_BASE_URL")

TIMEOUT = 30.0


async def _get(url: str) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


# ── CPF via cpfcnpj.com.br ──────────────────────────────────────────────────

async def consultar_cpf(cpf: str) -> dict:
    """Pacote 9: nome, nascimento, mãe, gênero + situação cadastral completa."""
    url = f"{CPFCNPJ_BASE}/{CPFCNPJ_TOKEN}/9/{cpf}"
    return await _get(url)


async def consultar_cpf_enderecos(cpf: str) -> dict:
    """Pacote 3: endereços vinculados ao CPF."""
    url = f"{CPFCNPJ_BASE}/{CPFCNPJ_TOKEN}/3/{cpf}"
    return await _get(url)


async def consultar_cpf_completo(cpf: str) -> tuple[dict, dict]:
    """Faz as duas consultas em paralelo e retorna (dados_pessoais, enderecos)."""
    return await asyncio.gather(
        consultar_cpf(cpf),
        consultar_cpf_enderecos(cpf),
    )


# ── CPF via Hub do Desenvolvedor (dados completos: telefones, emails, etc.) ──

async def consultar_cpf_basico_hub(cpf: str, data_nascimento: str) -> dict:
    url = f"{HUB_BASE}/cpf/?cpf={cpf}&data={data_nascimento}&token={HUB_TOKEN}"
    return await _get(url)


async def consultar_cpf_dados_hub(cpf: str) -> dict:
    url = f"{HUB_BASE}/cadastropf/?cpf={cpf}&token={HUB_TOKEN}"
    return await _get(url)


# ── Score / Crédito via cpfcnpj.com.br (pacote 300, assíncrono) ─────────────

async def consultar_score(documento: str) -> dict:
    """Análise de crédito: score, Pefin/Refin, protestos, CCF, alertas.
    Faz polling até estado=concluido ou timeout de 30s."""
    url = f"{CPFCNPJ_BASE}/{CPFCNPJ_TOKEN}/300/{documento}"
    for _ in range(15):
        dados = await _get(url)
        if dados.get("estado") == "concluido":
            return dados
        await asyncio.sleep(2)
    return dados  # retorna o último estado mesmo sem concluir


# ── CNPJ via cpfcnpj.com.br ─────────────────────────────────────────────────

async def consultar_cnpj(cnpj: str) -> dict:
    """Pacote 6: dados completos da empresa (sócios, CNAE, situação, etc.)."""
    url = f"{CPFCNPJ_BASE}/{CPFCNPJ_TOKEN}/6/{cnpj}"
    return await _get(url)


# ── CEP via Hub do Desenvolvedor ─────────────────────────────────────────────

async def consultar_cep(cep: str) -> dict:
    url = f"{HUB_BASE}/cep3/?cep={cep}&token={HUB_TOKEN}"
    return await _get(url)
