"""CLI local. Recebe JSON tipado; não envia documentos a serviços externos."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from .calculations import calculate_bdi, calculate_sla, screen_engineering_price
from .models import BDIRequest, PriceRequest, SLARequest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("price", "bdi", "sla"))
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 8_000_000:
            raise ValueError("Entrada excede limite local de 8 MB.")
        data = args.input.read_text(encoding="utf-8")
        if args.operation == "price":
            response = screen_engineering_price(PriceRequest.model_validate_json(data))
        elif args.operation == "bdi":
            response = calculate_bdi(BDIRequest.model_validate_json(data))
        else:
            response = calculate_sla(SLARequest.model_validate_json(data))
        print(response.model_dump_json(indent=2))
        return 0
    except ValidationError as exc:
        # Somente localizações/tipos; não expor os valores da entrada em logs.
        for error in exc.errors(include_input=False, include_context=False, include_url=False):
            print(f"Entrada inválida: {error['loc']} ({error['type']})", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Não foi possível executar: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
