import argparse
from display_timer import display_timer

# create arg parser
parser = argparse.ArgumentParser(description="Timer script")

# add optional args
parser.add_argument("-H", "--hours", type=int, default=0, help="Number of hours (default: 0)")
parser.add_argument("-M", "--minutes", type=int, default=0, help="Number of minutes (default: 0)")
parser.add_argument("-S", "--seconds", type=int, default=0, help="Number of seconds (default: 0)")
parser.add_argument("-seg", "--segment", action="store_true", help="Use 7-segment display")

# parse args
args = parser.parse_args()

# display timer
display_timer(args.hours, args.minutes, args.seconds, args.segment)
