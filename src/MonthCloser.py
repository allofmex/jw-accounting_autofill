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
        targetNav = self._createNavigator()
        await targetNav.loginAndNavMonth(taskInfo.getAccountName(), taskInfo.getMonth());
        await targetNav.navCloseMonthStart()
        nonCongregationDonations = await targetNav.readTransferAmountFromDonationBox()
        print(f"Other donations that will be transferred additionally to resolution amount (worldwide work and projects): {nonCongregationDonations}")
        while True:
            resolutionValueStr = input("Enter amount to transfer (by resolution): ")
            if resolutionValueStr.isnumeric():
                resolutionValue = int(resolutionValueStr)
                break
            else:
                print("Invalid input")
        await targetNav.setResultionInput(resolutionValue)
        print("Creating TO-62 form")
        await targetNav.downloadReportTO62()
        to62targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_TO62), taskInfo)
        print(f"TO-62 saved to {to62targetFile}")

    async def run(self, taskInfo : AccountTask):
        print("Finishing monthly report for account "+taskInfo.getAccountName())
        targetNav = self._createNavigator()
        await targetNav.loginAndNavMonth(taskInfo.getAccountName(), taskInfo.getMonth())
        await targetNav.downloadReportS30()
        s30targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_S30), taskInfo)
        print(f"S-30 saved to {s30targetFile}")
        
        await targetNav.navMonth(taskInfo.getMonth())
        await targetNav.downloadReportS26()
        s26targetFile = await self._savePrintResult(self.config.get(Config.FILEPATH_S26), taskInfo)
        print(f"S-26 saved to {s26targetFile}")
        print("Monthly reports downloaded. Please handle remaining tasks manually")

    def _createNavigator(self):
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR), self.downloadDir)
        userName = self.config.get(Config.WEBSITE_USERNAME, False)
        if userName is not None:
            targetNav.setCredentials(userName, None)
        else:
            print("You may consider setting your username in config file to speedup login.")
        return targetNav

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
            raise Exception(f'Print to pdf failed, no file found at expected location {printedFile}')
            return None

        targetDir = os.path.dirname(targetFilePath)
        fileName = os.path.basename(targetFilePath)
        os.makedirs(targetDir, exist_ok=True, mode=0o700)

        fileName = substitude(fileName, taskInfo)
        targetFilePath = f'{targetDir}/{fileName}'
        targetFilePath = self._prepareFilename(targetFilePath)

        await self._moveFile(printedFile, targetFilePath)
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

    async def _moveFile(self, srcFileName, targetFilePath) -> None:
        ttl = 10
        while ttl > 0:
            ttl -= 1
            try:
                shutil.move(srcFileName, targetFilePath)
                break
            except PermissionError:
                # Windows sometimes failes with "WinError 32, file in use", we just try again a little later
                print(f"Waiting for {srcFileName} to become ready")
                await asyncio.sleep(1)
        if os.path.isfile(srcFileName):
            raise Exception("File rename did not worked out "+srcFileName)
