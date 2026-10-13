"""Deterministic LNP measurement calculations.

These functions calculate quantities from user-supplied measurements; they do
not predict delivery efficacy, toxicity, stability, or clinical outcomes.
"""
import math


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def np_ratio(ionizable_nitrogen_moles: float, phosphate_moles: float) -> float:
    """Molar nitrogen-to-phosphate ratio; amounts must use identical units."""
    nitrogen = _finite(ionizable_nitrogen_moles, "ionizable_nitrogen_moles")
    phosphate = _finite(phosphate_moles, "phosphate_moles")
    if nitrogen < 0 or phosphate <= 0:
        raise ValueError("Nitrogen must be nonnegative and phosphate must be positive")
    return nitrogen / phosphate


def encapsulation_efficiency_percent(total_mrna: float, free_mrna: float) -> float:
    """Percentage encapsulated, assuming the same measurement units and assay basis."""
    total = _finite(total_mrna, "total_mrna")
    free = _finite(free_mrna, "free_mrna")
    if total <= 0 or free < 0 or free > total:
        raise ValueError("Require total_mrna > 0 and 0 <= free_mrna <= total_mrna")
    return 100.0 * (total - free) / total


def protonated_fraction(ph: float, pka: float) -> float:
    """Ideal Henderson-Hasselbalch estimate for a monoprotic basic group."""
    ph_value = _finite(ph, "ph")
    pka_value = _finite(pka, "pka")
    delta = ph_value - pka_value
    if delta >= 50:
        return 0.0
    if delta <= -50:
        return 1.0
    return 1.0 / (1.0 + 10.0 ** delta)


def cumulants_pdi(mean_decay_rate: float, second_cumulant: float) -> float:
    """DLS cumulants PDI = mu2 / Gamma^2 (not a diameter SD-based estimate)."""
    mean = _finite(mean_decay_rate, "mean_decay_rate")
    second = _finite(second_cumulant, "second_cumulant")
    if mean <= 0 or second < 0:
        raise ValueError("Require mean_decay_rate > 0 and second_cumulant >= 0")
    return second / (mean * mean)
