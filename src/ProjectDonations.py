#!/usr/bin/python3
from Config import Config
from AccountsPageNavigatior import AccountsPageNavigatior
import pandas as pd
from pandas.core.frame import DataFrame
from datetime import date, datetime
from os import path

import numpy as np 

class ProjectDonations:
    ''' Keeps record of local and online donations for specific project '''
    _accountName: str
    _projectName: str
    _config: Config
    _df : DataFrame

    def __init__(self, accountName: str, projectName: str, config: Config):
        self._accountName = accountName
        self._projectName = projectName
        self._config = config
        self._df = None
        self._filePath = config.get(Config.FILEPATH_PROJECT_DONATIONS)
        self._targetNav = None

    async def update(self):
        await self.validate()
        self._writeFile()

    async def readTransferedProjectDonation(self, monthDate: datetime):
        targetNav = await self._createNavigator()
        await targetNav.navMonth(monthDate)
        await targetNav.navMonthSummary()
        return await targetNav.readProjectDonation(self._projectName)

    def addOnlineDonation(self, date: date, amount: float) -> None:
        self._addDonation('online', date, amount)

    def addLocalDonation(self, date: date, amount: float) -> None:
        self._addDonation('local', date, amount)

    async def validate(self):
        isComplete = True
        self._loadData()
        now = datetime.now()

        for year in range(2023, now.year+1):
            startMonth = 7 if year == 2023 else 1
            for month in range(startMonth, (now.month if year == now.year else 12+1)):
                if self._df is not None:
                    monthData = self._df.loc[(self._df['date'].dt.year==year) & (self._df['date'].dt.month==month)]
                else:
                    monthData = None
                date = datetime(year, month, 1)

                if not self._hasValidValue(monthData, 'local'):
                    print(f"Searching for amount of transfered local donations for {year}-{month}")
                    amount = await self.readTransferedProjectDonation(date)
                    if amount > 0:
                        print(f"Found {amount} for {year}-{month}")
                    else:
                        print(f"No project donations found for {year}-{month}. Correct?")
                    self.addLocalDonation(date, amount)
                if not self._hasValidValue(monthData, 'online'):
                    print(f"Missing amount of online donations for {year}-{month}")
                    amount = self._requestUserInput(f"Please enter amount of online donations for project '{self._projectName}' in {year}-{month} "+
                                                    "(See form 'Empfangsbestätigung')")
                    if amount is None:
                        isComplete = False
                        continue
                    self.addOnlineDonation(date, amount)

        if self._df is not None:
            self._df = self._df.groupby('date').sum(min_count=1) # merge rows for same day into one but keep Nan of no value present in column
            self._df = self._df.reindex(columns=['online', 'local']) # creates column if missing
        if not isComplete or self._df is None or self._df.isna().values.any():
            print()
            print("!!! Data incomplete !!!")

    def getSum(self) -> int:
        self._loadData()
        total = self._df[['online', 'local']].sum().sum()
        return total

    def printList(self):
        print()
        print(f"Project {self._projectName}:")
        print(self._df.to_string(formatters={'online':'{:,.2f}'.format, 'local':'{:,.2f}'.format}))

    def _addDonation(self, srcType: str, date: date, amount: int) -> None:
        date = date.replace(day=1)
        self._loadData()
        if self._df is not None and srcType in self._df:
            existing = self._df.loc[self._df['date'] == date, [srcType]]
            if (existing.any(skipna=True).item()):
                if existing.values.sum() != amount:
                    raise Exception(f"Amount {amount} does not match existing amount {existing.sum()} for {srcType}")
                else:
                    # already present
                    return

        newDf = pd.DataFrame([{'date': date, srcType: amount}])
        self._df = pd.concat([self._df, newDf])

    def _hasValidValue(self, data: DataFrame, srcType: str) -> bool:
        return data is not None and not np.isnan(data[srcType].sum(min_count=1))

    def _requestUserInput(self, promt: str) -> float:
        while True:
            valueStr = input(f"{promt} or (s)kip : ")
            if valueStr == "s":
                return None
            valueStr = valueStr.replace(',', '.')
            if valueStr.replace('.', '').isnumeric():
                return float(valueStr)
                break
            else:
                print("Invalid input")

    def _loadData(self):
        if self._df is None and path.isfile(self._filePath):
            print("Loading history data from file...")
            self._df = pd.read_csv(self._filePath)
            self._df['date'] = pd.to_datetime(self._df['date'], format='%Y-%m-%d')
        return self._df

    def _writeFile(self):
        self._df.to_csv(self._filePath, index='date', date_format='%Y-%m-%d', float_format='%.2f')

    async def _createNavigator(self):
        if self._targetNav is None:
            targetNav = AccountsPageNavigatior(self._config.get(Config.BROWSER_PROFILE_DIR))
            userName = self._config.get(Config.WEBSITE_USERNAME, False)
            if userName is not None:
                targetNav.setCredentials(userName, None)
            await targetNav.navigateToHub()
            await targetNav.navAccounting()
            await targetNav.navAccount(self._accountName)
            self._targetNav = targetNav
        return self._targetNav
