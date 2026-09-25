"""Distributor domain model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Distributor(BaseModel):
    """A freight shipper / distributor participant."""

    id: str
    name: str
    contracts: list[str] = Field(default_factory=list, description="Contract IDs")
