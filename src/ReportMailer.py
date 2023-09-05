#!/usr/bin/python3
from os import path
import pathlib
from datetime import datetime

from jw_page_navigation.MailingHelper import MailingHelper
from Config import Config
from Template import substitude, loadTemplate
from AccountTask import AccountTask

class ReportMailer():
    def __init__(self, config: Config):
        self._config = config
        self._mailer = None

    async def prepareTransferApprovalMail(self, task: AccountTask):
        subject = substitude(self._config.get(Config.MAIL_SUBJECT_TRANSFER_APPROVAL), task)
        acc = self._config.get(Config.MAIL_ACC_TRANSFER_APPROVAL)
        templatePath = self._config.get(Config.MAIL_TEMPLATE_TRANSFER_APPROVAL)
        template = substitude(loadTemplate(templatePath), task)

        formPath = self._getMostRecentFile(substitude(self._config.get(Config.FILEPATH_TO62), task))

        accountBalance = self._getUserInput(f"Enter bank account balance at end of {task.getMonth().strftime('%b')}: ")
        template = template.replace("%%BALANCE%%", self._toLocaleAmount(accountBalance))
        transferAmount = self._getUserInput("Enter amount to transfer: ")
        template = template.replace("%%AMOUNT%%", self._toLocaleAmount(transferAmount))

        await self._initMailingHelper()
        await self._mailer.startNewMail()
        await self._mailer.setSubject(subject)
        await self._mailer.setBody(template)
        await self._mailer.setTo(acc)
        await self._mailer.addAttachment(formPath)

    def _getUserInput(self, msg: str):
        while True:
            resolutionValueStr = input(msg).replace(',', '.')
            if resolutionValueStr == 'q':
                raise Exception("Canceled by user")
            try:
                return float(resolutionValueStr)
            except ValueError:
                print("Invalid input!")

    def _toLocaleAmount(self, value: float):
        return f"{value:10.2f} €".replace('.', ',')
    
    def _getMostRecentFile(self, filePath: str) -> str:
        fileName = path.basename(filePath)
        extStart = fileName.rindex(".")
        targetPattern = f'{fileName[:extStart]}*{fileName[extStart:]}'
        print(targetPattern)
        resultPath = path.dirname(filePath)
        files = list(pathlib.Path(resultPath).glob(targetPattern))
        if len(files) == 1:
            return str(files[0]) # to string because PosixPath object
        elif len(files) > 1:
            for i in range(len(files)):
                file = files[i]
                fileDate = datetime.fromtimestamp(path.getmtime(file))
                print(f"{i+1:2d}: {path.basename(file):10s} {fileDate.strftime('%d.%m.%y %H:%M:%S') }")
            selIdx = int(self._getUserInput(f"Select file to send [1-{len(files)}]: "))
            
            return str(files[selIdx-1])
        else:
            raise Exception(f"No TO-62 form ({fileName}) found in {resultPath}. Did you created it already?")
    
    async def _initMailingHelper(self):
        if self._mailer is None:
            self._mailer = MailingHelper(self._config.get(Config.BROWSER_PROFILE_DIR))
            userName = self._config.get(Config.WEBSITE_USERNAME, False)
            if userName is not None:
                self._mailer.setCredentials(userName, None)
        await self._mailer.load()
        