import undetected_chromedriver as uc

class DriverMixin:
    def __init__(self, season, single_year_season):
        self.season = season
        self.single_year_season = single_year_season
        self.driver = None

    def start_driver(self):
        options = uc.ChromeOptions()
        options.headless = True
        self.driver = uc.Chrome(options=options)

    def close_driver(self):
        self.driver.close()