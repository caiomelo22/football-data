from datetime import datetime as dt
from selenium.webdriver.common.by import By

from ..mixins import DriverMixin


class BetExplorerScrapperService(DriverMixin):
    def __init__(
        self, country, league, stage, start_season, end_season, single_year_season
    ):
        DriverMixin.__init__(
            self,
            start_season=start_season,
            end_season=end_season,
            single_year_season=single_year_season,
        )
        self.stage = stage
        self.bet_explorer_country = country
        self.bet_explorer_league = league

    def transform_odds_date(self, date):
        return dt.strptime(date, "%d.%m.%Y")

    def bet_explorer_scrapper(self):
        self.bet_explorer_seasons = dict()

        for season in range(self.start_season, self.end_season):
            self.bet_explorer_seasons[season] = []

            if self.single_year_season:
                season_str = f"-{season}" if season != 2023 else ""
            else:
                season_str = f"-{season}-{season+1}" if season != 2022 else ""
            url = f"https://www.betexplorer.com/football/{self.bet_explorer_country}/{self.bet_explorer_league}{season_str}/results/"
            self.driver.get(url)

            self.driver.maximize_window()

            try:
                if self.stage:
                    btn = self.driver.find_element(
                        By.XPATH, f"//*[contains(text(), '{self.stage}')]"
                    )
                    btn.click()
            except:
                pass

            table = self.driver.find_element(
                By.XPATH, '//*[@id="js-leagueresults-all"]/div/div/table'
            )
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            total_games = 0
            for i, r in enumerate(rows):
                print(f"{season}/{self.end_season-1} {i}/{len(rows)}")
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
                    self.bet_explorer_seasons[season].append(match_info)
                    total_games += 1
                except Exception as e:
                    continue
