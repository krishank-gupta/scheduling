import csv
from datetime import time

def parse_time(t):
    hour, minute = map(int, t.strip().split(":"))
    return time(hour, minute)

def parse_ranges(cell):
    if not cell or cell.strip().lower() == "none":
        return []

    ranges = []
    for part in cell.split(","):
        start, end = part.strip().split(" - ")
        ranges.append((parse_time(start), parse_time(end)))
    return ranges

def csv_to_availability(csv_path):
    employee_availability = {}

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # ✅ FIX: strip whitespace before checking brackets
        day_columns = {}
        for col in reader.fieldnames:
            clean = col.strip()
            if clean.startswith("[") and clean.endswith("]"):
                day_columns[col] = clean.strip("[]")

        for row in reader:
            name = row["Name"].strip()
            employee_availability[name] = {}

            for original_col, day in day_columns.items():
                ranges = parse_ranges(row[original_col])
                if ranges:
                    employee_availability[name][day] = ranges

    return employee_availability


availability = csv_to_availability("responses.csv")
print(availability)