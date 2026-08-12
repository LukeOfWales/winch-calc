"""Core winching resistance and pull calculations.

Implements the IVR Group resistance formulas for calculating:
- Rolling/surface resistance
- Gradient (slope) resistance
- Total resistance to movement
- Effective pull with snatch blocks
- Safety factor assessment
"""

import math

from winch_calc.surfaces import get_coefficient


def rolling_resistance(gvw_kg: float, surface: str) -> float:
    """Calculate rolling/surface resistance in kg-force.

    This is the force required to drag a vehicle across a given surface,
    ignoring any slope.

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type (see surfaces.py for options).

    Returns:
        Resistance force in kg-force.
    """
    coefficient = get_coefficient(surface)
    return gvw_kg * coefficient


def gradient_resistance(gvw_kg: float, slope_degrees: float) -> float:
    """Calculate gradient resistance in kg-force.

    This is the additional force required to pull a vehicle up a slope.
    Negative slope (downhill) reduces resistance.

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        slope_degrees: Slope angle in degrees (positive = uphill).

    Returns:
        Gradient resistance in kg-force.
    """
    return gvw_kg * math.sin(math.radians(slope_degrees))


def total_resistance(
    gvw_kg: float,
    surface: str,
    slope_degrees: float = 0.0,
) -> float:
    """Calculate total resistance to movement in kg-force.

    Combines rolling resistance and gradient resistance.

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type (see surfaces.py for options).
        slope_degrees: Slope angle in degrees (positive = uphill).

    Returns:
        Total resistance force in kg-force.
    """
    rolling = rolling_resistance(gvw_kg, surface)
    gradient = gradient_resistance(gvw_kg, slope_degrees)
    return rolling + gradient


def snatch_block_advantage(num_blocks: int) -> int:
    """Calculate mechanical advantage from snatch block rigging.

    Each snatch block doubles the effective pulling force (but halves
    the line speed).

    Args:
        num_blocks: Number of snatch blocks in the rigging.

    Returns:
        Mechanical advantage multiplier.

    Raises:
        ValueError: If num_blocks is negative.
    """
    if num_blocks < 0:
        msg = "Number of snatch blocks cannot be negative"
        raise ValueError(msg)
    return 2**num_blocks


def effective_pull(winch_capacity_kg: float, num_blocks: int = 0) -> float:
    """Calculate effective pulling force with snatch blocks.

    Args:
        winch_capacity_kg: Rated winch capacity in kg-force.
        num_blocks: Number of snatch blocks used.

    Returns:
        Effective pulling force in kg-force.
    """
    return winch_capacity_kg * snatch_block_advantage(num_blocks)


def is_winch_sufficient(
    winch_capacity_kg: float,
    gvw_kg: float,
    surface: str,
    slope_degrees: float = 0.0,
    num_blocks: int = 0,
    safety_factor: float = 1.25,
) -> dict:
    """Assess whether a winch setup is sufficient for the recovery.

    Applies a safety factor (default 1.25 = 25% margin) to account for
    unseen conditions, friction losses in blocks, and dynamic loads.

    Args:
        winch_capacity_kg: Rated winch capacity in kg-force.
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type.
        slope_degrees: Slope angle in degrees (positive = uphill).
        num_blocks: Number of snatch blocks.
        safety_factor: Multiplier for required force (default 1.25).

    Returns:
        Dict with assessment details.
    """
    resistance = total_resistance(gvw_kg, surface, slope_degrees)
    required_with_safety = resistance * safety_factor
    available_pull = effective_pull(winch_capacity_kg, num_blocks)

    return {
        "rolling_resistance_kg": rolling_resistance(gvw_kg, surface),
        "gradient_resistance_kg": gradient_resistance(gvw_kg, slope_degrees),
        "total_resistance_kg": resistance,
        "safety_factor": safety_factor,
        "required_pull_kg": required_with_safety,
        "winch_capacity_kg": winch_capacity_kg,
        "num_blocks": num_blocks,
        "mechanical_advantage": snatch_block_advantage(num_blocks),
        "effective_pull_kg": available_pull,
        "is_sufficient": available_pull >= required_with_safety,
        "margin_kg": available_pull - required_with_safety,
        "margin_percent": (
            ((available_pull - required_with_safety) / required_with_safety) * 100
            if required_with_safety > 0
            else 0.0
        ),
    }


def kg_to_tonnes(kg: float) -> float:
    """Convert kilograms to metric tonnes."""
    return kg / 1000.0


def kg_to_lbs(kg: float) -> float:
    """Convert kg-force to pounds-force."""
    return kg * 2.20462


def lbs_to_kg(lbs: float) -> float:
    """Convert pounds-force to kg-force."""
    return lbs / 2.20462


def tonnes_to_kg(tonnes: float) -> float:
    """Convert metric tonnes to kilograms."""
    return tonnes * 1000.0
