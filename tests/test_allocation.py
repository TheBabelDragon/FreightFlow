"""Cost allocation determinism tests."""

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.allocation import AllocationPolicy
from freightflow.allocation.cost_allocator import CostAllocator


def _shipments():
    return [
        Shipment(id="S1", distributor_id="A", origin="X", destination="Y", weight=Decimal("8"), volume=Decimal("8")),
        Shipment(id="S2", distributor_id="B", origin="X", destination="Y", weight=Decimal("5"), volume=Decimal("5")),
        Shipment(id="S3", distributor_id="C", origin="X", destination="Y", weight=Decimal("7"), volume=Decimal("7")),
    ]


def test_weight_proportional():
    shares = CostAllocator().allocate(_shipments(), Decimal("1200"), AllocationPolicy.WEIGHT)
    assert shares["A"] == Decimal("480.00")
    assert shares["B"] == Decimal("300.00")
    assert shares["C"] == Decimal("420.00")
    assert sum(shares.values()) == Decimal("1200.00")


def test_volume_proportional():
    shares = CostAllocator().allocate(_shipments(), Decimal("1200"), AllocationPolicy.VOLUME)
    assert shares["A"] == Decimal("480.00")
    assert shares["B"] == Decimal("300.00")
    assert shares["C"] == Decimal("420.00")


def test_determinism():
    alloc = CostAllocator()
    s = _shipments()
    a = alloc.allocate(s, Decimal("1200"), AllocationPolicy.WEIGHT)
    b = alloc.allocate(s, Decimal("1200"), AllocationPolicy.WEIGHT)
    assert a == b
