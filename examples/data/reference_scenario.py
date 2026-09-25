"""Reference scenario fixtures for the Esri demonstrator.

Inspectable inputs \u2014 a reviewer can verify:
  8 + 5 + 7 = 20 pallets
  40% + 25% + 35% = 100%
  $480 + $300 + $420 = $1,200

All data is fixture/demo data. Network route is labeled source='fixture'.
"""

from __future__ import annotations

from decimal import Decimal

from freightflow.domain.distributor import Distributor
from freightflow.domain.shipment import Shipment
from freightflow.domain.vehicle import Vehicle
from freightflow.domain.contract import Contract
from freightflow.domain.network import NetworkRoute


DISTRIBUTORS = [
    Distributor(id="D-ACME", name="ACME Distribution"),
    Distributor(id="D-BABEL", name="Babel Supply"),
    Distributor(id="D-DESERT", name="Desert Wholesale"),
]

SHIPMENTS = [
    Shipment(
        id="S-ACME-001",
        distributor_id="D-ACME",
        origin="Dallas",
        destination="Phoenix",
        weight=Decimal("800"),
        volume=Decimal("8"),
        shareable=True,
    ),
    Shipment(
        id="S-BABEL-004",
        distributor_id="D-BABEL",
        origin="Dallas",
        destination="Phoenix",
        weight=Decimal("500"),
        volume=Decimal("5"),
        shareable=True,
    ),
    Shipment(
        id="S-DESERT-007",
        distributor_id="D-DESERT",
        origin="Dallas",
        destination="Phoenix",
        weight=Decimal("700"),
        volume=Decimal("7"),
        shareable=True,
    ),
]

VEHICLE = Vehicle(
    id="Truck-17",
    carrier_id="TruckCo-17",
    max_weight=Decimal("10000"),
    max_volume=Decimal("20"),
    origin="Dallas",
)

CONTRACTS: dict[str, Contract] = {
    "D-ACME": Contract(
        id="C-ACME-01",
        distributor_id="D-ACME",
        carrier_id="TruckCo-17",
        exclusive_carrier=False,
    ),
    "D-BABEL": Contract(
        id="C-BABEL-01",
        distributor_id="D-BABEL",
        carrier_id="TruckCo-17",
        exclusive_carrier=False,
    ),
    "D-DESERT": Contract(
        id="C-DESERT-01",
        distributor_id="D-DESERT",
        carrier_id="TruckCo-17",
        exclusive_carrier=False,
    ),
}

BABEL_EXCLUSIVE_CONTRACT = Contract(
    id="B-119",
    distributor_id="D-BABEL",
    carrier_id="C-22",
    exclusive_carrier=True,
    permitted_carriers=["C-22"],
)

NETWORK_ROUTE = NetworkRoute(
    id="RTE-DAL-PHX",
    origin="Dallas",
    destination="Phoenix",
    distance=Decimal("887"),
    travel_time_hours=Decimal("13.5"),
    geometry=None,
    network_metadata={
        "corridor": "I-20 / I-10",
        "note": "Deterministic fixture for demo \u2014 not a live ArcGIS response",
    },
    source="fixture",
)

TOTAL_TRANSPORT_COST = Decimal("1200.00")
CURRENCY = "USD"

DISTRIBUTOR_NAMES = {d.id: d.name for d in DISTRIBUTORS}
