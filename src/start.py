#!/usr/bin/python3
import os, asyncio, readchar, sys
from typing import List
import getopt
from datetime import datetime

from AccountingTool import AccountingTool
from MonthCloser import MonthCloser
from TransactionTaskInfo import TransactionTaskInfo
from AccountTask import AccountTask
from Config import Config

SCRIPT_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(SCRIPT_PATH)
config = month = accountName = sourceFile = None
simulationOnly = False;

def helpMsg():
    print("Accounting helper tool")
    print()
    print("Usage:")
    print("<run.sh> [--source=mt940.csv | --month=2023-05 | --help]")
    print("m|month         Date string YYYY.MM")
    print("a|account       Bank account name as used on jw org")
    print("s|source        Source file to import (e.g. mt940.csv)")
    # print("y|yes          Unattended mode, confirm most questions with yes. Useful for testing, Do not use for final run!")
    # print("v|verbose      Print additional data like found form field names in input file")
    # print("t|test         Stop after first report. May be used for initial setup/result test")
    print()
    print("Use MT940 csv format for bank account export")
    print()


async def printMainMenu():
    print("1: Upload transactions")
    print("5: Finalize month and download reports")
    print("9: Exit")
    selected = _requestUserSelection("Please select number", [1,5,9], int.__class__)
    if selected == 1:
        print("Starting upload")
        await _runTransactionUpload()
    elif selected == 5:
        print("Starting finalizing")
        await _runFinalizingOfMonth()
    elif selected == 9:
        sys.exit()

def _requestUserSelection(msg, allowedKeys: List, typeClass):
    print(msg)
    while True:
        selected = readchar.readkey()
        if typeClass is int.__class__:
            selected = int(selected)
        if selected in allowedKeys:
            return selected
        else:
            print("Invalid key")

async def _runTransactionUpload():
    if month is None or accountName is None or sourceFile is None:
        raise Exception("You must provide --month, --account and --source option")
    # datetime.date(2023, 6, 1)
    task = TransactionTaskInfo(accountName, month, sourceFile)
    tool = AccountingTool(config)
    if simulationOnly is True:
        tool.setSimulation()
    await tool.run(task)

async def _runFinalizingOfMonth():
    if month is None or accountName is None:
        raise Exception("You must provide --month and --account option")
    task = AccountTask(accountName, month)
    tool = MonthCloser(config)
    await tool.run(task)



try:
    argumentList = sys.argv[1:]
    options, remainder = getopt.getopt(argumentList, "ams:h", ["account=", "month=", "source=", "simulate", "help"])
    for opt, arg in options:
        if opt in ('-m', '--month'):
            try:
                month = datetime.strptime(arg, "%Y-%m")
            except ValueError:
                raise Exception("Invalid date format, use YYYY-MM")
            print("Selected month: "+datetime.strftime(month, "%B %Y"))
        if opt in ('a', '--account'):
            accountName = arg
        if opt in ('s', '--source'):
            sourceFile = arg
        if opt in ('--simulate'):
            print("Simulated run only!")
            simulationOnly = True
        if opt in ('-h', '--help'):
            helpMsg()
            sys.exit()
except getopt.GetoptError as e:
    print(e)
    helpMsg()
    sys.exit(2)

if config is None:
    defaultConfigFile = f"{BASE_PATH}/config.yml"
    if not os.path.isfile(defaultConfigFile):
        raise Exception("No default config file found! Create config.yml or provide config file argument")
    config = Config(defaultConfigFile, BASE_PATH)



async def main():
    print("Starting AccountingTool")
    await printMainMenu()
    print("Done")
    
if __name__ == "__main__":
    asyncio.run(main())