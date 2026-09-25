"""Domain models for FreightFlow."""

from .distributor import Distributor
from .shipment import Shipment
from .vehicle import Vehicle
from .contract import Contract
from .allocation import Allocation
from .settlement import Settlement
from .route import Route

__all__ = [
    "Distributor",
    "Shipment",
    "Vehicle",
    "Contract",
    "Allocation",
    "Settlement",
    "Route",
]
