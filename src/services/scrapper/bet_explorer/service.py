import time
import typing as t
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from tqdm import tqdm

from utils.helper_functions import get_season_str

from ..mixins import DriverMixin


class BetExplorerScrapperService(DriverMixin):
    def __init__(
        self,
        country: str,
        league: str,
        stage: str,
        season: t.Optional[int],
        single_year_season: bool,
    ):
        DriverMixin.__init__(
            self,
            season=season,
            single_year_season=single_year_season,
        )
        self.stage = stage
        self.country = country
        self.league = league

    def parse_betexplorer_date(self, date_str: str) -> datetime:
        if date_str == "Today":
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_str == "Yesterday":
            date = (datetime.now() - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            if not date_str.split(".")[-1]:
                date_str += str(datetime.now().year)
            date = datetime.strptime(date_str, "%d.%m.%Y")

        return date

    def bet_explorer_scrapper(self) -> None:
        bet_explorer_data = []

        season_str = get_season_str(self.single_year_season, self.season)
        if season_str:
            season_str = f"-{season_str}"

        url = f"https://www.betexplorer.com/football/{self.country}/{self.league}{season_str}/results/"

        self.driver.get(url)

        time.sleep(5)

        # Select the desired stage if valid
        try:
            if self.stage:
                btn = self.driver.find_element(
                    By.XPATH, f"//*[contains(text(), '{self.stage}')]"
                )
                btn.click()

                time.sleep(3)
        except:
            pass

        table = self.driver.find_element(
            By.XPATH, '//*[@id="js-leagueresults-all"]/div/div/table'
        )
        matches = table.find_elements(By.XPATH, ".//tbody/tr")

        print("Scrapping info from the BetExplore website:")
        for i in tqdm(range(len(matches))):
            curr_match = matches[i]
            if not curr_match.text:
                continue

            tds = curr_match.find_elements(By.XPATH, ".//child::td")
            if len(tds) < 6:
                continue

            matchup, score, home_odds, draw_odds, away_odds, date = [
                t.text for t in tds
            ]

            try:
                if not score:
                    continue
                home_score, away_score = score.split(":")

                if not matchup:
                    continue
                home_team, away_team = matchup.split(" - ")

                parsed_date = self.parse_betexplorer_date(date)

                match_info = {
                    "date": parsed_date,
                    "home_team": home_team,
                    "home_score": int(home_score),
                    "home_odds": float(home_odds),
                    "away_team": away_team,
                    "away_score": int(away_score),
                    "away_odds": float(away_odds),
                    "draw_odds": float(draw_odds),
                }
                bet_explorer_data.append(match_info)
            except Exception:
                continue

        self.bet_explorer_data_df = pd.DataFrame(bet_explorer_data)
