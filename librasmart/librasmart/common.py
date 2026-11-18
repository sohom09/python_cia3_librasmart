"""Shared constants for CHRIST LibraSmart (used by generate_data.py and app.py)."""

# (floor, zone, number of seats)
ZONES = [
    ("Ground Floor", "Reading Hall", 100),
    ("Ground Floor", "Digital Library", 50),
    ("First Floor", "Silent Zone", 70),
    ("First Floor", "Group Study", 40),
    ("Second Floor", "Computer Lab", 60),
]
ZONE_NAMES = [z[1] for z in ZONES]
ZONE_FLOOR = {z[1]: z[0] for z in ZONES}
ZONE_SEATS = {z[1]: z[2] for z in ZONES}
TOTAL_SEATS = sum(ZONE_SEATS.values())

# How busy each zone usually is compared with the library average
ZONE_BIAS = {
    "Reading Hall": 1.10,
    "Digital Library": 0.80,
    "Silent Zone": 1.15,
    "Group Study": 0.90,
    "Computer Lab": 1.00,
}

# Department -> share of visitors
DEPARTMENTS = {
    "MCA": 0.20,
    "BTech CSE": 0.22,
    "MBA": 0.14,
    "BCA": 0.10,
    "BBA": 0.09,
    "BCom": 0.09,
    "BA English": 0.05,
    "MSc": 0.11,
}
DEPT_CODE = {
    "MCA": "MCA", "BTech CSE": "BTC", "MBA": "MBA", "BCA": "BCA",
    "BBA": "BBA", "BCom": "BCM", "BA English": "BAE", "MSc": "MSC",
}
TECH_DEPTS = {"MCA", "BTech CSE", "BCA", "MSc"}

# Relative arrival rate by opening hour (library is open 8 AM - 8 PM)
HOUR_PROFILE = {
    8: 0.35, 9: 0.55, 10: 0.75, 11: 0.95, 12: 0.85, 13: 0.70,
    14: 0.90, 15: 1.00, 16: 0.95, 17: 0.70, 18: 0.40, 19: 0.20,
}
OPEN_HOURS = list(range(8, 20))
SUNDAY_HOURS = list(range(10, 16))
DAY_FACTOR = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.6, 6: 0.25}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

LOAN_DAYS = 14
FINE_PER_DAY = 2  # rupees


def hour_label(h: int) -> str:
    """8 -> '8 AM', 15 -> '3 PM'."""
    return f"{(h - 1) % 12 + 1} {'AM' if h < 12 else 'PM'}"
