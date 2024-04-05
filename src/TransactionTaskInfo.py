#!/usr/bin/python3
from AccountTask import AccountTask

class TransactionTaskInfo(AccountTask):
    
    def __init__(self, accountName, month, sourceFile):
        super().__init__(accountName, month)
        self.sourceFile = sourceFile
        self._startIdx = 0

    def getSourceFile(self):
        return self.sourceFile

    def setStartIdx(self, startIdx: int):
        """
        Set row index to start with (in case of partial uploads)
        """
        self._startIdx = startIdx

    def getStartIdx(self):
        return self._startIdx