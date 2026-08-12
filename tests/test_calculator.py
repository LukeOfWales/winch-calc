"""Tests for winch calculator core logic and unit conversions."""

import pytest

from winch_calc.calculator import (
    damage_resistance,
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
        assert "smooth_road" in names
        assert "bog_axle" in names

    def test_get_valid_coefficient(self):
        assert get_coefficient("smooth_road") == pytest.approx(1 / 25)
        assert get_coefficient("bog_axle") == pytest.approx(1.0)

    def test_get_invalid_coefficient(self):
        with pytest.raises(ValueError, match="Unknown surface"):
            get_coefficient("lava")

    def test_coefficients_increase_with_difficulty(self):
        assert get_coefficient("smooth_road") < get_coefficient("grass_min")
        assert get_coefficient("grass_min") < get_coefficient("grass_max")
        assert get_coefficient("grass_max") < get_coefficient("mud_min")
        assert get_coefficient("mud_min") < get_coefficient("bog_axle")


class TestRollingResistance:
    def test_smooth_road(self):
        # 2500kg vehicle on smooth road = 2500/25 = 100kg
        assert rolling_resistance(2500, "smooth_road") == pytest.approx(100.0)

    def test_bog_axle(self):
        # 2000kg vehicle bogged to axle = 2000×1 = 2000kg
        assert rolling_resistance(2000, "bog_axle") == pytest.approx(2000.0)

    def test_zero_weight(self):
        assert rolling_resistance(0, "smooth_road") == 0.0

    def test_heavy_vehicle_in_bog_radiator(self):
        # 3500kg in bog to radiator = 3500×3 = 10500kg
        assert rolling_resistance(3500, "bog_radiator") == pytest.approx(10500.0)


class TestDamageResistance:
    def test_no_damage(self):
        assert damage_resistance(2500, 0, 4) == pytest.approx(0.0)

    def test_one_wheel(self):
        assert damage_resistance(2500, 1, 4) == pytest.approx(625.0)

    def test_all_wheels(self):
        assert damage_resistance(2500, 4, 4) == pytest.approx(2500.0)

    def test_invalid_negative(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            damage_resistance(2500, -1, 4)

    def test_invalid_exceeds_total(self):
        with pytest.raises(ValueError, match="cannot exceed"):
            damage_resistance(2500, 5, 4)


class TestGradientResistance:
    def test_flat(self):
        assert gradient_resistance(2000, 0) == pytest.approx(0.0)

    def test_10_degree_slope(self):
        # IVR: W/60 × 10 = 2000/60 × 10 = 333.33
        assert gradient_resistance(2000, 10) == pytest.approx(2000 / 60 * 10)

    def test_downhill_reduces_resistance(self):
        result = gradient_resistance(2000, -10)
        assert result < 0

    def test_30_degree_slope(self):
        # IVR: W/60 × 30 = 2000/60 × 30 = 1000
        assert gradient_resistance(2000, 30) == pytest.approx(1000.0)


class TestTotalResistance:
    def test_flat_surface_no_damage(self):
        result = total_resistance(2500, "mud_min", 0)
        assert result == pytest.approx(2500 / 3)

    def test_uphill_adds_resistance(self):
        flat = total_resistance(2500, "mud_min", 0)
        uphill = total_resistance(2500, "mud_min", 10)
        assert uphill > flat

    def test_downhill_reduces_resistance(self):
        flat = total_resistance(2500, "mud_min", 0)
        downhill = total_resistance(2500, "mud_min", -10)
        assert downhill < flat

    def test_includes_damage(self):
        no_damage = total_resistance(2500, "mud_min", 0, damaged_wheels=0)
        with_damage = total_resistance(2500, "mud_min", 0, damaged_wheels=2)
        assert with_damage - no_damage == pytest.approx(2500 * 2 / 4)


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
        result = is_winch_sufficient(4500, 2500, "grass_min", 0, 0)
        assert result["is_sufficient"] is True

    def test_insufficient_without_blocks(self):
        result = is_winch_sufficient(4500, 3500, "bog_axle", 15, 0)
        assert result["is_sufficient"] is False

    def test_blocks_make_it_possible(self):
        result = is_winch_sufficient(4500, 3500, "bog_axle", 15, 1)
        assert result["is_sufficient"] is True
        assert result["mechanical_advantage"] == 2

    def test_safety_factor_applied(self):
        result = is_winch_sufficient(4500, 2500, "mud_min", 0, 0, safety_factor=1.5)
        expected_required = (2500 / 3) * 1.5
        assert result["required_pull_kg"] == pytest.approx(expected_required)

    def test_damage_included_in_assessment(self):
        result = is_winch_sufficient(4500, 2500, "mud_min", 0, 0, damaged_wheels=2)
        expected_damage = 2500 * 2 / 4
        assert result["damage_resistance_kg"] == pytest.approx(expected_damage)


class TestUnitConversions:
    def test_kg_to_tonnes(self):
        assert kg_to_tonnes(2500) == pytest.approx(2.5)

    def test_kg_to_lbs(self):
        assert kg_to_lbs(1000) == pytest.approx(2204.62, rel=1e-3)

    def test_lbs_to_kg(self):
        assert lbs_to_kg(2204.62) == pytest.approx(1000.0, rel=1e-3)

    def test_tonnes_to_kg(self):
        assert tonnes_to_kg(3.5) == pytest.approx(3500.0)
