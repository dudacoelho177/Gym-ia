from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.adapters import load_opportunity, load_portfolio
from src.services import generate_discovery_roteiro


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um roteiro de levantamento para pre-vendas.",
    )
    parser.add_argument("--opportunity-file", required=True)
    parser.add_argument("--portfolio-file", default="data/portfolio/reference_portfolio.json")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output-file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    opportunity = load_opportunity(args.opportunity_file)
    portfolio = load_portfolio(args.portfolio_file)
    roteiro = generate_discovery_roteiro(opportunity, portfolio)

    if args.format == "json":
        output = json.dumps(roteiro.to_dict(), ensure_ascii=False, indent=2)
    else:
        output = roteiro.to_markdown()

    if args.output_file:
        Path(args.output_file).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
