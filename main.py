# Necessary Dependencies
from pulp import *
from datetime import time

# Open Hours represented in the form of a dictionary with days as keys and a list as values. 
# The list represents open times in tuples based on shifts
openhours = {
    "Sunday": [
        # start time, open time, number of employees required
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 3),
        (time(18), time(20), 3),
        (time(20), time(22), 2)
    ],
    "Monday": [
        (time(14), time(16), 2),
        (time(16), time(18), 3),
        (time(18), time(20), 3),
        (time(20), time(22), 2)
    ],
    "Tueday": [
        (time(16), time(18), 3),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Wednesday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 3),
        (time(18), time(20), 2)
    ],
    "Thursday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 3),
        (time(18), time(20), 3)
    ],
    "Friday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 3),
        (time(18), time(20), 3),
        (time(20), time(22), 3)
    ],
    "Saturday": []
}

# This is the list of the available hours of each employee
# Represented in a dictionary 
employee_availablity = {
    "John": {
        "Sunday": [(time(12), time(16)), (time(18), time(20))],
        "Monday": [(time(12), time(14)), (time(18), time(20))],
        "Tuesday": [(time(12), time(16)), (time(18), time(20))],
        "Wednesday": [(time(12), time(16))]
    },
    "Jack": {
        "Thursday": [(time(12), time(16)), (time(18), time(20))],
        "Wednesday": [(time(12), time(14)), (time(18), time(20))],
        "Friday": [(time(12), time(16)), (time(18), time(20))],
        "Saturday": [(time(12), time(16))]
    },
    "Krish": {
        "Sunday": [(time(12), time(22))],
        "Monday": [(time(14), time(18))],
        "Tuesday": [(time(12), time(16)), (time(18), time(20))],
        "Wednesday": [(time(12), time(16))]
    },
    "Julia": {
        "Monday": [(time(12), time(22))],
        "Tuesday": [(time(12), time(22))],
        "Friday": [(time(16), time(18)), (time(20), time(22))],
        "Wednesday": [(time(12), time(16))]
    }
}

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
                variables[f"source_{employee}_{day}_{start}_{end}"] = LpVariable(
                    f"source_{employee}_{day}_{start}_{end}", lowBound=0
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
for employee in employee_availablity.keys():
    employee_vars = [var for name, var in variables.items() if name.startswith(employee)]
    if employee_vars:
        lp += lpSum(employee_vars) >= 1, f"{employee}_min_shifts"
        lp += lpSum(employee_vars) <= 3, f"{employee}_max_shifts"

# 3b: Each open shift must have the required number of employees
for day, shifts in openhours.items():
    for shift in shifts:
        shift_start, shift_end, employees_needed = shift
        # All employee variables that flow into this shift
        incoming_vars = [
            var for name, var in variables.items()
            if name.endswith(f"{shift_start.strftime('%H%M')}_{shift_end.strftime('%H%M')}")
            and not name.startswith(day)  # skip sink variable itself
        ]
        sink_var = variables[f"{day}_{shift_start.strftime('%H%M')}_{shift_end.strftime('%H%M')}_sink"]
        # inflow to shift = required employees
        lp += lpSum(incoming_vars) == sink_var, f"{day}_{shift_start.strftime('%H%M')}_{shift_end.strftime('%H%M')}_required"


# Objective of maximum flow problem
# create_variables()
# create_constraints()

lp += lpSum([var for name, var in variables.items() if not name.endswith("_sink")]), "Maximize_assigned_shifts"

# Solve 
lp.solve()

for name, var in variables.items():
    print(f"{name} = {var.varValue}")