# Gym.AI

MVP com backend em FastAPI (Python) e frontend em React + Vite (TypeScript). O backend orquestra
agentes que conversam com um provedor de LLM (hoje, OpenRouter) para descoberta e geração de
recomendações; o frontend consome essa API.

## Estrutura

```
project/
├── backend/     # FastAPI + SQLAlchemy + Alembic
└── frontend/    # React + Vite + Zustand
```

## Pré-requisitos

- Python 3.11+
- Node.js 20+
- Um banco Postgres (recomendado: [Supabase](https://supabase.com)) ou SQLite local para dev
- Uma API key de LLM (hoje, [OpenRouter](https://openrouter.ai))

## Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

cp .env.example .env
# edite .env com DATABASE_URL, OPENROUTER_API_KEY etc.

alembic upgrade head           # aplica as migrações (ou deixe o startup criar as tabelas em dev)
uvicorn app.main:app --reload  # sobe a API em http://127.0.0.1:8000
```

Variáveis de ambiente principais (ver `backend/.env.example`):

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | Connection string do Postgres (ou `sqlite:///./gym_ai.db` para dev local) |
| `OPENROUTER_API_KEY` | Chave da API do OpenRouter, usada pelo provedor de LLM |
| `OPENROUTER_MODEL` | Modelo a ser usado (padrão: `openrouter/auto`) |
| `DEV_TENANT_API_KEY` / `DEV_TENANT_SLUG` | Auth simplificada do MVP: API key estática por tenant |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas para o frontend |

### Rodando os testes

```bash
cd backend
pytest
```

## Frontend

```bash
cd frontend
npm install

cp .env.example .env
# ajuste VITE_API_BASE_URL e VITE_API_KEY se necessário

npm run dev       # http://localhost:5173
```

Variáveis de ambiente (ver `frontend/.env.example`):

| Variável | Descrição |
| --- | --- |
| `VITE_API_BASE_URL` | URL base da API backend |
| `VITE_API_KEY` | API key do tenant de dev (deve bater com `DEV_TENANT_API_KEY` do backend) |

Outros comandos úteis: `npm run build`, `npm run lint`, `npm run preview`.

## Autenticação

O MVP usa apenas uma API key estática por tenant (`DEV_TENANT_API_KEY`) — não há cadastro/login de
usuário final. Ver issue de autenticação para o plano de evolução (Google OAuth + email/senha).
