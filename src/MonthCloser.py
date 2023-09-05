#!/usr/bin/python3
import os, shutil
import asyncio

from AccountTask import AccountTask
from Config import Config
from AccountsPageNavigatior import AccountsPageNavigatior
from Template import substitude

class MonthCloser:

    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.downloadDir = config.get(Config.WORK_DIR) + '/dwnl-tmp'
        os.makedirs(self.downloadDir, exist_ok=True, mode=700)
        
    async def prepareTransferReport(self, taskInfo : AccountTask):
        while True:
            resolutionValueStr = input("Enter amount to transfer (by resolution): ")
            if resolutionValueStr.isnumeric():
                resolutionValue = int(resolutionValueStr)
                break
            else:
                print("Invalid input")
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR),
                                   self.downloadDir)
        await self._loginAndNavMonth(taskInfo, targetNav);
        await targetNav.navCloseMonthStart()
        await targetNav.setResultionInput(resolutionValue)
        print("Creating TO-62 form")
        await targetNav.downloadReportTO62()
        to62targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_TO62), taskInfo)
        print(f"TO-62 saved to {to62targetFile}")

    async def run(self, taskInfo : AccountTask):
        print("Finishing monthly report for account "+taskInfo.getAccountName())
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR),
                           self.downloadDir)
        await self._loginAndNavMonth(taskInfo, targetNav)
        await targetNav.downloadReportS30()
        s30targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_S30), taskInfo)
        print(f"S-30 saved to {s30targetFile}")
        
        await targetNav.navMonth(taskInfo.getMonth())
        await targetNav.downloadReportS26()
        s26targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_S26), taskInfo)
        print(f"S-26 saved to {s26targetFile}")
        print("Monthly reports downloaded. Please handle remaining tasks manually")

    async def _loginAndNavMonth(self, taskInfo: AccountTask, targetNav: AccountsPageNavigatior):
        userName = self.config.get(Config.WEBSITE_USERNAME, False)
        if userName is not None:
            targetNav.setCredentials(userName, None)
        await targetNav.navigateToHub()
        await targetNav.navAccounting()
        await targetNav.navAccount(taskInfo.getAccountName())
        await targetNav.navMonth(taskInfo.getMonth())

    async def _savePrintResult(self, targetFilePath: str, taskInfo : AccountTask) -> str:
        printedFile = f'{self.downloadDir}/printed.pdf'
        ttl = 20
        while ttl > 0:
            await asyncio.sleep(0.5)
            if os.path.isfile(printedFile):
                break
            ttl -= 1
        if ttl == 0:
            print(f'File not found! ({printedFile})')
            return None

        targetDir = os.path.dirname(targetFilePath)
        fileName = os.path.basename(targetFilePath)
        os.makedirs(targetDir, exist_ok=True, mode=0o700)

        fileName = substitude(fileName, taskInfo)
        targetFilePath = f'{targetDir}/{fileName}'
        targetFilePath = self._prepareFilename(targetFilePath)

        shutil.move(printedFile, targetFilePath)
        if os.path.isfile(printedFile):
            raise Exception("File rename did not worked out "+printedFile)
        return targetFilePath

    def _prepareFilename(self, targetFilePath: str) -> str:
        ''' Adds incremented number to filename if file exits '''
        if not os.path.isfile(targetFilePath):
            return targetFilePath
        extStart = targetFilePath.rindex(".")
        targetPattern = f'{targetFilePath[:extStart]}_%s{targetFilePath[extStart:]}'
        i = 1
        while os.path.exists(targetPattern % i):
            i += 1
        return targetPattern % i
    