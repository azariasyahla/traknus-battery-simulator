from datetime import datetime, timedelta
import pandas as pd


def _clock_to_minute(value):
    try:
        parsed = datetime.strptime(str(value).strip(), "%H:%M")
        return parsed.hour * 60 + parsed.minute
    except ValueError as exc:
        raise ValueError(f"Invalid time '{value}'. Use HH:MM, for example 07:00.") from exc


def simulate(config, shifts, breaks, catalog):
    """Simulate two-state battery use in workbook-matched 5-minute increments."""
    spec = config["spec"]
    capacity = float(config["battery"]["ah"])
    reserve = float(config["battery"].get("reserve_pct", 0.05))
    usable_capacity = capacity * (1 - reserve)
    step = int(catalog["time_step_min"])
    draw_ah_h = (
        float(spec["en_ah_per_hour"])
        * float(spec["power_modes"].get(config["mode"], 1.0))
        * float(catalog["intensity_factors"][config["intensity"]])
        * float(catalog["lift_factors"][config["lift"]])
    )
    charger_a = float(config["charger"] or 0)
    charge_ah_h = min(capacity, charger_a) * float(catalog["charge_efficiency"])

    shift_windows = []
    previous_start = None
    for _, row in shifts.iterrows():
        start = _clock_to_minute(row["Start"])
        if previous_start is not None:
            while start < previous_start:
                start += 1440
        duration = float(row["Length (h)"]) * 60
        if duration <= 0:
            raise ValueError("Shift lengths must be greater than zero.")
        shift_windows.append((start, start + duration))
        previous_start = start
    if not shift_windows:
        raise ValueError("At least one shift is required.")

    first_start = shift_windows[0][0]
    last_end = max(end for _, end in shift_windows)
    breaks_norm = []
    for _, row in breaks.iterrows():
        try:
            start = _clock_to_minute(row.get("Start", ""))
        except ValueError:
            continue
        while start < first_start:
            start += 1440
        length = int(float(row.get("Length (min)", 0) or 0))
        if length > 0:
            breaks_norm.append((start, start + length, bool(row.get("Charge", False))))

    timeline = list(range(first_start, int(last_end), step))
    if not timeline or timeline[0] != first_start:
        timeline.insert(0, first_start)
    if timeline[-1] < last_end:
        timeline.append(int(last_end))

    soc_ah = usable_capacity
    points = []
    for index, minute in enumerate(timeline):
        if index:
            previous_minute = timeline[index - 1]
            elapsed_hours = (minute - previous_minute) / 60
            working = any(start <= previous_minute < end for start, end in shift_windows)
            break_charge = None
            for start, end, can_charge in breaks_norm:
                if start <= previous_minute < end:
                    break_charge = can_charge
                    break
            if working and break_charge is None:
                soc_ah -= draw_ah_h * elapsed_hours
            elif working and break_charge is True and charge_ah_h > 0:
                soc_ah += charge_ah_h * elapsed_hours
            soc_ah = max(0.0, min(usable_capacity, soc_ah))
        clock = (datetime.combine(datetime.today().date(), datetime.min.time()) + timedelta(minutes=minute)).strftime("%H:%M")
        points.append({
            "Elapsed hour": (minute - first_start) / 60,
            "Absolute minute": minute,
            "Clock time": clock,
            "State of charge (%)": soc_ah / usable_capacity * 100 if usable_capacity else 0,
        })

    data = pd.DataFrame(points)
    return {
        "data": data,
        "runtime": usable_capacity / draw_ah_h if draw_ah_h else 0,
        "time_to_soft_limit": next((float(row["Elapsed hour"]) for row in points if row["State of charge (%)"] <= float(catalog.get("soft_safety_pct", .10)) * 100), None),
        "draw": draw_ah_h,
        "charge_rate": charge_ah_h,
        "usable": usable_capacity,
        "min_soc": float(data["State of charge (%)"].min()),
        "end_soc": float(data["State of charge (%)"].iloc[-1]),
        "depleted": bool(data["State of charge (%)"].min() <= 0.01),
    }
