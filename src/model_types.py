"""Shared model data structures for inflationary MVP models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ForwardResult:
    """Output of a slow-roll forward map."""

    As: float
    ns: float
    r: float
    N: float
    phi_end: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "As": self.As,
            "ns": self.ns,
            "r": self.r,
            "N": self.N,
            "phi_end": self.phi_end,
        }
