from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.db.session import init_db
from app.api.v1.routers import conversations, discovery, health, portfolio, prompts

configure_logging()
settings = get_settings()

app = FastAPI(title="Gym.AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # MVP: cria tabelas diretamente. Produção usa `alembic upgrade head` (specs/phase-07/003).
    init_db()


app.include_router(health.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(discovery.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(prompts.router, prefix="/api/v1")
