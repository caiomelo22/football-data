import time
from datetime import datetime as dt, timedelta
from selenium.webdriver.common.by import By
from tqdm import tqdm

from ..mixins import DriverMixin


class BetExplorerScrapperService(DriverMixin):
    def __init__(self, country, league, stage, season, single_year_season):
        DriverMixin.__init__(
            self,
            season=season,
            single_year_season=single_year_season,
        )
        self.stage = stage
        self.bet_explorer_country = country
        self.bet_explorer_league = league

    def transform_odds_date(self, date):
        return dt.strptime(date, "%d.%m.%Y")

    def bet_explorer_scrapper(self, hide_last_season_str=False):
        self.bet_explorer_season = []

        if hide_last_season_str:
            season_str = ""
        elif self.single_year_season:
            season_str = f"-{self.season}"
        else:
            season_str = f"-{self.season}-{self.season+1}"

        url = f"https://www.betexplorer.com/football/{self.bet_explorer_country}/{self.bet_explorer_league}{season_str}/results/"
        self.driver.get(url)

        time.sleep(5)

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
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        total_games = 0
        print("Scrapping info from the betexplorer website:")
        for i in tqdm(range(len(rows))):
            r = rows[i]
            if not r.text:
                continue

            tds = r.find_elements(By.XPATH, ".//child::td")
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

                if date == "Today":
                    date = dt.now()
                    date = date.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%d.%m.%Y')
                elif date == "Yesterday":
                    date = dt.now() - timedelta(days=1)
                    date = date.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%d.%m.%Y')
                else:
                    if not date.split(".")[-1]:
                        date += str(dt.now().year)

                match_info = [
                    self.transform_odds_date(date),
                    home_team,
                    int(home_score),
                    float(home_odds),
                    away_team,
                    int(away_score),
                    float(away_odds),
                    float(draw_odds),
                ]
                self.bet_explorer_season.append(match_info)
                total_games += 1
            except Exception as e:
                continue
