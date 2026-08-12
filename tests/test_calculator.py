"""Tests for winch calculator core logic."""

import math

import pytest

from winch_calc.calculator import (
    effective_pull,
    gradient_resistance,
    is_winch_sufficient,
    kg_to_lbs,
    kg_to_tonnes,
    lbs_to_kg,
    rolling_resistance,
    snatch_block_advantage,
    tonnes_to_kg,
    total_resistance,
)
from winch_calc.surfaces import get_coefficient, get_surface_names


class TestSurfaces:
    def test_get_all_surface_names(self):
        names = get_surface_names()
        assert len(names) > 0
        assert "tarmac" in names
        assert "deep_mud" in names

    def test_get_valid_coefficient(self):
        assert get_coefficient("tarmac") == 0.01
        assert get_coefficient("deep_mud") == 0.5

    def test_get_invalid_coefficient(self):
        with pytest.raises(ValueError, match="Unknown surface"):
            get_coefficient("lava")

    def test_coefficients_increase_with_difficulty(self):
        assert get_coefficient("tarmac") < get_coefficient("firm_grass")
        assert get_coefficient("firm_grass") < get_coefficient("wet_grass")
        assert get_coefficient("wet_grass") < get_coefficient("shallow_mud")
        assert get_coefficient("shallow_mud") < get_coefficient("deep_mud")


class TestRollingResistance:
    def test_tarmac(self):
        # 2000kg vehicle on tarmac = 20kg resistance
        assert rolling_resistance(2000, "tarmac") == pytest.approx(20.0)

    def test_deep_mud(self):
        # 2000kg vehicle in deep mud = 1000kg resistance
        assert rolling_resistance(2000, "deep_mud") == pytest.approx(1000.0)

    def test_zero_weight(self):
        assert rolling_resistance(0, "tarmac") == 0.0

    def test_heavy_vehicle_in_bog(self):
        # 3500kg Land Rover in bog = 2625kg resistance
        assert rolling_resistance(3500, "bog") == pytest.approx(2625.0)


class TestGradientResistance:
    def test_flat(self):
        assert gradient_resistance(2000, 0) == pytest.approx(0.0)

    def test_uphill_45_degrees(self):
        # sin(45°) ≈ 0.707
        expected = 2000 * math.sin(math.radians(45))
        assert gradient_resistance(2000, 45) == pytest.approx(expected)

    def test_downhill_reduces_resistance(self):
        result = gradient_resistance(2000, -10)
        assert result < 0

    def test_steep_slope(self):
        # 30° slope: sin(30°) = 0.5, so 2000 * 0.5 = 1000
        assert gradient_resistance(2000, 30) == pytest.approx(1000.0)


class TestTotalResistance:
    def test_flat_surface(self):
        # Just rolling resistance on flat ground
        result = total_resistance(2000, "deep_mud", 0)
        assert result == pytest.approx(1000.0)

    def test_uphill_adds_resistance(self):
        flat = total_resistance(2000, "deep_mud", 0)
        uphill = total_resistance(2000, "deep_mud", 10)
        assert uphill > flat

    def test_downhill_reduces_resistance(self):
        flat = total_resistance(2000, "deep_mud", 0)
        downhill = total_resistance(2000, "deep_mud", -10)
        assert downhill < flat


class TestSnatchBlocks:
    def test_no_blocks(self):
        assert snatch_block_advantage(0) == 1

    def test_one_block(self):
        assert snatch_block_advantage(1) == 2

    def test_two_blocks(self):
        assert snatch_block_advantage(2) == 4

    def test_three_blocks(self):
        assert snatch_block_advantage(3) == 8

    def test_negative_blocks_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            snatch_block_advantage(-1)


class TestEffectivePull:
    def test_no_blocks(self):
        assert effective_pull(4000, 0) == pytest.approx(4000.0)

    def test_one_block(self):
        assert effective_pull(4000, 1) == pytest.approx(8000.0)

    def test_two_blocks(self):
        assert effective_pull(4000, 2) == pytest.approx(16000.0)


class TestIsWinchSufficient:
    def test_easy_recovery(self):
        # 4000kg winch, 2000kg car on wet grass, flat
        result = is_winch_sufficient(4000, 2000, "wet_grass", 0, 0)
        assert result["is_sufficient"] is True
        assert result["total_resistance_kg"] == pytest.approx(200.0)

    def test_impossible_without_blocks(self):
        # 4000kg winch, 3500kg vehicle in bog, 15° uphill
        result = is_winch_sufficient(4000, 3500, "bog", 15, 0)
        assert result["is_sufficient"] is False

    def test_blocks_make_it_possible(self):
        # Same scenario but with 2 snatch blocks (4x advantage)
        result = is_winch_sufficient(4000, 3500, "bog", 15, 2)
        assert result["is_sufficient"] is True
        assert result["mechanical_advantage"] == 4

    def test_safety_factor_applied(self):
        result = is_winch_sufficient(4000, 2000, "deep_mud", 0, 0, safety_factor=1.5)
        # Resistance = 1000kg, with 1.5 safety = 1500kg required
        assert result["required_pull_kg"] == pytest.approx(1500.0)

    def test_margin_calculation(self):
        result = is_winch_sufficient(4000, 2000, "tarmac", 0, 0)
        # Resistance = 20kg, with 1.25 safety = 25kg required
        # Margin = 4000 - 25 = 3975
        assert result["margin_kg"] == pytest.approx(3975.0)


class TestUnitConversions:
    def test_kg_to_tonnes(self):
        assert kg_to_tonnes(2500) == pytest.approx(2.5)

    def test_kg_to_lbs(self):
        assert kg_to_lbs(1000) == pytest.approx(2204.62, rel=1e-3)

    def test_lbs_to_kg(self):
        assert lbs_to_kg(2204.62) == pytest.approx(1000.0, rel=1e-3)

    def test_tonnes_to_kg(self):
        assert tonnes_to_kg(3.5) == pytest.approx(3500.0)
