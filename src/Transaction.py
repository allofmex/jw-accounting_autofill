#!/usr/bin/python3
from _datetime import date

class Transaction:
    _name: str
    _date: date
    _amount: float
    _action: str
    _purpose: str
    
    def __init__(self, date: date, amount, action):
        self._date = date
        self._amount = amount
        self._action = action
        
    def setName(self, name):
        self._name = name
        
    def setPurpose(self, txt: dict):
        self._purpose = txt
        
    def isDonation(self):
        return self._action == "GUTSCHR. UEBERW. DAUERAUFTR" or self._action == "GUTSCHR. UEBERWEISUNG"
    
    def isCashDeposit(self):
        return self._action.startswith("BARGELDEINZAHLUNG")
    
    def isFundsTransfer(self):
        return 'txt' in self._purpose and 'Einzug jw.org' in self._purpose['txt']
    
    def isPayment(self):
        return self._action == "DAUERAUFTRAG" or self._action == "EINZELUEBERWEISUNG"
    
    def isBankingCosts(self):
        return self._action == "ENTGELTABSCHLUSS"
    
    def getDate(self):
        return self._date
    
    def getName(self):
        return self._name
    
    def getAmount(self):
        return self._amount
    
    def getSubject(self):
        return self._purpose['txt'] if 'txt' in self._purpose else ""
    
    def __repr__(self):
        purpose = self._purpose['txt'] if 'txt' in self._purpose else ""
        if len(purpose) > 30:
            purpose = purpose[:30]+".."
        return "<Transaction "+self._date.strftime("%d.%m.%y") +f"  {self._name:50s} {self._amount:10.2f}  {purpose}>"