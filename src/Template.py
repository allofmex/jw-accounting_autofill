#!/usr/bin/python3
import locale
import markdown
from AccountTask import AccountTask
from os import path

def substitude(text: str, taskInfo: AccountTask) -> str:
    locale.setlocale(locale.LC_TIME,'de_DE.UTF-8')
    text = text.replace("%%MONTH%%", taskInfo.getMonth().strftime("%m"))
    text = text.replace("%%MONTH_STR%%", taskInfo.getMonth().strftime("%B"))
    text = text.replace("%%YEAR%%", taskInfo.getMonth().strftime("%Y"))
    return text

def loadTemplate(filePath: str) -> str:
    if not path.isfile(filePath):
        raise Exception(f"Template file {filePath} not existing!")
    f = open(filePath, "r")
    text = f.read()
    fromMarkdown = markdown.markdown(text).replace('\r', '').replace('\n', '')
    return fromMarkdown