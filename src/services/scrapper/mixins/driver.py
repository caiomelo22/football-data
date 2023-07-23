import undetected_chromedriver as uc
import shutil

class DriverMixin:
    def __init__(self, start_season, end_season, single_year_season):
        self.start_season = start_season
        self.end_season = end_season
        self.single_year_season = single_year_season
        self.driver = None

    def start_driver(self):
        options = uc.ChromeOptions()
        options.headless = False
        self.driver = uc.Chrome(options=options, executable_path=shutil.which('chromedriver'))
        self.driver.maximize_window()

    def close_driver(self):
        self.driver.close()