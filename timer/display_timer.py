import os
import time
from seven_seg_digits import get_digits

def calculate_strings(total_seconds):
    curr_hr = total_seconds // 3600
    curr_min = (total_seconds % 3600) // 60
    curr_sec = total_seconds % 60

    hr_str = str(curr_hr).zfill(2)
    min_str = str(curr_min).zfill(2)
    sec_str = str(curr_sec).zfill(2)
    return (hr_str, min_str, sec_str)



def display_digits(digit1, digit2, digit3, digit4, digit5, digit6):
    for i in range(len(digit1)):
        col = '   '
        if (i == 2 or i == 4):
            col = ' o '
        line = ' ' + digit1[i] + ' ' + digit2[i] + col + digit3[i] + ' ' + digit4[i] + col + digit5[i] + ' ' + digit6[i]
        print(line)


def display_regular_timer(hours, minutes, seconds):
    total_seconds = hours * 3600 + minutes * 60 + seconds

    while total_seconds >= 0:
        (hours_str, minutes_str, seconds_str) = calculate_strings(total_seconds)

        timer_str = f'{hours_str}:{minutes_str}:{seconds_str}'
        print(timer_str)

        time.sleep(1)
        total_seconds -= 1
        os.system('cls' if os.name == 'nt' else 'clear')

def display_7segment_timer(hours, minutes, seconds):
    digits = get_digits()
    total_seconds = hours * 3600 + minutes * 60 + seconds

    while total_seconds >= 0:
        (hours_str, minutes_str, seconds_str) = calculate_strings(total_seconds)

        display_digits(digits[int(hours_str[0])], digits[int(hours_str[1])],
                       digits[int(minutes_str[0])], digits[int(minutes_str[1])], 
                       digits[int(seconds_str[0])], digits[int(seconds_str[1])])

        time.sleep(1)
        total_seconds -= 1
        os.system('cls' if os.name == 'nt' else 'clear') # clear terminal
        

def display_timer(hours, minutes, seconds, use_7segment_display=False):
    if use_7segment_display:
        display_7segment_timer(hours, minutes, seconds)
    else:
        display_regular_timer(hours, minutes, seconds)
