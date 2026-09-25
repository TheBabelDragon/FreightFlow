"""Orchestrates matching, validation, and cost allocation.

MultiFlow owns admissibility conceptually; this engine runs the FreightFlow
constraint suite and produces commercially interpreted allocations only when
all validators pass. Rejected candidates never produce settlements.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from freightflow.domain.allocation import Allocation, AllocationPolicy
from freightflow.domain.contract import Contract
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.validation import ValidationReport, ValidationResult
from freightflow.constraints.capacity_constraints import CapacityValidator
from freightflow.constraints.contract_constraints import ContractValidator
from freightflow.constraints.allocation_constraints import AllocationValidator
from freightflow.constraints.delivery_constraints import DeliveryWindowValidator
from freightflow.allocation.cost_allocator import CostAllocator
from freightflow.allocation.load_matcher import LoadMatcher


class AllocationEngine:
    """Propose \u2192 validate (structured) \u2192 allocate cost."""

    def __init__(self) -> None:
        self.matcher = LoadMatcher()
        self.capacity = CapacityValidator()
        self.contract = ContractValidator()
        self.alloc_validator = AllocationValidator()
        self.delivery = DeliveryWindowValidator()
        self.cost_allocator = CostAllocator()

    def validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
        contracts: dict[str, Contract] | None = None,
    ) -> ValidationReport:
        """Run all constraint validators; aggregate failures."""
        contracts = contracts or {}
        report = ValidationReport()

        report = report.add(self.alloc_validator.validate_shareable(shipments))
        report = report.add(self.capacity.validate(shipments, vehicle))

        for s in shipments:
            c = contracts.get(s.distributor_id)
            report = report.add(self.contract.validate(s, vehicle, c))
            report = report.add(self.delivery.validate(s, vehicle))

        return report

    def propose_and_validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
        contracts: dict[str, Contract] | None = None,
        total_cost: Decimal = Decimal("0"),
        policy: AllocationPolicy = AllocationPolicy.WEIGHT,
        route_id: str | None = None,
    ) -> tuple[bool, list[Allocation] | None, ValidationReport]:
        """Return (ok, allocations, report).

        On failure, allocations is None and no commercial interpretation occurs.
        """
        if isinstance(total_cost, float):
            raise TypeError("total_cost must be Decimal")

        report = self.validate(shipments, vehicle, contracts)
        if not report.valid:
            return False, None, report

        shares = self.cost_allocator.allocate(shipments, total_cost, policy)
        contracts = contracts or {}

        if policy == AllocationPolicy.VOLUME:
            total_qty = sum((s.volume for s in shipments), Decimal("0"))
        else:
            total_qty = sum((s.weight for s in shipments), Decimal("0"))

        allocations: list[Allocation] = []
        for s in shipments:
            num, den = self.cost_allocator.share_fraction(s, shipments, policy)
            c = contracts.get(s.distributor_id)
            alloc = Allocation(
                id=f"ALLOC-{uuid4().hex[:8].upper()}",
                shipment_id=s.id,
                vehicle_id=vehicle.id,
                route_id=route_id,
                allocated_weight=s.weight,
                allocated_volume=s.volume,
                cost_share=shares.get(s.distributor_id, Decimal("0")),
                contract_basis=c.id if c else None,
                policy=policy,
                share_numerator=num,
                share_denominator=den if den else total_qty,
            )
            allocations.append(alloc)

        return True, allocations, report
