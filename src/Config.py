import yaml, os

class Config:

    CONG_NAME = 'congregationName'
    
    WEBSITE_USERNAME = 'websiteUserName'
    
    WORK_DIR = 'workDir'
    BROWSER_PROFILE_DIR = 'browserProfileDir'
    
    DESC_JW_ORG_DONATIONS = 'DescDonationsViaJwOrg'
    DESC_KH_MONTHLY = 'DescKhCostsMonthly'
    
    MAIL_SUBJECT_TRANSFER_APPROVAL = 'mailing/fundTransferApproval/subject'
    MAIL_TEMPLATE_TRANSFER_APPROVAL = 'mailing/fundTransferApproval/bodyTemplate'
    MAIL_ACC_TRANSFER_APPROVAL = 'mailing/fundTransferApproval/acc'
    
    FILEPATH_RESULTS_BASE = 'filePathResultsBase'
    FILEPATH_S26 = 'filePathS26'
    FILEPATH_S30 = 'filePathS30'
    FILEPATH_TO62 = 'filePathTO62'

    def __init__(self, configFilePath, basePath):
        self.basePath = basePath
        file = open(configFilePath, 'r')
        self.content = yaml.load(file, Loader=yaml.SafeLoader)

    def get(self, key: str, required: bool = True):
        if key not in self.content:
            # test if multi/level/key
            levels = key.split('/')
            if len(levels) > 1:
                innerContent = self.content
                for level in levels:
                    innerContent = innerContent[level]
                data = innerContent
            else:
                data = self._getDefault(key)
        else:
            data = self.content[key]
        if required == True and data is None:
            raise Exception(f"Key {key} is empty in config file!")
        
        if self._isFilePathKey(key):
            if self._isResultFilePathKey(key):
                basePath = self.get(self.FILEPATH_RESULTS_BASE) + '/'
            elif self._isWorkingFilePathKey(key):
                basePath = self.get(self.WORK_DIR) + '/'
            elif key is self.FILEPATH_RESULTS_BASE:
                basePath = ''
            else:
                basePath = self.basePath+ '/'
            data = basePath +data
            data = os.path.expandvars(data)
        return data
    
    def _getDefault(self, key: str):
        if key == self.WORK_DIR:
            return f'{self.basePath}/tmp'
        if key == self.BROWSER_PROFILE_DIR:
            return 'firefox-profile'
        return None
    
    def _isFilePathKey(self, key):
        return (self._isResultFilePathKey(key)
                or self._isWorkingFilePathKey(key) 
                or key == self.MAIL_TEMPLATE_TRANSFER_APPROVAL
                or key == self.FILEPATH_RESULTS_BASE)

    def _isResultFilePathKey(self, key):
        return (key == self.FILEPATH_S26 or key == self.FILEPATH_S30 or key == self.FILEPATH_TO62)
    
    def _isWorkingFilePathKey(self, key):
        return (key == self.BROWSER_PROFILE_DIR)
        