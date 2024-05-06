#!/usr/bin/python3
from Config import Config
import pathlib

def validatedIntegerStr(numStr: str, minValue: int, maxValue: int) -> int:
    if not numStr.isdigit():
        raise ValueError(f"{numStr} is not a digit")
    number = int(numStr)
    if number < minValue:
        raise ValueError(f"{number} smaller than {minValue}")
    if number > maxValue:
        raise ValueError(f"{number} bigger than {maxValue}")
    return number

def deleteFolder(path: str):
    pth = pathlib.Path(path)
    if not pth.exists():
        return
    for sub in pth.iterdir():
        if sub.is_dir():
            deleteFolder(sub)
        else:
            sub.unlink()
    pth.rmdir() # if you just want to delete the dir content but not the dir itself, remove this line
    
def clearBrowserProfile(config: Config) -> None:
    profilePath = config.get(Config.BROWSER_PROFILE_DIR)
    print(f"Removing {profilePath}")
    deleteFolder(profilePath)
    print("Browser cache deleted")