from __future__ import annotations

import json
from pathlib import Path

from src.domain import Opportunity, Portfolio, PortfolioOffer


def load_opportunity(path: str | Path) -> Opportunity:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Opportunity(
        description=data.get("description", ""),
        solution_type=data.get("solution_type", ""),
        customer_segment=data.get("customer_segment", ""),
        objective=data.get("objective", ""),
        initial_scope=data.get("initial_scope", ""),
        target_audience=data.get("target_audience", "pre-vendas"),
    )


def load_portfolio(path: str | Path) -> Portfolio:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    offers = [
        PortfolioOffer(
            name=item["name"],
            category=item["category"],
            capabilities=tuple(item.get("capabilities", [])),
        )
        for item in data.get("offers", [])
    ]
    return Portfolio(offers=tuple(offers))
