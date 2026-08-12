"""Core winching resistance and pull calculations.

Implements the IVR Group resistance formulas for calculating:
- Rolling/surface resistance
- Damage resistance (non-rolling wheels)
- Gradient (slope) resistance
- Total resistance to movement
- Effective pull with snatch blocks
- Safety factor assessment

IVR Reference:
https://www.theivrgroup.com/sites/default/files/public-documents/2023-10/Resistance%20Card.pdf

PUWER compliance:
Equipment must be suitable for the task (Reg 4). Risk assessment must
consider consequences of failure. Safety factors account for dynamic
loads, friction losses, and unseen conditions.
"""

from winch_calc.surfaces import get_coefficient


def rolling_resistance(gvw_kg: float, surface: str) -> float:
    """Calculate rolling/surface resistance in kg-force.

    IVR formula: Rolling Resistance = W × surface coefficient

    This is the force required to drag a vehicle across a given surface,
    ignoring slope and damage.

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type (see surfaces.py for IVR options).

    Returns:
        Resistance force in kg-force.
    """
    coefficient = get_coefficient(surface)
    return gvw_kg * coefficient


def damage_resistance(
    gvw_kg: float,
    damaged_wheels: int = 0,
    total_wheels: int = 4,
) -> float:
    """Calculate damage resistance in kg-force.

    IVR formula:
        Damage Resistance = W × (damaged_wheels / total_wheels)

    "Damaged" means any wheel not freely rotating:
    - Seized/locked brakes
    - Broken axle or drivetrain
    - Missing wheel (hub dragging)
    - Steering locked hard over (front wheels scrubbing)
    - Handbrake/park gear stuck

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        damaged_wheels: Number of non-rolling wheels.
        total_wheels: Total number of wheels on the vehicle.

    Returns:
        Damage resistance in kg-force.

    Raises:
        ValueError: If inputs are invalid.
    """
    if damaged_wheels < 0:
        msg = "Number of damaged wheels cannot be negative"
        raise ValueError(msg)
    if total_wheels <= 0:
        msg = "Total wheels must be positive"
        raise ValueError(msg)
    if damaged_wheels > total_wheels:
        msg = "Damaged wheels cannot exceed total wheels"
        raise ValueError(msg)
    return gvw_kg * (damaged_wheels / total_wheels)


def gradient_resistance(gvw_kg: float, slope_degrees: float) -> float:
    """Calculate gradient resistance in kg-force.

    IVR formula:
        Gradient Resistance = W ÷ 60 × slope (in degrees)

    This is a linear approximation used in the field. It is slightly
    conservative at steep angles (>30°) compared to the trigonometric
    sin() formula, which provides an additional safety margin.

    Negative slope (downhill pull) produces negative resistance,
    reducing total force required.

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        slope_degrees: Slope angle in degrees (positive = uphill).

    Returns:
        Gradient resistance in kg-force.
    """
    return (gvw_kg / 60) * slope_degrees


def total_resistance(
    gvw_kg: float,
    surface: str,
    slope_degrees: float = 0.0,
    damaged_wheels: int = 0,
    total_wheels: int = 4,
) -> float:
    """Calculate total resistance to movement in kg-force.

    IVR formula:
        WINCH POWER REQUIRED = Rolling + Damage + Gradient

    Args:
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type (see surfaces.py for IVR options).
        slope_degrees: Slope angle in degrees (positive = uphill).
        damaged_wheels: Number of non-rolling wheels.
        total_wheels: Total number of wheels on the vehicle.

    Returns:
        Total resistance force in kg-force.
    """
    rolling = rolling_resistance(gvw_kg, surface)
    damage = damage_resistance(gvw_kg, damaged_wheels, total_wheels)
    gradient = gradient_resistance(gvw_kg, slope_degrees)
    return rolling + damage + gradient


def snatch_block_advantage(num_blocks: int) -> int:
    """Calculate mechanical advantage from snatch block rigging.

    Each snatch block creates an additional part of line, doubling
    the effective pulling force (but halving the line speed).

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
    damaged_wheels: int = 0,
    total_wheels: int = 4,
) -> dict:
    """Assess whether a winch setup is sufficient for the recovery.

    Applies a safety factor (default 1.25 = 25% margin) to account for
    unseen conditions, friction losses in blocks, and dynamic loads.

    Per PUWER Regulation 4, equipment must be suitable for the task.
    This assessment supports the required risk assessment process.

    Args:
        winch_capacity_kg: Rated winch capacity in kg-force.
        gvw_kg: Gross vehicle weight in kilograms.
        surface: Surface type.
        slope_degrees: Slope angle in degrees (positive = uphill).
        num_blocks: Number of snatch blocks.
        safety_factor: Multiplier for required force (default 1.25).
        damaged_wheels: Number of non-rolling wheels.
        total_wheels: Total number of wheels on the vehicle.

    Returns:
        Dict with assessment details including resistance breakdown,
        effective pull, and sufficiency verdict.
    """
    rolling = rolling_resistance(gvw_kg, surface)
    damage = damage_resistance(gvw_kg, damaged_wheels, total_wheels)
    gradient = gradient_resistance(gvw_kg, slope_degrees)
    resistance = rolling + damage + gradient
    required_with_safety = resistance * safety_factor
    available_pull = effective_pull(winch_capacity_kg, num_blocks)

    return {
        "rolling_resistance_kg": rolling,
        "damage_resistance_kg": damage,
        "gradient_resistance_kg": gradient,
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
