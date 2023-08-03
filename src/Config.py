import yaml

class Config:

    CONG_NAME = 'congregationName'
    
    WEBSITE_USERNAME = 'websiteUserName'
    
    WORK_DIR = 'workDir'
    BROWSER_PROFILE_DIR = 'browserProfileDir'
    
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
            data = self._getDefault(key)
        else:
            data = self.content[key]
        if required == True and data is None:
            raise Exception("Key {key} is empty in config file!")
        
        if key == self.FILEPATH_S26 or key == self.FILEPATH_S30:
            data = self.get(self.FILEPATH_RESULTS_BASE) + '/' +data
        return data
    
    def _getDefault(self, key: str):
        if key == self.WORK_DIR:
            return f'{self.basePath}/tmp'
        if key == self.BROWSER_PROFILE_DIR:
            return f'{self.get(self.WORK_DIR)}/firefox-profile'
        return None