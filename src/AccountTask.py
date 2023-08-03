#!/usr/bin/python3
from _datetime import date

class AccountTask:
    def __init__(self, accountName, month):
        self.accountName = accountName
        self.month = month

    def getAccountName(self):
        return self.accountName
    
    def getMonth(self) -> date:
        return self.month