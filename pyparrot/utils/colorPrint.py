"""Print messages in color"""


def color_print(print_str, type="NONE"):
    # Null cases
    if not print_str:
        print_str = ""

    colours = {
        "ERROR": "38;5;196m",
        "WARN": "38;5;202m",
        "SUCCESS": "38;5;22m",
        "INFO": "38;5;33m",
    }
    colour = colours.get(type, "0m")
    print(f"\033[{colour} {print_str} \033[0m")
