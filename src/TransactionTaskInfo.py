#!/usr/bin/python3
from AccountTask import AccountTask

class TransactionTaskInfo(AccountTask):
    def __init__(self, accountName, month, sourceFile):
        super().__init__(accountName, month)
        self.sourceFile = sourceFile

    def getSourceFile(self):
        return self.sourceFile