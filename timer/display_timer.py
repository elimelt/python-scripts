import os
import time
# Seven segment representations for digits 0-9
digits = [
    [' ### ',
     '#   #',
     '#   #',
     '#   #',
     '#   #',
     '#   #',
     ' ### '],

    ['   # ',
     '  ## ',
     '#  # ',
     '   # ',
     '   # ',
     '   # ',
     '#####'],

    [' ### ',
     '#   #',
     '    #',
     '  ## ',
     ' #   ',
     '#    ',
     '#####'],

    [' ### ',
     '#   #',
     '    #',
     ' ### ',
     '    #',
     '#   #',
     ' ### '],

    ['#   #',
     '#   #',
     '#   #',
     '#####',
     '    #',
     '    #',
     '    #'],

    ['#####',
     '#    ',
     '#    ',
     '#####',
     '    #',
     '    #',
     '#####'],
    
    [' ### ',
     '#   #',
     '#    ',
     '#####',
     '#   #',
     '#   #',
     ' ### '],
    
    ['#####',
     '   # ',
     '  #  ',
     ' #   ',
     '#    ',
     '#    ',
     '#    '],
    
    [' ### ',
     '#   #',
     '#   #',
     ' ### ',
     '#   #',
     '#   #',
     ' ### '],
    
    [' ### ',
     '#   #',
     '#   #',
     ' ####',
     '    #',
     '#   #',
     ' ### ']
]

def display_digits(digit1, digit2, digit3, digit4, digit5, digit6):
    for i in range(len(digit1)):
        col = '   '
        if (i == 2 or i == 4):
            col = ' o '
        line = ' ' + digit1[i] + ' ' + digit2[i] + col + digit3[i] + ' ' + digit4[i] + col + digit5[i] + ' ' + digit6[i]
        print(line)

def display_timer(hours, minutes, seconds):
    total_seconds = hours * 3600 + minutes * 60 + seconds

    while total_seconds >= 0:
        # Calculate hours, minutes, and remaining seconds
        current_hours = total_seconds // 3600
        current_minutes = (total_seconds % 3600) // 60
        current_seconds = total_seconds % 60

        # Convert hours, minutes, and seconds to two-digit strings
        hours_str = str(current_hours).zfill(2)
        minutes_str = str(current_minutes).zfill(2)
        seconds_str = str(current_seconds).zfill(2)
        
        # Display the timer
        display_digits(digits[int(hours_str[0])], digits[int(hours_str[1])],
                       digits[int(minutes_str[0])], digits[int(minutes_str[1])], 
                       digits[int(seconds_str[0])], digits[int(seconds_str[1])])

        time.sleep(1)
        total_seconds -= 1
        os.system('cls')
