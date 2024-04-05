#!/usr/bin/python3
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ExpCond
from selenium.webdriver.support.select import Select

import locale
from _datetime import date
import re

from jw_page_navigation.PageNavigator import PageNavigator

class AccountsPageNavigatior(PageNavigator):

    _isSimulation = False

    async def loginAndNavMonth(self, accountName : str, month : date):
        await self.navigateToHub()
        await self.navAccounting()
        await self.navAccount(accountName)
        await self.navMonth(month)

    async def navAccounting(self):
        await self._navWithBtnForUrl("app/field-accounting")
        self.navWait.until(ExpCond.presence_of_element_located((By.TAG_NAME, "app-accounting-overview")))
        
    async def navAccount(self, accountName):
        accountCards = self.driver.find_elements(By.CLASS_NAME, "card__header")
        for cardInfo in accountCards:
            print("Found account " +cardInfo.text)
            if cardInfo.text == accountName:
                cardInfo.click()
                return
        raise Exception(f'Card "{accountName}" not found!')
    
    async def navMonth(self, month: date):
        await self._expandSideNav()
        
        await self._navWithBtnForUrl("/sheets", "side-nav__link")
        # self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(@href, "/sheets") and contains(@class, "side-nav__link")]'))).click()
        self.navWait.until(ExpCond.presence_of_element_located((By.TAG_NAME, 'app-period-list')))
        container = self.driver.find_element(By.TAG_NAME, 'app-sheets-by-year')
        yearList = container.find_elements(By.TAG_NAME, 'article')
        searchedYearStr = month.strftime("%Y") # like "May 2023"
        for yearToggle in yearList:
            if yearToggle.text == searchedYearStr:
                if 'card--collapsed' in yearToggle.get_attribute('class'):
                    yearToggle.click()
                yearArticleId = yearToggle.get_attribute('id')
                self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, f"//article[@id='{yearArticleId}']//ul")))
                monthBtn = yearToggle.find_elements(By.XPATH, "//a[contains(@href, '/sheets/')]")
                locale.setlocale(locale.LC_TIME,'de_DE.UTF-8')
                searchedMonthstr = month.strftime("%B") # like "May"
                for btn in monthBtn:
                    if btn.text == searchedMonthstr:
                        btn.click()
                        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//app-entity-header[contains(@pageheader, "Accounting_HdgMonthlyActivity_Colon")]')))
                        return
        raise Exception(f'{searchedMonthstr} not found!')
    
    async def navMonthSummary(self):
        sumBlock = self.navWait.until(ExpCond.element_to_be_clickable((By.TAG_NAME, 'app-activity-summary'))) # not clickable
        collapseHead = sumBlock.find_element(By.TAG_NAME, 'article')
        if 'card--collapsed' in collapseHead.get_attribute('class'):
            collapseHead.click()

    async def readProjectDonation(self, projectName: str) -> float :
        summaryItems = self.driver.find_elements(By.XPATH, '//dt[contains(@class, "data__label")]')
        for labelItem in summaryItems:
            if labelItem.text == projectName:
                parent = labelItem.find_element(By.XPATH, './..')
                valueWithCurrency = parent.find_element(By.CLASS_NAME, 'currency-amount').text
                return self._parseAmount(valueWithCurrency)

    async def navCloseMonthStart(self):
        closeMonthStartBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//ptrn-icon[contains(@icon, "calendar-checkmark")]')))
        # closeMonthStartBtn = self.driver.find_elements(By.XPATH, '//ptrn-icon[contains(icon, "calendar-checkmark")]')
        closeMonthStartBtn.click()

    async def readTransferAmountFromDonationBox(self) -> float:
        """ Reading amount that will be transfered additionally to resolution amount
        (from worldwide donation box or project donations)
        """
        self.navWait.until(ExpCond.presence_of_element_located((By.TAG_NAME, 'app-total-amount')))
        form = self.driver.find_element(By.XPATH, '//section[contains(@class, "step__content")]')
        items = form.find_elements(By.XPATH, '//div[contains(@class, "grid__item")]')
        amount = 0
        for gridItem in items:
            itemElements = gridItem.find_elements(By.XPATH, "*")
            if (len(itemElements) > 0 and itemElements[0].tag_name == "p"):
                # read only grid-items containing p tag, others are inputs or summary
                amount += self._parseAmount(gridItem.text)
        if amount <= 0:
            raise Exception("No non-congregation donations item found, maybe this tool needs an update..")
        return amount

    async def setResultionInput(self, amount: int):
        self.navWait.until(ExpCond.presence_of_element_located((By.TAG_NAME, 'app-total-amount')))
        ## no unique identifier available für input fields
        inputs = self.driver.find_elements(By.XPATH, '//input[contains(@id, "form.unknown")]')
        resolutionInput = inputs[0]
        resolutionInput.clear()
        resolutionInput.send_keys(f"{amount:.2f}".replace('.' , ','))

    async def addElectronicContrib(self, date: date, amount: float, label: str = None):
        await self._navTransaction("electronic-contribution/add")
        self._fillDateInput(date)
        self._fillAmountInput(amount)
        if label is not None:
            self._fillDescInput(label)
        if self._isSimulation:
            self._clickCancelBtn()
            await self._navWithBtnForUrl("/congregation/sheets/", "breadcrumb__breadcrumb-link")
            return
        self._clickSubmitBtn()

    async def addCashDeposit(self, date: date, amount: float):
        await self._navTransaction("/deposited-contributions/add")
        self._fillDateInput(date)
        self._fillAmountInput(amount)
        self._clickSubmitBtn()
        if self._isSimulation:
            self._clickPreviousBtn()
            await self._navWithBtnForUrl("/congregation/sheets/", "breadcrumb__breadcrumb-link")
            # await self.navAccounting()
            return
        self._completeUpload()
        
    async def addPayment(self, date: date, amount: float, text: str, categoryValue: str):
        await self._navTransaction("/paid-expense/add")
        self._fillDateInput(date)
        self._fillAmountInput(amount)
        # select main account
        radioBtn = self.driver.find_elements(By.XPATH, '//label[contains(@for, "takeFrom-radio-item") and contains(@class, "field__button-input-label--radio")]')
        radioBtn[0].click() # ToDo: check for correct option element (but do not use form1.takeFrom-radio-item-0, it is not stable)

        descriptionInput = self.navWait.until(ExpCond.presence_of_element_located((By.ID, 'form.description')))
        descriptionInput.send_keys(text)
        
        catSelect = self.navWait.until(ExpCond.presence_of_element_located((By.ID, 'form.transactionCategory')))
        select = Select(catSelect)
        select.select_by_value(categoryValue)
        # select.select_by_index(3)
        self._clickSubmitBtn()
        if self._isSimulation:
            self._clickPreviousBtn()
            self._clickPreviousBtn()
            await self._navWithBtnForUrl("/congregation/sheets/", "breadcrumb__breadcrumb-link")
            return
        self._completeUpload()

    async def downloadReportS26(self):
        ## be aware of different dash character for de and en locale!
        btn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//button[contains(.,"S‑26") or contains(.,"S-26")]')))
        btn.click()
        self._waitPrintReportReady()

    async def downloadReportS30(self):
        ## be aware of different dash character for de and en locale!
        btn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//button[contains(.,"S‑30") or contains(.,"S-30")]')))
        btn.click()
        self._waitPrintReportReady()
        
    async def downloadReportTO62(self):
        ## be aware of different dash character for de and en locale!
        btn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(.,"TO‑62") or contains(.,"TO-62")]')))
        btn.click()
        self.driver.switch_to.window(self.driver.window_handles[2])
        self._waitPrintReportReady()
        self._clickPrintBtn()

    def setSimulation(self):
        self._isSimulation = True

    def _fillDateInput(self, date: date):
        dateInput = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//input[contains(@id, ".date") or contains(@id, ".transactionDate")]')))
        dateInput.send_keys(date.strftime("%d.%m.%y"))
        
    def _fillAmountInput(self, amount):
        amountInput = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//input[contains(@id, "form.amount")]')))
        amountInput.send_keys(f"{amount:.2f}".replace('.' , ','))

    def _fillDescInput(self, text: str):
        descInput = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//input[contains(@id, "form.description")]')))
        descInput.clear()
        descInput.send_keys(text)

    def _completeUpload(self):
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//section[contains(@class, "file-upload-select")]')))
        self._clickSubmitBtn()

    def _clickSubmitBtn(self):
        submitBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//button[contains(@type, "submit") and contains(@class, "button--primary")]')))
        submitBtn.click()
        
    def _clickCancelBtn(self):
        submitBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//ptrn-button[contains(@id, "cancelButton")]')))
        submitBtn.click()
        
    def _clickPreviousBtn(self):
        prevBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//ptrn-button[@ptrnstepperprevious]')))
        prevBtn.click()
        
    def _clickPrintBtn(self):
        printBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//ptrn-button[contains(@icon, "printer")]')))
        printBtn.click()

    async def _navTransactions(self):
        addBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(@href, "/transactions") and contains(@class, "button--action")]')))
        addBtn.click()

    async def _navTransaction(self, urlPathSegment):
        await self._navTransactions()
        addBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(@href, "'+urlPathSegment+'") and contains(@class, "list__action")]')))
        addBtn.click()
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, 
                "//app-e-contribution-container | //app-add-edit-transaction-container | //app-deposited-contributions-container")))

    def _waitPrintReportReady(self):
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//section[contains(@class,"page--print-layout")]')))

    def _parseAmount(self, valueWithCurrency: str) -> float:
        match = re.search("^([\d,.]+)[,.](\d{2})\s.*$", valueWithCurrency)
        if (match is None):
            raise Exception(f'Amount could not be parsed from {valueWithCurrency}')
        return float(f'{match.group(1)}.{match.group(2).replace(",","").replace(".","")}')
