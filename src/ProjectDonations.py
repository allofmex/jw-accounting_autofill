#!/usr/bin/python3
from Config import Config
from AccountsPageNavigatior import AccountsPageNavigatior
from ProjectTask import ProjectTask

class ProjectDonations:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        
    async def readDonations(self, taskInfo : ProjectTask):
        targetNav = self._createNavigator()
        await targetNav.loginAndNavMonth(taskInfo.getAccountName(), taskInfo.getMonth());
        await targetNav.navMonthSummary()
        return await targetNav.readProjectDonation(taskInfo.getProjectName())

    def _createNavigator(self):
        targetNav = AccountsPageNavigatior(self.config.get(Config.BROWSER_PROFILE_DIR))
        userName = self.config.get(Config.WEBSITE_USERNAME, False)
        if userName is not None:
            targetNav.setCredentials(userName, None)
        return targetNav