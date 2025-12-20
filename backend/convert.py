import csv
from datetime import time

# Columns in the CSV that contain availability
DAY_COLUMNS = {
    "Availability: [Sunday]": "Sunday",
    "Availability: [Monday]": "Monday",
    "Availability: [Tuesday]": "Tuesday",
    "Availability: [Wednesday]": "Wednesday",
    "Availability: [Thursday]": "Thursday",
    "Availability: [Friday]": "Friday",
    "Availability: [Saturday]": "Saturday",
}

def parse_time_range(time_range: str):
    """
    Converts a time range like '12:00 - 2:00' (PM assumed)
    into (start_time, end_time) as datetime.time objects.
    """

    def parse_time(t: str) -> time:
        hour, minute = map(int, t.strip().split(":"))

        # Convert to 24-hour time (PM assumed)
        if hour != 12:
            hour += 12

        return time(hour=hour, minute=minute)

    start_str, end_str = time_range.split("-")

    start_time = parse_time(start_str)
    end_time = parse_time(end_str)

    return start_time, end_time


def parse_availability(cell):
    """
    Converts '12:00 - 2:00, 4:00 - 6:00'
    -> [(time(12), time(14)), (time(16), time(18))]
    """
    if not cell or not cell.strip():
        return []

    ranges = cell.split(",")
    return [parse_time_range(r.strip()) for r in ranges]


employee_availability = {}

with open("responses.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = row["Name"].strip()
        employee_availability[name] = {}

        for csv_col, day in DAY_COLUMNS.items():
            availability = parse_availability(row.get(csv_col, ""))
            if availability:
                employee_availability[name][day] = availability


# Example output
print(employee_availability)
# for employee, schedule in employee_availability.items():
#     print(employee)
#     for day, slots in schedule.items():
#         print(f"  {day}: {slots}")
