#!/usr/bin/python3
import readchar

from AccountReportReader import AccountReportReader
from AccountsPageNavigatior import AccountsPageNavigatior
from Transaction import Transaction
from Config import Config
from TransactionTaskInfo import TransactionTaskInfo
from typing import List
from Tools import validatedIntegerStr

class AccountingTool:
    CAT_HALL = 'eaac3e7e-bb9e-4bc9-b35b-5bb1a3a7fe5e'
    CAT_OTHER = '2a84f1ab-6994-40ff-a286-386cae927bb0'

    _isSimulation = False

    def __init__(self, config: Config):
        self.config = config
        self.workingDir = config.get(Config.WORK_DIR)

    async def run(self, taskInfo : TransactionTaskInfo):
        print("Reading account report file "+taskInfo.getSourceFile())
        reportReader = AccountReportReader()
        # reportReader.read(SCRIPT_PATH+"/umsatz2.csv")
        reportReader.read(taskInfo.getSourceFile())
        transactions = reportReader.getTransactions()
        self._updateUserSubstitudes(transactions)
        print("Found data:")
        reportReader.printData()
        if not self._requestUserConfirmForUpload(transactions, taskInfo):
            print("Exiting")
            return
        
        print("Navigating to website")
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR))
        if (self._isSimulation):
            targetNav.setSimulation()

        userName = self.config.get(Config.WEBSITE_USERNAME, False)
        if userName is not None:
            targetNav.setCredentials(userName, None)

        await targetNav.navigateToHub()
        await targetNav.navAccounting()

        await targetNav.navAccount(taskInfo.getAccountName())
        await targetNav.navMonth(taskInfo.getMonth())
        
        for i in range(taskInfo.getStartIdx(), len(transactions)):
        # for transaction in transactions:
            transaction = transactions[i]
            if transaction.isDonation():
                # if not self._isSimulation:
                await targetNav.addElectronicContrib(transaction.getDate(), transaction.getAmount())
                self._logTransaction("Donation", transaction)
            elif transaction.isJwDonation():
                # if not self._isSimulation:
                label = self.config.get(Config.DESC_JW_ORG_DONATIONS)
                await targetNav.addElectronicContrib(transaction.getDate(), transaction.getAmount(), label)
                self._logTransaction("Jw.org Donation", transaction)
            elif transaction.isCashDeposit():
                # if not self._isSimulation:
                await targetNav.addCashDeposit(transaction.getDate(), transaction.getAmount())
                self._logTransaction("Cash deposit", transaction)
            elif transaction.isPayment():
                category = self.CAT_HALL # ToDo
                # if not self._isSimulation:
                
                await targetNav.addPayment(transaction.getDate(), transaction.getAmount(), transaction.getSubject(), category)
                print("Please update type of payment manually afterwards for "+transaction.getSubject())
                self._logTransaction("Payment", transaction)
            elif transaction.isBankingCosts():
                # if not self._isSimulation:
                await targetNav.addPayment(transaction.getDate(), transaction.getAmount(), "Bankgebühren", self.CAT_OTHER)
                self._logTransaction("Banking costs", transaction)
            elif transaction.isFundsTransfer():
                print(f"Fund transfer found {transaction.getAmount()}. Skipping because it does not need to handled.")
            elif transaction.isOtherContribution():
                await targetNav.addElectronicContrib(transaction.getDate(), transaction.getAmount(), transaction.getSubject())
                self._logTransaction("Other incomming contribution", transaction)
            else:
                print("Unhandled transaction!"+str(transaction))

    def setSimulation(self):
        self._isSimulation = True
        
    def _logTransaction(self, label: str, transaction: Transaction):
        date = transaction.getDate().strftime("%d.%m.%y")
        tag = "SIMULATED" if self._isSimulation else ""
        print(f"  {label:20s} handled.    {date} {transaction.getAmount():10.2f}   {tag}")

    def _requestUserConfirmForUpload(self, transactions: List[Transaction], taskInfo: TransactionTaskInfo):
        print("Is this correct? (Transactions will be created on website!) [(y)es / (n)o / (r)esume previous upload]")
        while True:
            key = readchar.readkey()
            if key == 'y':
                return True
            elif key == 'n':
                return False
            elif key == 'r': 
                print("What row number to start to upload? (q for quit)")
                numStr = ''
                while True:
                    key = readchar.readkey()
                    if key == readchar.key.ENTER:
                        try:
                            startIdx = validatedIntegerStr(numStr, 0, len(transactions) -1)
                            startIdx = int(numStr)
                            taskInfo.setStartIdx(startIdx)
                            print(f"Starting from row {startIdx}")
                            return True
                        except ValueError as e:
                            print("Invalid number")
                            print(e)
                            numStr = ''
                    elif key == 'q':
                        return False
                    else:
                        print(key, end='', flush=True)
                        numStr += key

    def _updateUserSubstitudes(self, transactions: List[Transaction]):
        for transaction in transactions:
            subject = transaction.getSubject()
            overridePurpose = self.config.getSubstitude(Config.SUBSTITUDES_PURPOSE, subject)
            if overridePurpose is not None:
                print(f"'{subject}' replaced by '{overridePurpose}'")
                transaction.setOverridePurpose(overridePurpose)
