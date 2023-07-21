from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

class DriverMixin:
    def __init__(self, start_season, end_season, single_year_season):
        self.start_season = start_season
        self.end_season = end_season
        self.single_year_season = single_year_season
        self.driver = None

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # driver.maximize_window()

    def close_driver(self):
        self.driver.close()