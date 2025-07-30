import typing as t
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class DriverMixin:
    def __init__(
        self,
        season: t.Optional[int] = None,
        single_year_season: t.Optional[bool] = None,
    ):
        self.season = season
        self.single_year_season = single_year_season
        self.driver = None

    def start_driver(self) -> None:
        # Set Chrome options (for example, to run headless if desired)
        chrome_options = Options()
        # chrome_options.add_argument('--headless=new')

        # Fetch the latest ChromeDriver version and start the driver
        service = Service(ChromeDriverManager().install())

        # Start the Chrome driver with the given service and options
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def close_driver(self) -> None:
        # Gracefully close the driver
        if self.driver:
            self.driver.quit()
