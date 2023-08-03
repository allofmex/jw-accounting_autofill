#!/usr/bin/python3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpCond
from selenium.webdriver.support.select import Select

import locale
from _datetime import date

from PageNavigator import PageNavigator

class AccountsPageNavigatior(PageNavigator):

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
        monthBtn = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/sheets/")]')
        locale.setlocale(locale.LC_TIME,'de_DE.UTF-8')
        searchedMonthstr = month.strftime("%B %Y") # like "May 2023"
        for btn in monthBtn:
            #print(btn.text)
            if btn.text == searchedMonthstr:
                # print(f'{searchedMonthstr} found')
                btn.click()
                return
        raise Exception(f'{searchedMonthstr} not found!')

    async def addElectronicContrib(self, date: date, amount: float):
        await self._navTransaction("electronic-contribution/add")
        self._fillDateInput(date)
        self._fillAmountInput(amount)
        self._clickSubmitBtn()

    async def addCashDeposit(self, date: date, amount: float):
        await self._navTransaction("/deposited-contributions/add")
        self._fillDateInput(date)
        self._fillAmountInput(amount)
        self._clickSubmitBtn()
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

    def _fillDateInput(self, date: date):
        dateInput = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//input[contains(@id, ".date") or contains(@id, ".transactionDate")]')))
        dateInput.send_keys(date.strftime("%d.%m.%y"))
        
    def _fillAmountInput(self, amount):
        amountInput = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//input[contains(@id, "form.amount")]')))
        amountInput.send_keys(f"{amount:.2f}".replace('.' , ','))

    def _completeUpload(self):
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//section[contains(@class, "file-upload-select")]')))
        self._clickSubmitBtn()

    def _clickSubmitBtn(self):
        submitBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//button[contains(@type, "submit") and contains(@class, "button--primary")]')))
        submitBtn.click()

    async def _navTransactions(self):
        addBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(@href, "/transactions") and contains(@class, "button--action")]')))
        addBtn.click()

    async def _navTransaction(self, urlPathSegment):
        await self._navTransactions()
        addBtn = self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//a[contains(@href, "'+urlPathSegment+'") and contains(@class, "list__action")]')))
        addBtn.click()
        self.navWait.until(ExpCond.presence_of_element_located((By.TAG_NAME, 'app-add-edit-transaction-container')))
        
    async def _waitForUserLoggedIn(self):
        loginWait = WebDriverWait(self.driver, 120);
        hubStartPageCond = ExpCond.presence_of_element_located((By.XPATH, '//h1[contains(@class,"top-nav__title")]'))
        inputOrTitle = loginWait.until(ExpCond.any_of(
            ExpCond.element_to_be_clickable((By.XPATH, '//input[@autocomplete="username"]')),
            hubStartPageCond));
    
        if inputOrTitle.tag_name == "input":
            if self.userName is not None:
                usernameInput = self.driver.find_element(By.ID, "username")
                usernameInput.send_keys(self.userName)
                self.driver.find_element(By.ID, "submit-button").click()
            print("##### Please login now! #####")
            loginWait.until(hubStartPageCond)
            print("Login complete")
        else: # h1
            print("Already logged in.")

    def _waitPrintReportReady(self):
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, '//section[contains(@class,"page--print-layout")]')))
