"""Surface resistance coefficients for winching calculations.

Values represent the fraction of Gross Vehicle Weight (GVW) required
to move a vehicle across different surfaces. Based on IVR Group data.

Each entry is: surface_name -> (coefficient, description)
"""

# Resistance coefficients (fraction of GVW)
# These represent the rolling/drag resistance on various surfaces
SURFACES: dict[str, dict] = {
    "tarmac": {
        "coefficient": 0.01,
        "description": "Hard tarmac or concrete road",
    },
    "gravel": {
        "coefficient": 0.02,
        "description": "Compacted gravel track",
    },
    "firm_grass": {
        "coefficient": 0.05,
        "description": "Firm, dry grassland",
    },
    "wet_grass": {
        "coefficient": 0.1,
        "description": "Wet grass or soft ground",
    },
    "sand": {
        "coefficient": 0.15,
        "description": "Loose dry sand",
    },
    "wet_sand": {
        "coefficient": 0.25,
        "description": "Wet sand or shingle beach",
    },
    "shallow_mud": {
        "coefficient": 0.33,
        "description": "Shallow mud (up to axle depth)",
    },
    "deep_mud": {
        "coefficient": 0.5,
        "description": "Deep mud or clay (above axle depth)",
    },
    "bog": {
        "coefficient": 0.75,
        "description": "Marsh or bog conditions",
    },
    "submerged": {
        "coefficient": 1.0,
        "description": "Fully submerged or deeply bogged vehicle",
    },
}


def get_surface_names() -> list[str]:
    """Return all available surface type names."""
    return list(SURFACES.keys())


def get_coefficient(surface: str) -> float:
    """Get the resistance coefficient for a given surface type.

    Args:
        surface: Surface type key (e.g., 'shallow_mud')

    Returns:
        Resistance coefficient as a fraction of GVW.

    Raises:
        ValueError: If surface type is not recognised.
    """
    if surface not in SURFACES:
        available = ", ".join(SURFACES.keys())
        msg = f"Unknown surface '{surface}'. Available: {available}"
        raise ValueError(msg)
    return SURFACES[surface]["coefficient"]
