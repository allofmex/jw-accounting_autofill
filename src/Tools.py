#!/usr/bin/python3

def validatedIntegerStr(numStr: str, minValue: int, maxValue: int) -> int:
    if not numStr.isdigit():
        raise ValueError(f"{numStr} is not a digit")
    number = int(numStr)
    if number < minValue:
        raise ValueError(f"{number} smaller than {minValue}")
    if number > maxValue:
        raise ValueError(f"{number} bigger than {maxValue}")
    return number