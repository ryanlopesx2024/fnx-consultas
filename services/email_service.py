import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
_PORT = int(os.getenv("EMAIL_PORT", "587"))
_USER = os.getenv("EMAIL_USER", "")
_PASS = os.getenv("EMAIL_PASS", "")


def _send(to: str, subject: str, html: str) -> bool:
    if not _USER or not _PASS:
        print(f"[EMAIL] sem credenciais configuradas — to={to} subject={subject}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"FNX Consultas <{_USER}>"
        msg["To"] = to
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(_HOST, _PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(_USER, _PASS)
            smtp.sendmail(_USER, to, msg.as_string())
        print(f"[EMAIL] enviado → {to}")
        return True
    except Exception as e:
        print(f"[EMAIL] erro → {e}")
        return False


def enviar_credenciais(nome: str, email: str, senha: str) -> bool:
    primeiro = nome.split()[0] if nome else "cliente"
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#000;font-family:'Arial',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#000;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:#0d0d0d;border:1px solid #1e1e1e;">

        <!-- header -->
        <tr>
          <td style="padding:32px 40px 24px;border-bottom:1px solid #1e1e1e;">
            <p style="margin:0;font-family:'Arial Black',sans-serif;font-size:22px;
                       letter-spacing:6px;color:#fff;text-transform:uppercase;">
              FNX CONSULTAS
            </p>
          </td>
        </tr>

        <!-- body -->
        <tr>
          <td style="padding:36px 40px;">
            <p style="color:#888;font-size:12px;letter-spacing:3px;text-transform:uppercase;margin:0 0 16px;">
              Bem-vindo(a)
            </p>
            <h1 style="color:#fff;font-size:24px;margin:0 0 24px;font-weight:700;">
              Olá, {primeiro}!
            </h1>
            <p style="color:#aaa;font-size:14px;line-height:1.8;margin:0 0 32px;">
              Seu acesso ao <strong style="color:#fff;">FNX Consultas</strong> foi liberado.<br/>
              Use as credenciais abaixo para entrar na plataforma.
            </p>

            <!-- credenciais -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#000;border:1px solid #1e1e1e;margin-bottom:32px;">
              <tr>
                <td style="padding:16px 20px;border-bottom:1px solid #1e1e1e;">
                  <p style="margin:0;font-size:10px;letter-spacing:2px;color:#555;text-transform:uppercase;">
                    E-mail
                  </p>
                  <p style="margin:4px 0 0;font-size:15px;color:#fff;">{email}</p>
                </td>
              </tr>
              <tr>
                <td style="padding:16px 20px;">
                  <p style="margin:0;font-size:10px;letter-spacing:2px;color:#555;text-transform:uppercase;">
                    Senha
                  </p>
                  <p style="margin:4px 0 0;font-size:15px;color:#fff;font-family:monospace;">
                    {senha}
                  </p>
                </td>
              </tr>
            </table>

            <a href="https://fnx-consultas.onrender.com/login"
               style="display:inline-block;background:#fff;color:#000;
                      font-size:11px;font-weight:700;letter-spacing:3px;
                      text-transform:uppercase;text-decoration:none;
                      padding:14px 32px;">
              Acessar Agora
            </a>

            <p style="color:#555;font-size:12px;margin:28px 0 0;line-height:1.7;">
              Recomendamos que você troque sua senha após o primeiro acesso.<br/>
              Em caso de dúvidas, responda este e-mail.
            </p>
          </td>
        </tr>

        <!-- footer -->
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #1e1e1e;">
            <p style="margin:0;font-size:10px;letter-spacing:2px;color:#333;text-transform:uppercase;">
              &copy; 2025 FNX Corporation
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""
    return _send(to=email, subject="FNX Consultas — Seu acesso foi liberado", html=html)


def enviar_acesso_reativado(nome: str, email: str) -> bool:
    primeiro = nome.split()[0] if nome else "cliente"
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#000;font-family:'Arial',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#000;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="background:#0d0d0d;border:1px solid #1e1e1e;">
        <tr>
          <td style="padding:32px 40px 24px;border-bottom:1px solid #1e1e1e;">
            <p style="margin:0;font-family:'Arial Black',sans-serif;font-size:22px;
                       letter-spacing:6px;color:#fff;text-transform:uppercase;">
              FNX CONSULTAS
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;">
            <p style="color:#888;font-size:12px;letter-spacing:3px;text-transform:uppercase;margin:0 0 16px;">
              Assinatura Renovada
            </p>
            <h1 style="color:#fff;font-size:24px;margin:0 0 24px;font-weight:700;">
              Olá, {primeiro}!
            </h1>
            <p style="color:#aaa;font-size:14px;line-height:1.8;margin:0 0 32px;">
              Sua assinatura do <strong style="color:#fff;">FNX Consultas</strong> foi renovada com sucesso.<br/>
              Seu acesso continua ativo — boas consultas!
            </p>
            <a href="https://fnx-consultas.onrender.com/login"
               style="display:inline-block;background:#fff;color:#000;
                      font-size:11px;font-weight:700;letter-spacing:3px;
                      text-transform:uppercase;text-decoration:none;
                      padding:14px 32px;">
              Acessar Plataforma
            </a>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #1e1e1e;">
            <p style="margin:0;font-size:10px;letter-spacing:2px;color:#333;text-transform:uppercase;">
              &copy; 2025 FNX Corporation
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""
    return _send(to=email, subject="FNX Consultas — Assinatura renovada", html=html)
