from __future__ import annotations

import html
import json
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.adapters import AuthDependencies, create_auth_dependencies, load_portfolio
from src.domain import Opportunity, User
from src.services import (
    AuthError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    WeakPassword,
    current_user,
    generate_discovery_roteiro,
    login_with_password,
    register_user,
)


PORTFOLIO_PATH = Path("data/portfolio/reference_portfolio.json")
SESSION_COOKIE = "onion_session"


def page(body: str) -> bytes:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agente de Pre-vendas</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; line-height: 1.45; color: #1f2933; }}
    main {{ max-width: 980px; margin: 0 auto; }}
    label {{ display: block; font-weight: 700; margin-top: 16px; }}
    input, textarea {{ width: 100%; box-sizing: border-box; padding: 10px; margin-top: 6px; }}
    textarea {{ min-height: 110px; }}
    button {{ margin-top: 18px; padding: 10px 14px; cursor: pointer; }}
    nav {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; }}
    nav form {{ margin: 0; }}
    .error {{ background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; padding: 12px; }}
    .muted {{ color: #52606d; }}
    pre {{ background: #f4f6f8; padding: 16px; overflow: auto; white-space: pre-wrap; }}
  </style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>""".encode("utf-8")


def app_form(user: User) -> str:
    display_name = html.escape(user.display_name or user.email.value)
    return f"""
<nav>
  <div class="muted">Conectado como {display_name}</div>
  <form method="post" action="/logout">
    <button type="submit">Sair</button>
  </form>
</nav>
<h1>Agente de IA para Roteiro de Levantamento</h1>
<form method="post">
  <label>Descricao da oportunidade</label>
  <textarea name="description" required></textarea>
  <label>Tipo de solucao</label>
  <input name="solution_type" placeholder="ex: cloud, backup, SOC">
  <label>Cliente ou segmento</label>
  <input name="customer_segment">
  <label>Objetivo da demanda</label>
  <input name="objective">
  <label>Escopo inicial</label>
  <textarea name="initial_scope"></textarea>
  <button type="submit">Gerar roteiro</button>
</form>
"""


def login_form(error: str = "") -> str:
    return f"""
<h1>Entrar</h1>
{error_block(error)}
<form method="post" action="/login">
  <label>Email</label>
  <input name="email" type="email" required>
  <label>Senha</label>
  <input name="password" type="password" required>
  <button type="submit">Entrar</button>
</form>
<p class="muted">Ainda nao tem conta? <a href="/register">Criar cadastro</a>.</p>
"""


def register_form(error: str = "") -> str:
    return f"""
<h1>Criar cadastro</h1>
{error_block(error)}
<form method="post" action="/register">
  <label>Nome</label>
  <input name="display_name">
  <label>Email</label>
  <input name="email" type="email" required>
  <label>Senha</label>
  <input name="password" type="password" minlength="8" required>
  <button type="submit">Cadastrar</button>
</form>
<p class="muted">Ja tem conta? <a href="/login">Entrar</a>.</p>
"""


def error_block(message: str) -> str:
    if not message:
        return ""
    return f'<div class="error">{html.escape(message)}</div>'


class Handler(BaseHTTPRequestHandler):
    auth_deps: AuthDependencies | None = None

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/login":
            self.handle_login_get()
            return
        if path == "/register":
            self.handle_register_get()
            return
        if path == "/":
            self.handle_app_get()
            return
        self.respond_not_found()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/login":
            self.handle_login_post()
            return
        if path == "/register":
            self.handle_register_post()
            return
        if path == "/logout":
            self.handle_logout_post()
            return
        if path == "/":
            self.handle_app_post()
            return
        self.respond_not_found()

    def handle_login_get(self) -> None:
        if self.authenticated_user() is not None:
            self.redirect("/")
            return
        self.respond(page(login_form()))

    def handle_login_post(self) -> None:
        data = self.read_form_data()
        try:
            _, session = login_with_password(
                email=data.get("email", [""])[0],
                password=data.get("password", [""])[0],
                users=self.deps.users,
                hasher=self.deps.hasher,
                sessions=self.deps.sessions,
            )
        except InvalidCredentials:
            self.respond(page(login_form("Email ou senha invalidos.")), status=401)
            return

        self.redirect("/", cookie=self.session_cookie(session.token))

    def handle_register_get(self) -> None:
        if self.authenticated_user() is not None:
            self.redirect("/")
            return
        self.respond(page(register_form()))

    def handle_register_post(self) -> None:
        data = self.read_form_data()
        try:
            _, session = register_user(
                email=data.get("email", [""])[0],
                password=data.get("password", [""])[0],
                display_name=data.get("display_name", [""])[0],
                users=self.deps.users,
                hasher=self.deps.hasher,
                sessions=self.deps.sessions,
            )
        except EmailAlreadyRegistered:
            self.respond(page(register_form("Este email ja esta cadastrado.")), status=400)
            return
        except WeakPassword:
            self.respond(page(register_form("A senha deve ter pelo menos 8 caracteres.")), status=400)
            return
        except AuthError:
            self.respond(page(register_form("Nao foi possivel criar o cadastro.")), status=400)
            return

        self.redirect("/", cookie=self.session_cookie(session.token))

    def handle_logout_post(self) -> None:
        token = self.session_token()
        if token:
            self.deps.sessions.revoke_session(token)
        self.redirect("/login", cookie=self.clear_session_cookie())

    def handle_app_get(self) -> None:
        user = self.authenticated_user()
        if user is None:
            self.redirect("/login")
            return
        self.respond(page(app_form(user)))

    def handle_app_post(self) -> None:
        user = self.authenticated_user()
        if user is None:
            self.redirect("/login")
            return

        data = self.read_form_data()
        body = self.generate_roteiro_body(data, user)
        self.respond(page(body))

    def generate_roteiro_body(self, data: dict[str, list[str]], user: User) -> str:
        opportunity = Opportunity(
            description=data.get("description", [""])[0],
            solution_type=data.get("solution_type", [""])[0],
            customer_segment=data.get("customer_segment", [""])[0],
            objective=data.get("objective", [""])[0],
            initial_scope=data.get("initial_scope", [""])[0],
        )
        portfolio = load_portfolio(PORTFOLIO_PATH)
        roteiro = generate_discovery_roteiro(opportunity, portfolio)
        rendered = html.escape(roteiro.to_markdown())
        raw_json = html.escape(json.dumps(roteiro.to_dict(), ensure_ascii=False, indent=2))
        return f"""
<nav>
  <div class="muted">Conectado como {html.escape(user.display_name or user.email.value)}</div>
  <form method="post" action="/logout">
    <button type="submit">Sair</button>
  </form>
</nav>
<h1>Roteiro gerado</h1>
<pre>{rendered}</pre>
<details><summary>JSON estruturado</summary><pre>{raw_json}</pre></details>
<p><a href="/">Gerar outro roteiro</a></p>
"""

    @property
    def deps(self) -> AuthDependencies:
        if self.auth_deps is None:
            raise RuntimeError("Auth dependencies were not initialized.")
        return self.auth_deps

    def authenticated_user(self) -> User | None:
        return current_user(
            self.session_token(),
            users=self.deps.users,
            sessions=self.deps.sessions,
        )

    def session_token(self) -> str | None:
        cookie_header = self.headers.get("Cookie", "")
        cookies = SimpleCookie(cookie_header)
        morsel = cookies.get(SESSION_COOKIE)
        if morsel is None:
            return None
        return morsel.value

    def read_form_data(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        return parse_qs(self.rfile.read(length).decode("utf-8"))

    def session_cookie(self, token: str) -> str:
        return f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Lax; Path=/"

    def clear_session_cookie(self) -> str:
        return f"{SESSION_COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"

    def redirect(self, location: str, cookie: str | None = None) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        if cookie is not None:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def respond(
        self,
        payload: bytes,
        status: int = 200,
        cookie: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if cookie is not None:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(payload)

    def respond_not_found(self) -> None:
        self.respond(page("<h1>Pagina nao encontrada</h1>"), status=404)


def main() -> int:
    Handler.auth_deps = create_auth_dependencies()
    server = ThreadingHTTPServer(("127.0.0.1", 8501), Handler)
    print("Servidor em http://127.0.0.1:8501")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
