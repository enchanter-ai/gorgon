"""
G5 — Gauss Accumulation: Hotspot-Drift Signature

Reference:
    Gauss C.F. (1809), "Theoria motus corporum coelestium in sectionibus
    conicis solem ambientium" (least-squares foundation for recursive
    EMA-with-posterior updates).

Ecosystem precedent:
    Wixie F6, Emu A7, Crow H6, Djinn D5.

Role:
    Per-(repo x hotspot-kind) drift posterior. Tracks how the top-N hotspot set
    evolves across snapshots — a stable hotspot earns a tighter advisory band;
    a thrashing hotspot earns wider tolerance.

Stdlib only. EMA mean + EMA variance with sample-count tracked alongside the
posterior. Atomic JSONL append is delegated to `state_io.append_jsonl`.
"""
from __future__ import annotations

import math


def update_posterior(prior: dict, observation: dict, alpha: float = 0.3) -> dict:
    """Fold a single snapshot observation into the per-(repo x hotspot-kind) posterior.

    `prior` shape (any subset; first call may be {}):
        {
            "median_score": float,
            "sigma": float,
            "n_snapshots": int,
            "top_n_stability": float,  # Jaccard similarity to previous snapshot
            "last_seen": str,          # ISO timestamp
        }
    `observation` shape:
        {
            "hotspot_score": float,
            "top_n_stability": float,
            "captured_at": str,
        }

    Returns a new posterior dict. EMA half-life ~ 30 snapshots at alpha = 0.3
    (tunable). Sample variance maintained via Welford-like recurrence on the
    EMA (approximate but stable enough for advisory bands).
    """
    if not isinstance(observation, dict):
        return dict(prior or {})

    score = float(observation.get("hotspot_score", 0.0))
    stab = float(observation.get("top_n_stability", 0.0))
    seen = str(observation.get("captured_at", ""))

    n_prior = int(prior.get("n_snapshots", 0)) if prior else 0
    if n_prior == 0:
        return {
            "median_score": score,
            "sigma": 0.0,
            "n_snapshots": 1,
            "top_n_stability": stab,
            "last_seen": seen,
        }

    prev_med = float(prior.get("median_score", score))
    prev_sigma = float(prior.get("sigma", 0.0))
    prev_stab = float(prior.get("top_n_stability", stab))

    new_med = (1 - alpha) * prev_med + alpha * score
    delta = score - prev_med
    # EMA-of-squared-deviation as a tractable variance estimator.
    new_var = (1 - alpha) * (prev_sigma ** 2) + alpha * (delta * delta)
    new_sigma = math.sqrt(max(0.0, new_var))
    new_stab = (1 - alpha) * prev_stab + alpha * stab

    return {
        "median_score": new_med,
        "sigma": new_sigma,
        "n_snapshots": n_prior + 1,
        "top_n_stability": new_stab,
        "last_seen": seen,
    }
