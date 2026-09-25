"""Contract constraint tests."""

from decimal import Decimal

from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.constraints.contract_constraints import ContractValidator


def test_exclusive_carrier_rejects():
    s = Shipment(id="S1", distributor_id="B", origin="D", destination="P", weight=Decimal("5"), volume=Decimal("5"))
    v = Vehicle(id="T17", carrier_id="TruckCo-17", max_weight=Decimal("1000"), max_volume=Decimal("20"))
    c = Contract(id="B-119", distributor_id="B", carrier_id="C-22", exclusive_carrier=True)
    ok, reason = ContractValidator().validate(s, v, c)
    assert ok is False
    assert "CONTRACT-CARRIER-EXCLUSIVITY" in reason


def test_matching_carrier_ok():
    s = Shipment(id="S1", distributor_id="B", origin="D", destination="P", weight=Decimal("5"), volume=Decimal("5"))
    v = Vehicle(id="T17", carrier_id="C-22", max_weight=Decimal("1000"), max_volume=Decimal("20"))
    c = Contract(id="B-119", distributor_id="B", carrier_id="C-22", exclusive_carrier=True)
    ok, reason = ContractValidator().validate(s, v, c)
    assert ok is True
