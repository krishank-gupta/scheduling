from pulp import *
from datetime import time
from itertools import combinations

# Define open hours and employee availability
openhours = {
    #Day: start, open, employees needed
    "Monday": [(time(12), time(15), 3)],
    "Tuesday": [(time(12), time(15), 1)]
}

employee_availability = {
    "Jack": {
        # Day: start, end
        "Monday": [(time(12), time(15))]
    },
    "Jackson": {
        "Monday": [(time(12), time(15))],
        "Tuesday": [(time(12), time(15))]
    }, 
    "Jake": {
        "Monday": [(time(12), time(15))],
        "Tuesday": [(time(12), time(15))]
    },
    "Marina": {
        "Monday": [(time(12), time(15))]
    }
}

# Discourage algorithm to return results with the following pairs working together
conflicts = {
    ("Marina", "Jackson"): 5,   # higher value = more discouraged
    ("", "") : 5
}

# Encourage algorithm to return resuts with the following pairs working together
preferred_pairs = {
    ("Marina", "Jackson"): 1   # higher value = more encouraged
}

# Start a problem definition
lp = LpProblem("wall_scheduling", LpMaximize)

# variable[(employee, day, start, end)] = 1 if employee works that shift
variable = {}

for day, shifts in openhours.items():
    for start, end, _ in shifts:
        for employee, availability in employee_availability.items():
            if day in availability:
                for a_start, a_end in availability[day]:
                    if a_start <= start and a_end >= end:
                        variable[(employee, day, start, end)] = LpVariable(
                            f"{employee}_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}",
                            cat="Binary"
                        )

# 1) Enough employees on staff
for day, shifts in openhours.items():
    for start, end, required in shifts:
        lp += (
            lpSum(
                variable[(e, day, start, end)]
                for e in employee_availability
                if (e, day, start, end) in variable
            )
            == required,
            f"coverage_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}"
        )

# 2) Employee min 1 shift and max 3 shifts
for employee in employee_availability:
    employee_shifts = [
        var for (e, _, _, _), var in variable.items() if e == employee
    ]

    if employee_shifts:  # only constrain if they can work
        lp += lpSum(employee_shifts) >= 1, f"min_shifts_{employee}"
        lp += lpSum(employee_shifts) <= 3, f"max_shifts_{employee}"

# 3) No consecutive shifts for an employee
for employee in employee_availability:
    shifts = [
        (day, start, end, variable[(employee, day, start, end)])
        for (e, day, start, end) in variable
        if e == employee
    ]

    for (d1, s1, e1, v1), (d2, s2, e2, v2) in combinations(shifts, 2):
        if d1 == d2 and (e1 == s2 or e2 == s1):
            lp += v1 + v2 <= 1, f"no_consecutive_{employee}_{d1}"


# 4) Penalize staff who shouldn't be places together
penalties = []

for (e1, e2), weight in conflicts.items():
    for (employee, day, start, end) in variable:
        if employee == e1 and (e2, day, start, end) in variable:
            p = LpVariable(
                f"penalty_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                lowBound=0,
                upBound=1,
                cat="Binary"
            )

            # Activate penalty if both are scheduled
            lp += (
                p >= variable[(e1, day, start, end)] + variable[(e2, day, start, end)] - 1
            )

            penalties.append((p, weight))

# 5) Encourage algorithms to pair these pairs
bonuses = []

for (e1, e2), weight in preferred_pairs.items():
    for (employee, day, start, end) in variable:
        if employee == e1 and (e2, day, start, end) in variable:
            b = LpVariable(
                f"bonus_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                lowBound=0,
                upBound=1,
                cat="Binary"
            )

            # Bonus active only if both are assigned
            lp += (
                b <= variable[(e1, day, start, end)]
            )
            lp += (
                b <= variable[(e2, day, start, end)]
            )

            bonuses.append((b, weight))

lp += (
    lpSum(variable.values())
    + lpSum(weight * b for b, weight in bonuses)
    - lpSum(weight * p for p, weight in penalties)  # if you also have penalties
)
lp.solve(PULP_CBC_CMD(msg=False))

print(f"Status: {LpStatus[lp.status]}\n")

final_schedule_set = []

for key, var in variable.items():
    if var.varValue==1:
        final_schedule_set.append(var.name)
        
        
def who_is_working(shift):
    employees = []
    for instance in final_schedule_set:
        if shift in instance:
            employees.append(instance.split("_")[0])

    return employees


def when_are_they_working(employee):
    shifts = []
    for instance in final_schedule_set:
        if instance.split("_")[0] == employee:
            shifts.append(instance.split("_")[1:4])

    return shifts


def total_hours():
    return len(final_schedule_set)


for instance in final_schedule_set:
    print("final: ", instance)

print("when is person x working ", when_are_they_working("Jack"))
print("who is working on monday 12 - 15 ",who_is_working("Monday_1200_1500"))
print("total hours: ", total_hours())
