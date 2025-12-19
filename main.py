# Necessary Dependencies
from pulp import *
from datetime import time
from itertools import combinations

# Open Hours represented in the form of a dictionary with days as keys and a list as values. 
# The list represents open times in tuples based on shifts

openhours = {
    "Monday": [
        (time(12), time(15), 2)
    ],
    "Tuesday": [
        (time(12), time(15), 1)
    ]
}

# --- Sample Employee Availability ---
employee_availablity = {
    "Alice": {
        "Monday": [(time(12), time(15))],
    },
    "John": {
        "Monday": [(time(12), time(15))],
        "Tuesday": [(time(12), time(15))]
    }
}

# openhours = {
#     "Sunday": [
#         # start time, open time, number of employees required
#         (time(12), time(14), 2),
#         (time(14), time(16), 2),
#         (time(16), time(18), 3),
#         (time(18), time(20), 3),
#         (time(20), time(22), 2)
#     ],
#     "Monday": [
#         (time(14), time(16), 2),
#         (time(16), time(18), 3),
#         (time(18), time(20), 3),
#         (time(20), time(22), 2)
#     ],
#     "Tueday": [
#         (time(16), time(18), 3),
#         (time(18), time(20), 2),
#         (time(20), time(22), 2)
#     ],
#     "Wednesday": [
#         (time(12), time(14), 2),
#         (time(14), time(16), 2),
#         (time(16), time(18), 3),
#         (time(18), time(20), 2)
#     ],
#     "Thursday": [
#         (time(12), time(14), 2),
#         (time(14), time(16), 2),
#         (time(16), time(18), 3),
#         (time(18), time(20), 3)
#     ],
#     "Friday": [
#         (time(12), time(14), 2),
#         (time(14), time(16), 2),
#         (time(16), time(18), 3),
#         (time(18), time(20), 3),
#         (time(20), time(22), 3)
#     ],
#     "Saturday": []
# }

# # This is the list of the available hours of each employee
# # Represented in a dictionary 
# employee_availablity = {
#     "John": {
#         "Sunday": [(time(12), time(16)), (time(18), time(20))],
#         "Monday": [(time(12), time(14)), (time(18), time(20))],
#         "Tuesday": [(time(12), time(16)), (time(18), time(20))],
#         "Wednesday": [(time(12), time(16))]
#     },
#     "Jack": {
#         "Thursday": [(time(12), time(16)), (time(18), time(20))],
#         "Wednesday": [(time(12), time(14)), (time(18), time(20))],
#         "Friday": [(time(12), time(16)), (time(18), time(20))],
#         "Saturday": [(time(12), time(16))]
#     },
#     "Krish": {
#         "Sunday": [(time(12), time(22))],
#         "Monday": [(time(14), time(18))],
#         "Tuesday": [(time(12), time(16)), (time(18), time(20))],
#         "Wednesday": [(time(12), time(16))]
#     },
#     "Julia": {
#         "Monday": [(time(12), time(14)), (time(14), time(16)), (time(16), time(18)), (time(18), time(20))],
#         "Tuesday": [(time(12), time(22))],
#         "Friday": [(time(16), time(18)), (time(20), time(22))],
#         "Wednesday": [(time(12), time(16))]
#     },
#     "tues": {
#         "Tuesday": [(time(12), time(14)), (time(14), time(16)), (time(16), time(18)), (time(18), time(20))]
#     }
# }

lp = LpProblem("wall_scheduling", LpMaximize)
variables = {}

# Add variables here
for day in openhours:
    if day:
        for shifts in openhours[day]:
            start = shifts[0].strftime('%H%M')
            end = shifts[1].strftime('%H%M')
            employees_needed = shifts[2]

            variables[(f"{day}_{start}_{end}_sink")] = LpVariable(
                f"{day}_{start}_{end}_sink", lowBound=int(employees_needed), upBound=int(employees_needed)
            )

for employee in employee_availablity:
    if employee:
        for days in employee_availablity[employee]:
            shifts = employee_availablity[employee][days]
            for shift in shifts:
                start = shift[0].strftime('%H%M')
                end = shift[1].strftime('%H%M')
                variables[f"source_{employee}_{days}_{start}_{end}"] = LpVariable(
                    f"source_{employee}_{days}_{start}_{end}", lowBound=1, upBound=3
                )

for day, shifts in openhours.items():
    for shift in shifts:
        shift_start, shift_end, employees_needed = shift
        
        # Loop over each employee
        for employee, availability in employee_availablity.items():
            # Check if employee is available on this day
            if day in availability:
                for avail in availability[day]:
                    avail_start, avail_end = avail
                    # Check if the shift is fully within employee availability
                    if avail_start <= shift_start and avail_end >= shift_end:
                        # Variable name: "employee_day_start_end"
                        var_name = f"{employee}_{day}_{shift_start.strftime('%H%M')}_{shift_end.strftime('%H%M')}"
                        variables[var_name] = LpVariable(var_name, lowBound=0, upBound=1)

print("all vars created")

# Add constraints here

# Collect shift assignment variables by (day, start, end)
shift_assignments = {}
employee_assignments = {}

for name, var in variables.items():
    parts = name.split("_")
    if len(parts) == 4 and parts[0] not in ["source"] and not name.endswith("_sink"):
        employee, day, start, end = parts
        shift_assignments.setdefault((day, start, end), []).append(var)
        employee_assignments.setdefault(employee, []).append((day, start, end, var))


for (day, start, end), vars_for_shift in shift_assignments.items():
    sink_var = variables[f"{day}_{start}_{end}_sink"]
    lp += lpSum(vars_for_shift) == sink_var, f"coverage_{day}_{start}_{end}"


for employee, shifts in employee_assignments.items():
    lp += lpSum(var for _, _, _, var in shifts) >= 1, f"min_shifts_{employee}"
    lp += lpSum(var for _, _, _, var in shifts) <= 3, f"max_shifts_{employee}"


for employee in employee_assignments:
    source_vars = [
        var for name, var in variables.items()
        if name.startswith(f"source_{employee}_")
    ]
    assigned_vars = [
        var for _, _, _, var in employee_assignments[employee]
    ]
    lp += lpSum(assigned_vars) == lpSum(source_vars), f"flow_{employee}"


for employee, shifts in employee_assignments.items():
    for (day1, s1, e1, var1), (day2, s2, e2, var2) in combinations(shifts, 2):
        if day1 == day2:
            # consecutive forward
            if e1 == s2 or e2 == s1:
                lp += var1 + var2 <= 1, f"no_consecutive_{employee}_{day1}_{s1}_{s2}"



# Objective of maximum flow problem
lp += lpSum(
    var for name, var in variables.items()
    if len(name.split("_")) == 4 and not name.endswith("_sink")
)
# Solve 
lp.solve()

for name, var in variables.items():
    print(f"{name} = {var.varValue}")

# Helper Functions
def employee_can_work(employee, open_shift):
    # returns if given employee can work given shift
    return None

def who_is_working(open_shift):
    # return all employees working on the given shift
    return None

def when_are_they_working(employee):
    # return all shifts where given employee is working
    return None
