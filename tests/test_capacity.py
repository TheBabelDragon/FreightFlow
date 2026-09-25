"""Capacity constraint tests."""

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.constraints.capacity_constraints import CapacityValidator


def test_capacity_ok():
    v = Vehicle(id="V1", carrier_id="C1", max_weight=Decimal("1000"), max_volume=Decimal("20"))
    s = [
        Shipment(id="S1", distributor_id="D1", origin="A", destination="B", weight=Decimal("400"), volume=Decimal("8")),
        Shipment(id="S2", distributor_id="D2", origin="A", destination="B", weight=Decimal("500"), volume=Decimal("10")),
    ]
    ok, reason = CapacityValidator().validate(s, v)
    assert ok is True
    assert reason is None


def test_capacity_over_weight():
    v = Vehicle(id="V1", carrier_id="C1", max_weight=Decimal("100"), max_volume=Decimal("20"))
    s = [
        Shipment(id="S1", distributor_id="D1", origin="A", destination="B", weight=Decimal("80"), volume=Decimal("5")),
        Shipment(id="S2", distributor_id="D2", origin="A", destination="B", weight=Decimal("30"), volume=Decimal("5")),
    ]
    ok, reason = CapacityValidator().validate(s, v)
    assert ok is False
    assert "CAPACITY-WEIGHT" in reason


def test_capacity_over_volume():
    v = Vehicle(id="V1", carrier_id="C1", max_weight=Decimal("10000"), max_volume=Decimal("10"))
    s = [
        Shipment(id="S1", distributor_id="D1", origin="A", destination="B", weight=Decimal("10"), volume=Decimal("6")),
        Shipment(id="S2", distributor_id="D2", origin="A", destination="B", weight=Decimal("10"), volume=Decimal("6")),
    ]
    ok, reason = CapacityValidator().validate(s, v)
    assert ok is False
    assert "CAPACITY-VOLUME" in reason
