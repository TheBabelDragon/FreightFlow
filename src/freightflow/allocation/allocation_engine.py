"""Orchestrates matching, validation, and cost allocation."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from freightflow.domain.allocation import Allocation, AllocationPolicy
from freightflow.domain.contract import Contract
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.constraints.capacity_constraints import CapacityValidator
from freightflow.constraints.contract_constraints import ContractValidator
from freightflow.constraints.allocation_constraints import AllocationValidator
from freightflow.allocation.cost_allocator import CostAllocator
from freightflow.allocation.load_matcher import LoadMatcher


class AllocationEngine:
    """Propose → validate → allocate cost."""

    def __init__(self) -> None:
        self.matcher = LoadMatcher()
        self.capacity = CapacityValidator()
        self.contract = ContractValidator()
        self.alloc_validator = AllocationValidator()
        self.cost_allocator = CostAllocator()

    def propose_and_validate(
        self,
        shipments: list[Shipment],
        vehicle: Vehicle,
        contracts: dict[str, Contract] | None = None,
        total_cost: Decimal = Decimal("0"),
        policy: AllocationPolicy = AllocationPolicy.WEIGHT_PROPORTIONAL,
        route_id: str | None = None,
    ) -> tuple[bool, list[Allocation] | None, str | None]:
        """Return (ok, allocations, rejection_reason)."""
        contracts = contracts or {}

        # Shareability
        ok, reason = self.alloc_validator.validate_shareable(shipments)
        if not ok:
            return False, None, reason

        # Capacity
        ok, reason = self.capacity.validate(shipments, vehicle)
        if not ok:
            return False, None, reason

        # Contract checks per shipment
        for s in shipments:
            c = contracts.get(s.distributor_id)
            ok, reason = self.contract.validate(s, vehicle, c)
            if not ok:
                return False, None, reason

        # Cost shares
        shares = self.cost_allocator.allocate(shipments, total_cost, policy)

        allocations = []
        for s in shipments:
            alloc = Allocation(
                id=f"ALLOC-{uuid4().hex[:8].upper()}",
                shipment_id=s.id,
                vehicle_id=vehicle.id,
                route_id=route_id,
                allocated_weight=s.weight,
                allocated_volume=s.volume,
                cost_share=shares.get(s.distributor_id, Decimal("0")),
                contract_basis=contracts.get(s.distributor_id).id if contracts.get(s.distributor_id) else None,
                policy=policy,
            )
            allocations.append(alloc)

        return True, allocations, None
