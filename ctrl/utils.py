
def u_human_to_percent(h: float) -> float:
    try:
        return float(h) * 100.0 / 65535.0
    except Exception:
        return 0.0

def u_percent_to_human(p: float) -> float:
    try:
        return round(float(p) * 65535.0 / 100.0)
    except Exception:
        return 0.0
