"""MultiFlow adapter — translate FreightFlow domain into MultiFlow problems.

Critical rule: never fork MultiFlow core. FreightFlow only supplies the problem
and interprets validated results commercially.
"""

from __future__ import annotations

from typing import Any

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract


class MultiFlowAdapter:
    """Translate domain objects → MultiFlow problem representation."""

    def to_problem(
        self,
        shipments: list[Shipment],
        vehicles: list[Vehicle],
        contracts: list[Contract] | None = None,
    ) -> dict[str, Any]:
        """Build a MultiFlow-compatible problem dict (stub for v0.1)."""
        return {
            "type": "shared_freight_allocation",
            "shipments": [s.model_dump(mode="json") for s in shipments],
            "vehicles": [v.model_dump(mode="json") for v in vehicles],
            "contracts": [c.model_dump(mode="json") for c in (contracts or [])],
            "constraints": [
                "capacity_weight",
                "capacity_volume",
                "contract_carrier",
                "delivery_windows",
                "shareability",
            ],
        }

    def from_solution(self, solution: dict[str, Any]) -> dict[str, Any]:
        """Interpret a MultiFlow validation result (stub)."""
        return {
            "admissible": solution.get("admissible", False),
            "allocations": solution.get("allocations", []),
            "rejections": solution.get("rejections", []),
            "explanations": solution.get("explanations", []),
        }
