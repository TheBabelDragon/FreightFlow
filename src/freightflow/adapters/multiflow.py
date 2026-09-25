"""MultiFlow adapter \u2014 translate FreightFlow domain into MultiFlow problems.

Architectural invariant:
  MultiFlow owns admissibility.
  FreightFlow owns commercial interpretation.

This adapter does NOT reimplement MultiFlow's solver. It packages domain
objects into a problem representation and interprets validation results.

When a live MultiFlow package is available, swap the internal validate path
to call MultiFlow's public API. Until then, FreightFlow's constraint suite
acts as the local admissibility gate while preserving the same interface.
"""

from __future__ import annotations

from typing import Any

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.domain.validation import ValidationReport
from freightflow.allocation.allocation_engine import AllocationEngine


class MultiFlowAdapter:
    """Translate domain objects \u2192 problem; interpret validation results."""

    def __init__(self, engine: AllocationEngine | None = None) -> None:
        self._engine = engine or AllocationEngine()

    def to_problem(
        self,
        shipments: list[Shipment],
        vehicles: list[Vehicle],
        contracts: list[Contract] | None = None,
    ) -> dict[str, Any]:
        """Build a MultiFlow-compatible problem dict."""
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

    def validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
        contracts: dict[str, Contract] | None = None,
    ) -> ValidationReport:
        """Admissibility check. Delegates to constraint suite (MultiFlow boundary).

        When MultiFlow core is wired, this method becomes a thin client call.
        """
        return self._engine.validate(shipments, vehicle, contracts)

    def from_solution(self, solution: dict[str, Any]) -> dict[str, Any]:
        """Interpret a MultiFlow validation result."""
        return {
            "admissible": solution.get("admissible", False),
            "allocations": solution.get("allocations", []),
            "rejections": solution.get("rejections", []),
            "explanations": solution.get("explanations", []),
        }
