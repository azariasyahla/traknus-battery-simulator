import unittest
import pandas as pd
from engine import simulate

CATALOG = {
    "time_step_min": 5,
    "charge_efficiency": 1.0,
    "intensity_factors": {"Medium": 0.8, "Very High": 1.0},
    "lift_factors": {"All": 0.8},
}
CONFIG = {
    "spec": {"en_ah_per_hour": 10.0, "power_modes": {"Standard": 1.0}},
    "battery": {"ah": 100, "reserve_pct": 0.05},
    "charger": 5,
    "mode": "Standard",
    "intensity": "Medium",
    "lift": "All",
}

class EngineTests(unittest.TestCase):
    def test_break_charging_changes_soc_but_rest_break_does_not_draw(self):
        shifts = pd.DataFrame([{"Start": "07:00", "Length (h)": 2.0}])
        with_charge = pd.DataFrame([{"Start": "08:00", "Length (min)": 30, "Charge": True}])
        without_charge = pd.DataFrame([{"Start": "08:00", "Length (min)": 30, "Charge": False}])
        charged = simulate(CONFIG, shifts, with_charge, CATALOG)
        idle = simulate(CONFIG, shifts, without_charge, CATALOG)
        expected_idle = (100 * .95 - 6.4 * 1.5) / 95 * 100
        self.assertGreater(charged["end_soc"], idle["end_soc"])
        self.assertAlmostEqual(idle["end_soc"], expected_idle, delta=.2)

    def test_intensity_increases_draw_and_lowers_end_soc(self):
        shifts = pd.DataFrame([{"Start": "07:00", "Length (h)": 2.0}])
        breaks = pd.DataFrame(columns=["Start", "Length (min)", "Charge"])
        lower = simulate(CONFIG, shifts, breaks, CATALOG)
        higher_config = {**CONFIG, "intensity": "Very High"}
        higher = simulate(higher_config, shifts, breaks, CATALOG)
        self.assertGreater(higher["draw"], lower["draw"])
        self.assertLess(higher["end_soc"], lower["end_soc"])

    def test_second_shift_rolls_past_midnight(self):
        shifts = pd.DataFrame([
            {"Start": "22:00", "Length (h)": 4.0},
            {"Start": "02:00", "Length (h)": 4.0},
        ])
        breaks = pd.DataFrame(columns=["Start", "Length (min)", "Charge"])
        out = simulate(CONFIG, shifts, breaks, CATALOG)
        self.assertAlmostEqual(out["data"]["Elapsed hour"].iloc[-1], 8.0)

if __name__ == "__main__":
    unittest.main()
