from pulp import *
from datetime import time

# Open Hours represented in the form of a dictionary with days as keys and a list as values. 
# The list represents open times in tuples based on shifts
openhours = {
    "Sunday": [
        # start time, open time, number of employees required
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Monday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Tueday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Wednesday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Thursday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Friday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
        (time(20), time(22), 2)
    ],
    "Saturday": []
}

# This is the list of the available hours of each employee
# Represented in a dictionary 
employee_availablity = {
    "John": {
        "Monday": (time(12), time(22))
    },
    "Jack": {
        "Tuesday": (time(16), time(18))
    },
    "JJ": {
        "Wednesday": (time(16), time(18))
    },
    "Mia": {
        # "Thursday": (time(16), time(18)),
        "Friday": (time(16), time(18)),
        "Sunday": (time(16), time(18)),
    },
    "Esteban": {
        "Friday": (time(16), time(18))
    },
    "Krish": {
        "Saturday": (time(16), time(18))
    },
    "Jul": {
        "Friday": (time(16), time(18)),
        "Sunday": (time(16), time(18))
    }
}

lp = LpProblem("wall_scheduling", LpMaximize)

variables = {}

# Add variables here

# Add constraints here

# Objective of maximum flow problem
lp += lpSum(variables.values())


# Solve 
lp.solve()

for edge in lp.variables():
    if edge.value() == 1:
        print(edge.name)