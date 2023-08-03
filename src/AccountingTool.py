#!/usr/bin/python3
import readchar

from AccountReportReader import AccountReportReader
from AccountsPageNavigatior import AccountsPageNavigatior
from Transaction import Transaction
from Config import Config
from TransactionTaskInfo import TransactionTaskInfo

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
        print("Found data:")
        reportReader.printData()
        if not self._requestUserConfirm("Is this correct? [y/n]"):
            print("Exiting")
            return
        
        print("Navigating to website")
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR))

        userName = self.config.get(Config.WEBSITE_USERNAME, False)
        if userName is not None:
            targetNav.setCredentials(userName, None)

        await targetNav.navigateToHub()
        await targetNav.navAccounting()

        await targetNav.navAccount(taskInfo.getAccountName())
        await targetNav.navMonth(taskInfo.getMonth())
        
        for transaction in transactions:
            if transaction.isDonation():
                if not self._isSimulation:
                    await targetNav.addElectronicContrib(transaction.getDate(), transaction.getAmount())
                self._logTransaction("Donation", transaction)
            elif transaction.isCashDeposit():
                if not self._isSimulation:
                    await targetNav.addCashDeposit(transaction.getDate(), transaction.getAmount())
                self._logTransaction("Cash deposit", transaction)
            elif transaction.isPayment():
                category = self.CAT_HALL # ToDo
                if not self._isSimulation:
                    await targetNav.addPayment(transaction.getDate(), transaction.getAmount(), transaction.getSubject(), category)
                print("Please update type of payment manually afterwards for "+transaction.getSubject())
                self._logTransaction("Payment", transaction)
            elif transaction.isBankingCosts():
                if not self._isSimulation:
                    await targetNav.addPayment(transaction.getDate(), transaction.getAmount(), "Bankgebühren", self.CAT_OTHER)
                self._logTransaction("Banking costs", transaction)
            elif transaction.isFundsTransfer():
                print("Fund transfer found {transaction.getAmount()}. Skipping because it does not need to handled.")
            else:
                print("Unhandled transaction!"+str(transaction))

    def setSimulation(self):
        self._isSimulation = True
        
    def _logTransaction(self, label: str, transaction: Transaction):
        date = transaction.getDate().strftime("%d.%m.%y")
        tag = "SIMULATED" if self._isSimulation else ""
        print(f"  {label:20s} handled.    {date} {transaction.getAmount():10.2f}   {tag}")

    def _requestUserConfirm(self, msg):
        print(msg)
        while True:
            key = readchar.readkey()
            if key == 'y':
                return True
            elif key == 'n':
                return False
