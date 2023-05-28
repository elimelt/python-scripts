import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from display_timer import display_timer

# Read command-line arguments
if len(sys.argv) != 7 or sys.argv[1] != '-h' or sys.argv[3] != '-m' or sys.argv[5] != '-s':
    print("Usage: python timer.py -h [hours] -m [minutes] -s [seconds]")
    sys.exit(1)

try:
    hours = int(sys.argv[2])
    minutes = int(sys.argv[4])
    seconds = int(sys.argv[6])
except ValueError:
    print("Error: Invalid argument. Hours, minutes, and seconds must be integers.")
    sys.exit(1)

# Display the timer
display_timer(hours, minutes, seconds)
