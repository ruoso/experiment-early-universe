"""Model registry and adapters for the scanning/priors pipeline."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from . import mvp_model, plateau_model
from .model_types import ForwardResult

ForwardFn = Callable[[float, float, float], ForwardResult]
ValidFn = Callable[..., bool]
EFoldsFn = Callable[[float, float, float], float]
PotentialFn = Callable[[float, float, float], float]
ParamFromEnergyFn = Callable[[float, float, float], float]


@dataclass(frozen=True)
class ModelConfig:
    name: str
    param_name: str
    param_scale: str
    forward: ForwardFn
    valid: ValidFn
    e_folds: EFoldsFn
    default_phi_range: Tuple[float, float]
    default_param_range: Tuple[float, float]
    potential: Optional[PotentialFn]
    param_from_energy: Optional[ParamFromEnergyFn]


_DEF_PHI_RANGE = (6.0, 22.0)
_DEF_M_RANGE = (5e-7, 5e-5)
_DEF_V0_RANGE = (1e-11, 1e-8)


def quadratic_model() -> ModelConfig:
    return ModelConfig(
        name="quadratic",
        param_name="m",
        param_scale="log",
        forward=mvp_model.forward,
        valid=mvp_model.valid,
        e_folds=lambda phi_star, m, mpl=1.0: mvp_model.e_folds(phi_star, mpl),
        default_phi_range=_DEF_PHI_RANGE,
        default_param_range=_DEF_M_RANGE,
        potential=lambda phi_star, m, mpl=1.0: 0.5 * m ** 2 * phi_star ** 2,
        param_from_energy=lambda phi_star, V_star, mpl=1.0: math.sqrt(2.0 * V_star) / phi_star,
    )


def plateau_model_config() -> ModelConfig:
    return ModelConfig(
        name="plateau",
        param_name="V0",
        param_scale="log",
        forward=plateau_model.forward,
        valid=plateau_model.valid,
        e_folds=lambda phi_star, V0, mpl=1.0: plateau_model.e_folds(phi_star, V0, mpl),
        default_phi_range=(4.5, 8.5),
        default_param_range=_DEF_V0_RANGE,
        potential=lambda phi_star, V0, mpl=1.0: plateau_model.potential(phi_star, V0=V0, mpl=mpl),
        param_from_energy=lambda phi_star, V_star, mpl=1.0: V_star
        / plateau_model.potential(phi_star, V0=1.0, mpl=mpl),
    )


MODEL_CONFIGS = {
    "quadratic": quadratic_model(),
    "plateau": plateau_model_config(),
}


def get_model(name: str) -> ModelConfig:
    try:
        return MODEL_CONFIGS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown model '{name}'") from exc
