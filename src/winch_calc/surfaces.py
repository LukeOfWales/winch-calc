"""Surface resistance coefficients for winching calculations.

Values taken directly from the IVR Group Resistance Card:
https://www.theivrgroup.com/sites/default/files/public-documents/2023-10/Resistance%20Card.pdf

Resistance is expressed as a coefficient of Gross Vehicle Weight (GVW).
IVR expresses these as W÷n or W×n — stored here as the resulting multiplier.

Some surfaces have MIN and MAX values representing the range of conditions
(e.g., dry vs waterlogged grass). Use MIN for best-case and MAX for worst-case
assessment. When in doubt, use MAX — PUWER requires equipment to be suitable.
"""

# Resistance coefficients (multiplier of GVW)
# IVR format: W÷25 → 1/25, W×2 → 2.0
SURFACES: dict[str, dict] = {
    # --- Hard surfaces ---
    "smooth_road": {
        "coefficient": 1 / 25,  # W ÷ 25
        "description": "Smooth tarmac or concrete road",
        "ivr_formula": "W ÷ 25",
    },
    # --- Grass (range: firm/dry to soft/wet) ---
    "grass_min": {
        "coefficient": 1 / 7,  # W ÷ 7
        "description": "Grass — firm/dry (minimum resistance)",
        "ivr_formula": "W ÷ 7",
    },
    "grass_max": {
        "coefficient": 1 / 4,  # W ÷ 4
        "description": "Grass — soft/wet (maximum resistance)",
        "ivr_formula": "W ÷ 4",
    },
    # --- Gravel (range: compacted to loose) ---
    "gravel_min": {
        "coefficient": 1 / 7,  # W ÷ 7
        "description": "Gravel — compacted (minimum resistance)",
        "ivr_formula": "W ÷ 7",
    },
    "gravel_max": {
        "coefficient": 1 / 5,  # W ÷ 5
        "description": "Gravel — loose (maximum resistance)",
        "ivr_formula": "W ÷ 5",
    },
    # --- Beach ---
    "beach_shingle": {
        "coefficient": 1 / 3,  # W ÷ 3
        "description": "Beach shingle",
        "ivr_formula": "W ÷ 3",
    },
    # --- Sand (range: firm to soft/deep) ---
    "sand_min": {
        "coefficient": 1 / 6,  # W ÷ 6
        "description": "Sand — firm/damp (minimum resistance)",
        "ivr_formula": "W ÷ 6",
    },
    "sand_max": {
        "coefficient": 1 / 2,  # W ÷ 2
        "description": "Sand — soft/deep/dry (maximum resistance)",
        "ivr_formula": "W ÷ 2",
    },
    # --- Mud (range: shallow to deep) ---
    "mud_min": {
        "coefficient": 1 / 3,  # W ÷ 3
        "description": "Mud — shallow (minimum resistance)",
        "ivr_formula": "W ÷ 3",
    },
    "mud_max": {
        "coefficient": 1 / 2,  # W ÷ 2
        "description": "Mud — deep (maximum resistance)",
        "ivr_formula": "W ÷ 2",
    },
    # --- Clay ---
    "soft_clay": {
        "coefficient": 1 / 2,  # W ÷ 2
        "description": "Soft clay",
        "ivr_formula": "W ÷ 2",
    },
    # --- Bog (by depth) ---
    "bog_axle": {
        "coefficient": 1.0,  # W × 1
        "description": "Bog — submerged to axle depth",
        "ivr_formula": "W × 1",
    },
    "bog_wheel_top": {
        "coefficient": 2.0,  # W × 2
        "description": "Bog — submerged to top of wheels",
        "ivr_formula": "W × 2",
    },
    "bog_radiator": {
        "coefficient": 3.0,  # W × 3
        "description": "Bog — submerged to radiator top",
        "ivr_formula": "W × 3",
    },
}


def get_surface_names() -> list[str]:
    """Return all available surface type names."""
    return list(SURFACES.keys())


def get_coefficient(surface: str) -> float:
    """Get the resistance coefficient for a given surface type.

    Args:
        surface: Surface type key (e.g., 'mud_min', 'bog_axle')

    Returns:
        Resistance coefficient as a multiplier of GVW.

    Raises:
        ValueError: If surface type is not recognised.
    """
    if surface not in SURFACES:
        available = ", ".join(SURFACES.keys())
        msg = f"Unknown surface '{surface}'. Available: {available}"
        raise ValueError(msg)
    return SURFACES[surface]["coefficient"]
