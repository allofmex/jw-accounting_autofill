#!/usr/bin/python3
import csv, re
from datetime import datetime
from Transaction import Transaction
from typing import List


class AccountReportReader:
    """
    CSV-MT940-Format
    """

    DATE_COL = 1
    AMOUNT_COL = 8
    PURPOSE_COL = 4

    data: List[Transaction]

    def __init__(self):
        self.result = {}
        self.data = []
        self.errorLog = []

    def read(self, csvFilePath: str):
        with open(csvFilePath, mode='r', encoding='latin-1') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            data = []
            multiLineTxt = ""
            for row in reader:
                # "Auftragskonto";"Buchungstag";"Valutadatum";"Buchungstext";"Verwendungszweck";"Beguenstigter/Zahlungspflichtiger";"Kontonummer";"BLZ";"Betrag";"Waehrung";"Info"
                try:
                    amount = self._parseAmount(row)
                    if amount != 0:
                        
                        transaction = Transaction(self._parseDate(row), amount, row[3])
                        transaction.setName(self._parseRecvName(row))
                        try:
                            transaction.setPurpose(self._parsePurpose(row))
                        except Exception:
                            transaction.setPurpose({'alt': row[self.PURPOSE_COL]})
                        data.append(transaction)
                        multiLineTxt = ""
                    else:
                        multiLineTxt += row[self.PURPOSE_COL]
                except ValueError:
                    msg = "Line "+row[1]+" skipped!"
                    print(msg)
                    self.errorLog.append(msg)

            sorter = _Sorter(_Sorter.MODE_BW_BANK)
            sortedlist = sorter.sort(data)
            self.data = sortedlist
        return self.result
    
    def getTransactions(self) -> List[Transaction]:
        return self.data

    def printData(self):
        ''' For debugging '''
        for transact in self.data:
            print(transact)

    def _parseDate(self, row):
        return datetime.strptime(row[self.DATE_COL], "%d.%m.%y")
    
    def _parseRecvName(self, row):
        return row[5].title()  # first letter uppercase, rest lower

    def _parseAmount(self, row):
        return float(row[self.AMOUNT_COL].replace(",", "."))
    
    def _parsePurpose(self, row):
        rawTxt = row[self.PURPOSE_COL]
        regEx = re.search(r'^.*SVWZ\+([^+]+)(?:ABWA\+([^+]+))?$', rawTxt)
        if regEx is not None:
            result = {
                'txt': regEx.group(1)
            }
            if regEx.group(2) is not None:
                # ABWA, abweichender Auftraggeber
                result['inOtherName'] = regEx.group(2)
            return result
        else:
            raise Exception("Purpose text error "+rawTxt)


class _Sorter:
    MODE_DATE = 1
    MODE_BW_BANK = 9000
    
    def __init__(self, mode):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.trans = str.maketrans(alphabet, alphabet[::-1], ' ') # a-z,z-a
        self.mode = mode
    
    def sort(self, data):
        return sorted(data, key=self._compare, reverse=False)
        
    def _compare(self, transact : Transaction):
        try:
            dateStr = transact.getDate().strftime("%y%m%d")
            name = transact.getName()
            if (self.mode == self.MODE_DATE):
                key = f"{dateStr}"
            elif (self.mode == self.MODE_BW_BANK):
                # Buchungstag
                # Betrag
                # Begünstigter     (Z bis A)
                name = name.lower().translate(self.trans) # sort-by-name-reversed
                key = f"{dateStr}{transact.getAmount():08.2f}{name}"
            else:
                raise Exception("Not implemented")
            return key
        except ValueError:
            return "0"
