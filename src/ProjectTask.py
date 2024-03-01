#!/usr/bin/python3
from AccountTask import AccountTask

class ProjectTask(AccountTask):
    _projectName : str

    def __init__(self, accountName, projectName : str, month):
        super().__init__(accountName, month)
        self._projectName = projectName

    def getProjectName(self):
        return self._projectName