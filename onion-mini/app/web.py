from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from src.adapters import load_portfolio
from src.domain import Opportunity
from src.services import generate_discovery_roteiro


PORTFOLIO_PATH = Path("data/portfolio/reference_portfolio.json")


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
    pre {{ background: #f4f6f8; padding: 16px; overflow: auto; white-space: pre-wrap; }}
  </style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>""".encode("utf-8")


FORM = """
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


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.respond(page(FORM))

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        data = parse_qs(self.rfile.read(length).decode("utf-8"))
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
        body = f"""
<h1>Roteiro gerado</h1>
<pre>{rendered}</pre>
<details><summary>JSON estruturado</summary><pre>{raw_json}</pre></details>
<p><a href="/">Gerar outro roteiro</a></p>
"""
        self.respond(page(body))

    def respond(self, payload: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8501), Handler)
    print("Servidor em http://127.0.0.1:8501")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
