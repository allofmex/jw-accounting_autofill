#!/usr/bin/python3
from subprocess import getoutput
import asyncio
from os import makedirs

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpCond
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

class PageNavigator:

    URL = 'https://jw.org/de'

    def __init__(self, firefoxProfilePath: str, downloadDir: str = None):
        options = Options()
        options.binary_location = getoutput("find /snap/firefox -name firefox").split("\n")[-1]
        # options.add_argument("--kiosk") 
        ## To check if profile path is used, open about:support in firefox
        makedirs(firefoxProfilePath, exist_ok=True, mode=700)
        profile = webdriver.FirefoxProfile(firefoxProfilePath)
        profile.set_preference('browser.link.open_newwindow', 3) # new tab in current window
        # profile.set_preference("browser.link.open_newwindow.restriction", 0)
        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        if downloadDir is not None:
            profile.set_preference('browser.download.dir', downloadDir)
            # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        
            # handle print dialog, block system dialog and save as pdf
            profile.set_preference("print_printer", "Mozilla Save to PDF")
            profile.set_preference("print.always_print_silent", True)
            profile.set_preference("print.show_print_progress", False)
            profile.set_preference('print.save_as_pdf.links.enabled', True)
            profile.set_preference("print.printer_Mozilla_Save_to_PDF.print_to_file", True)
            profile.set_preference('print.printer_Mozilla_Save_to_PDF.print_to_filename',
                                   downloadDir+"/printed.pdf")
        options.profile = profile

        self.driver = webdriver.Firefox(
            service = Service(executable_path = getoutput("find /snap/firefox -name geckodriver").split("\n")[-1]),
            options = options)

        self.navWait = WebDriverWait(self.driver, 20)

    def setCredentials(self, userName, password):
        """
        userName and password may be None, will wait for manual login
        """
        self.userName = userName
        self.password = password

    async def navigateTo(self, url: str):
        self.driver.get(url)

    async def navigateToHub(self):
        """
        navigates to hub.jw.org/home/en
        """
        self.driver.get(self.URL)
        asyncio.create_task(self._acceptCookie())
        
        # acceptCookie()
        loginBtn = self.driver.find_element(By.XPATH, '//a[contains(@href,"hub.jw.org/home/") and contains(@class,"siteFeaturesItem")]')
        loginBtn.click()
        # login will open new tab
        self.driver.switch_to.window(self.driver.window_handles[1])
        await self._waitForUserLoggedIn()

    async def _expandSideNav(self):
        contextNavBtn = self.driver.find_element(By.CLASS_NAME, "side-nav__context-link")
        if not contextNavBtn.is_displayed():
            self.driver.find_element(By.CLASS_NAME, "top-nav__hamburger").click()
        self.navWait.until(ExpCond.presence_of_element_located((By.CLASS_NAME, "side-nav__context-link")))

    async def _navWithBtnForUrl(self, urlPart, className = None):
        if (className is not None):
            query = '//a[contains(@href,"'+urlPart+'") and contains(@class,"'+className+'")]'
        else:
            query = '//a[contains(@href,"'+urlPart+'")]'
        self.navWait.until(ExpCond.presence_of_element_located((By.XPATH, query))).click()

    async def _acceptCookie(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            consentBtn = wait.until(ExpCond.presence_of_element_located((By.CLASS_NAME, 'lnc-acceptCookiesButton')))
            consentBtn.click()
        except Exception:
            print("No cookie banner found")