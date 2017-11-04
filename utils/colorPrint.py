"""
Print messages in color
"""

def color_print(print_str, type="NONE"):
    # handle null cases
    if (print_str is None):
        print_str = ""

    if (type is "ERROR"):
        # red
        print('\033[38;5;196m' + print_str + '\033[0m')

    elif (type is "WARN"):
        # orange
        print('\033[38;5;202m' + print_str + '\033[0m')

    elif (type is "SUCCESS"):
        # green
        print('\033[38;5;22m' + print_str + '\033[0m')

    elif (type is "INFO"):
        # blue
        print('\033[38;5;33m' + print_str + '\033[0m')

    else:
        # black
        print('\033[38;5;33m' + print_str + '\033[0m')
