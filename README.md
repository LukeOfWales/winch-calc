# 🪝 Winch Calculator

Vehicle recovery resistance & pulling power calculator based on the [IVR Group Resistance Card](https://www.theivrgroup.com/sites/default/files/public-documents/2023-10/Resistance%20Card.pdf).

Helps you determine whether your winching equipment is appropriate for a recovery and how much pull strength is required.

## Live Calculator

👉 **[Use the web calculator](https://lukeofwales.github.io/winch-calc/)** (GitHub Pages)

## What it calculates

- **Rolling resistance** — force to drag a vehicle across a given surface (GVW × surface coefficient)
- **Gradient resistance** — additional force for slope (GVW × sin(angle))
- **Total resistance** — combined force required
- **Effective pull** — winch capacity multiplied by snatch block mechanical advantage
- **Safety assessment** — whether your setup has sufficient margin

## Surface Coefficients

| Surface | Coefficient | Example |
|---------|------------|---------|
| Tarmac | 0.01 | Hard road |
| Gravel | 0.02 | Compacted track |
| Firm grass | 0.05 | Dry field |
| Wet grass | 0.10 | Soft ground |
| Sand | 0.15 | Loose dry sand |
| Wet sand | 0.25 | Beach/shingle |
| Shallow mud | 0.33 | Up to axle depth |
| Deep mud | 0.50 | Above axle depth |
| Bog | 0.75 | Marsh conditions |
| Submerged | 1.00 | Fully bogged/submerged |

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
uv sync --extra dev
```

### Run tests

```bash
uv run pytest
```

### Lint & format

```bash
uv run ruff check .
uv run ruff format .
```

### Use as a library

```python
from winch_calc.calculator import is_winch_sufficient

result = is_winch_sufficient(
    winch_capacity_kg=4500,
    gvw_kg=3500,
    surface="shallow_mud",
    slope_degrees=10,
    num_blocks=1,
    safety_factor=1.25,
)

print(f"Sufficient: {result['is_sufficient']}")
print(f"Required pull: {result['required_pull_kg']:.0f} kg")
print(f"Available pull: {result['effective_pull_kg']:.0f} kg")
print(f"Margin: {result['margin_percent']:.0f}%")
```

## GitHub Pages Deployment

The web calculator lives in `/docs/index.html`. To deploy:

1. Push to GitHub
2. Go to **Settings → Pages**
3. Set source to "Deploy from a branch"
4. Set branch to `main` and folder to `/docs`
5. Save — the site will be live in a few minutes

## Safety Disclaimer

These calculations provide **estimates only**. Real-world conditions vary significantly. Always:

- Assess the scene before committing to a recovery
- Use rated equipment within its Safe Working Load (SWL)
- Apply appropriate safety factors for dynamic loads
- Keep bystanders clear of the winch line
- Use a winch line damper

## References

- [IVR Group Resistance Card (PDF)](https://www.theivrgroup.com/sites/default/files/public-documents/2023-10/Resistance%20Card.pdf)
- [IVR Group - International Vehicle Recovery](https://www.theivrgroup.com/)
