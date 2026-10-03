from typing import Any


claims_memory: list[dict[str, Any]] = []


def add_claim(claim: dict[str, Any]) -> None:
    claims_memory.append(claim)


def get_claims() -> list[dict[str, Any]]:
    return claims_memory


def get_claim(claim_id: str) -> dict[str, Any] | None:
    for c in claims_memory:
        if c.get('claim_id') == claim_id:
            return c
    return None
