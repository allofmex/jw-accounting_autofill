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
        
    def setOverridePurpose(self, txt: str):
        self._purpose['override'] = txt
    
    def isIncommingBankTransfer(self):
        return self._amount > 0 and self._action == "GUTSCHR. UEBERW. DAUERAUFTR" or self._action == "GUTSCHR. UEBERWEISUNG"
    
    def isDonation(self):
        return self.isIncommingBankTransfer() and 'txt' in self._purpose and "spende" in self._purpose['txt'].lower()

    def isOtherContribution(self):
        return self.isIncommingBankTransfer() and 'txt' in self._purpose and "spende" not in self._purpose['txt'].lower()
        
    def isJwDonation(self):
        # unsharp string detect because it is changed frequently (upper/lower case, with/without comma or dots) 
        return self._amount > 0 and 'jehovas zeugen in deutschland k d' in self._name.lower().replace(',', '').replace('.', '');
    
    def isCashDeposit(self):
        return self._action.startswith("BARGELDEINZAHLUNG")
    
    def isFundsTransfer(self):
        return self._amount < 0 and 'txt' in self._purpose and 'Einzug jw.org' in self._purpose['txt']
    
    def isPayment(self):
        return self._amount < 0 and self._action == "DAUERAUFTRAG" or self._action == "EINZELUEBERWEISUNG" or self._action == "ONLINE-UEBERWEISUNG"
    
    def isBankingCosts(self):
        return self._action == "ENTGELTABSCHLUSS"
    
    def getDate(self):
        return self._date
    
    def getName(self):
        return self._name
    
    def getAmount(self):
        return self._amount
    
    def getSubject(self):
        if 'override' in self._purpose:
            return self._purpose['override']
        elif 'txt' in self._purpose:
            return self._purpose['txt']
        else:
            return ""

    def _getTypePrint(self):
        if self.isDonation():
            return "Donation"
        elif self.isJwDonation():
            return "JWORG Donation"
        elif self.isOtherContribution():
            return "Other contribution"
        elif self.isFundsTransfer():
            return "FundTransfer"
        elif self.isBankingCosts():
            return "BankingCosts"
        elif self.isCashDeposit():
            return "CashDeposit"
        elif self.isPayment():
            return "Payment"
        return "UNKNOWN!";
    
    def __repr__(self):
        purpose = self.getSubject()
        if len(purpose) > 30:
            purpose = purpose[:30]+".."
        return "<Transaction "+self._date.strftime("%d.%m.%y") +f"  {self._name:50s} {self._amount:10.2f}  {purpose:35s} {self._getTypePrint():10s}>"
        