import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from .stats_helper import selected_stats
from ..mixins import DriverMixin
from tqdm import tqdm


class FbrefScrapperService(DriverMixin):
    def __init__(self, league, league_id, season, single_year_season):
        DriverMixin.__init__(
            self,
            season=season,
            single_year_season=single_year_season,
        )
        self.fbref_league_id = league_id
        self.fbref_league = league
        self.games_stats_dict = {}

    def get_teams_squad_id(self, home_td_index, away_td_index, tds):
        if (
            len(
                tds[home_td_index]
                .find_element(By.TAG_NAME, "a")
                .get_attribute("href")
                .split("/")
            )
            > 7
        ):
            squad_id_index = -3
        else:
            squad_id_index = -2
        home_squad_id = (
            tds[home_td_index]
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
            .split("/")[squad_id_index]
        )
        away_squad_id = (
            tds[away_td_index]
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
            .split("/")[squad_id_index]
        )
        return home_squad_id, away_squad_id

    def parse_score(self, score_string):
        # Pattern to match scores with optional penalty shootouts
        match = re.match(r"(?:\(\d+\) )?(\d+)[–-](\d+)(?: \(\d+\))?", score_string)

        if match:
            # Extract the main scores
            home_score = int(match.group(1))
            away_score = int(match.group(2))

            return home_score, away_score
        else:
            raise ValueError("Invalid score format")

    def fbref_scrapper(self, include_advanced_stats):
        self.fbref_season = []
        self.fbref_squad_ids = []

        season_str = (
            str(self.season)
            if self.single_year_season
            else f"{self.season}-{self.season+1}"
        )

        url = f"https://fbref.com/en/comps/{self.fbref_league_id}/{season_str}/schedule/Scores-and-Fixtures"
        self.driver.get(url)

        fb = self.driver.find_element(By.CLASS_NAME, "fb")

        head = fb.find_element(By.XPATH, "//table/thead/tr")
        ths = head.find_elements(By.XPATH, ".//child::th")

        home_xg, away_xg = None, None
        date_idx, home_team_idx, score_idx, away_team_idx, home_xg_idx, away_xg_idx = (
            None,
            None,
            None,
            None,
            None,
            None,
        )

        for th_idx in range(len(ths)):
            if ths[th_idx].text == "Date":
                date_idx = th_idx - 1
            elif ths[th_idx].text == "Home":
                home_team_idx = th_idx - 1
            elif ths[th_idx].text == "Score":
                score_idx = th_idx - 1
            elif ths[th_idx].text == "Away":
                away_team_idx = th_idx - 1
            elif ths[th_idx].get_attribute("data-stat") == "home_xg":
                home_xg_idx = th_idx - 1
            elif ths[th_idx].get_attribute("data-stat") == "away_xg":
                away_xg_idx = th_idx - 1

        rows = fb.find_elements(By.XPATH, "//table/tbody/tr")

        total_games = 0

        print("Scrapping info from the fbref website:")
        for i in tqdm(range(len(rows))):
            r = rows[i]
            if not r.text:
                continue

            try:
                tds = r.find_elements(By.XPATH, ".//child::td")
                week = r.find_element(By.XPATH, ".//child::th").text

                score = tds[score_idx].text
                if not score:
                    continue

                home_score, away_score = self.parse_score(score)

                date = tds[date_idx].text
                home_team = tds[home_team_idx].text
                away_team = tds[away_team_idx].text

                if home_xg_idx is not None:
                    home_xg = tds[home_xg_idx].text

                if away_xg_idx is not None:
                    away_xg = tds[away_xg_idx].text

                if include_advanced_stats:
                    home_squad_id, away_squad_id = self.get_teams_squad_id(
                        home_team_idx, away_team_idx, tds
                    )
                    self.fbref_squad_ids.extend(
                        [(home_squad_id, home_team), (away_squad_id, away_team)]
                    )
            except:
                continue

            try:
                match_info = [
                    self.season,
                    self.fbref_league.lower(),
                    date,
                    week,
                    home_team,
                    float(home_xg) if home_xg is not None else None,
                    home_score,
                    away_score,
                    float(away_xg) if away_xg is not None else None,
                    away_team,
                ]
            except ValueError:
                continue

            self.fbref_season.append(match_info)
            total_games += 1

        if include_advanced_stats:
            self.fbref_squad_ids = set(self.fbref_squad_ids)

    def get_value(self, attr, tds, cols):
        col_index = cols.index(attr)
        return tds[col_index - 1].text

    def save_game_stats(self, team, opp_team, date, venue, stats, cols, games_dict):
        if venue == "Home":
            home_team, away_team = team, opp_team
            prefixed_cols = ["home_" + col for col in cols]
        else:
            away_team, home_team = team, opp_team
            prefixed_cols = ["away_" + col for col in cols]

        stats_dict = {col: stat for col, stat in zip(prefixed_cols, stats)}
        game_key = (home_team, away_team, date)
        if game_key in games_dict:
            games_dict[game_key].update(stats_dict)
        else:
            games_dict[game_key] = stats_dict

    def fbref_advanced_stats_scrapper(self):
        self.games_stats_dict = {}

        for squad_idx, si in enumerate(self.fbref_squad_ids):
            squad_id, team_name = si

            for stat_type in selected_stats.keys():
                print(
                    f"{self.season} {squad_idx}/{len(self.fbref_squad_ids)} --> {team_name}:{stat_type}"
                )
                season_str = (
                    str(self.season)
                    if self.single_year_season
                    else f"{self.season}-{self.season+1}"
                )

                url = f"https://fbref.com/en/squads/{squad_id}/{season_str}/matchlogs/c{self.fbref_league_id}/{stat_type}"
                self.driver.get(url)

                try:
                    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                    thead = self.driver.find_elements(By.XPATH, "//table/thead/tr")[1]
                    cols = thead.find_elements(By.XPATH, ".//child::th")
                    cols = [c.text for c in cols]
                except:
                    print(f"Error when fetching {stat_type} info for {team_name}")
                    continue

                for _, r in enumerate(rows):
                    if not r.text:
                        continue

                    tds = r.find_elements(By.XPATH, ".//child::td")

                    if not len(tds):
                        continue

                    try:
                        date = r.find_element(By.XPATH, ".//child::th").text
                    except:
                        continue

                    opp_team = self.get_value("Opponent", tds, cols)
                    venue = self.get_value("Venue", tds, cols)

                    stats = []
                    for stat_col in selected_stats[stat_type]:
                        stats.append(float(self.get_value(stat_col, tds, cols) or 0))

                    self.save_game_stats(
                        team_name,
                        opp_team,
                        date,
                        venue,
                        stats,
                        selected_stats[stat_type],
                        self.games_stats_dict,
                    )

                time.sleep(6)

    def complete_stats(self, game_stats, reg_cols):
        reg_dict = {col: stat for col, stat in zip(reg_cols, game_stats)}
        game_key = (reg_dict["home_team"], reg_dict["away_team"], reg_dict["date"])

        if self.games_stats_dict:
            advanced_stats_dict = self.games_stats_dict.get(game_key, {})
        else:
            advanced_stats_dict = dict()

        game_dict = {**reg_dict, **advanced_stats_dict}
        return game_dict

    def combine_fbref_stats(self):
        print(f"Total games in the {self.season} season:", len(self.fbref_season))

        columns = [
            "season",
            "league",
            "date",
            "week",
            "home_team",
            "home_xg",
            "home_score",
            "away_score",
            "away_xg",
            "away_team",
        ]
        complete_games = [
            self.complete_stats(game_stats, columns) for game_stats in self.fbref_season
        ]

        self.fbref_season = pd.DataFrame(complete_games)
