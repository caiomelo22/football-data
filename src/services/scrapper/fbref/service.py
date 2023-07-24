import time
import pandas as pd
from selenium.webdriver.common.by import By
from .stats_helper import selected_stats
from ..mixins import DriverMixin


class FbrefScrapperService(DriverMixin):
    def __init__(self, league, league_id, start_season, end_season, single_year_season):
        DriverMixin.__init__(
            self,
            start_season=start_season,
            end_season=end_season,
            single_year_season=single_year_season,
        )
        self.fbref_league_id = league_id
        self.fbref_league = league

    def get_teams_squad_id(self, home_td_index, tds):
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
            tds[home_td_index + 4]
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
            .split("/")[squad_id_index]
        )
        return home_squad_id, away_squad_id

    def fbref_scrapper(self):
        self.fbref_seasons = dict()
        self.fbref_squad_ids = dict()

        for season in range(self.start_season, self.end_season):
            self.fbref_seasons[season] = []
            self.fbref_squad_ids[season] = []
            season_str = (
                str(season) if self.single_year_season else f"{season}-{season+1}"
            )

            url = f"https://fbref.com/en/comps/{self.fbref_league_id}/{season_str}/schedule/{self.fbref_league}-Scores-and-Fixtures"
            self.driver.get(url)

            fb = self.driver.find_element(By.CLASS_NAME, "fb")
            rows = fb.find_elements(By.XPATH, "//table/tbody/tr")

            total_games = 0
            for i, r in enumerate(rows):
                print(f"{season}/{self.end_season-1} {i}/{len(rows)}")
                if not r.text:
                    continue
                tds = r.find_elements(By.XPATH, ".//child::td")
                week = r.find_element(By.XPATH, ".//child::th").text

                if len(tds) == 12:
                    (
                        date,
                        _,
                        home_team,
                        home_xg,
                        score,
                        away_xg,
                        away_team,
                        _,
                        _,
                        _,
                        _,
                        _,
                    ) = [t.text for t in tds]
                    home_squad_id, away_squad_id = self.get_teams_squad_id(2, tds)
                elif len(tds) == 13:
                    (
                        _,
                        date,
                        _,
                        home_team,
                        home_xg,
                        score,
                        away_xg,
                        away_team,
                        _,
                        _,
                        _,
                        _,
                        _,
                    ) = [t.text for t in tds]
                    home_squad_id, away_squad_id = self.get_teams_squad_id(3, tds)
                elif len(tds) == 14:
                    (
                        _,
                        _,
                        date,
                        _,
                        home_team,
                        home_xg,
                        score,
                        away_xg,
                        away_team,
                        _,
                        _,
                        _,
                        _,
                        _,
                    ) = [t.text for t in tds]
                    home_squad_id, away_squad_id = self.get_teams_squad_id(4, tds)
                else:
                    continue

                if not score:
                    continue
                self.fbref_squad_ids[season].extend(
                    [(home_squad_id, home_team), (away_squad_id, away_team)]
                )
                home_score, away_score = score.split("–")
                try:
                    match_info = [
                        date,
                        week,
                        home_team,
                        float(home_xg),
                        int(home_score),
                        int(away_score),
                        float(away_xg),
                        away_team,
                    ]
                except ValueError:
                    continue
                self.fbref_seasons[season].append(match_info)
                total_games += 1

            self.fbref_squad_ids[season] = set(self.fbref_squad_ids[season])

    def get_value(self, attr, tds, cols):
        col_index = cols.index(attr)
        return tds[col_index - 1].text

    def save_game_stats(
        self, season, team, opp_team, date, venue, stats, cols, games_dict
    ):
        if venue == "Home":
            home_team, away_team = team, opp_team
            prefixed_cols = ["home_" + col for col in cols]
        else:
            away_team, home_team = team, opp_team
            prefixed_cols = ["away_" + col for col in cols]

        stats_dict = {col: stat for col, stat in zip(prefixed_cols, stats)}
        game_key = (home_team, away_team, date)
        if game_key in games_dict[season]:
            games_dict[season][game_key].update(stats_dict)
        else:
            games_dict[season][game_key] = stats_dict

    def fbref_advanced_stats_scrapper(self):
        self.games_stats_dict = {}

        for season in range(self.start_season, self.end_season):
            self.games_stats_dict[season] = {}
            for squad_idx, si in enumerate(self.fbref_squad_ids[season]):
                squad_id, team_name = si
                for stat_type in selected_stats.keys():
                    print(
                        f"{season}/{self.end_season-1} {squad_idx}/{len(self.fbref_squad_ids[season])} --> {team_name}:{stat_type}"
                    )
                    season_str = (
                        str(season)
                        if self.single_year_season
                        else f"{season}-{season+1}"
                    )
                    url = f"https://fbref.com/en/squads/{squad_id}/{season_str}/matchlogs/c{self.fbref_league_id}/{stat_type}"
                    self.driver.get(url)

                    rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                    thead = self.driver.find_elements(By.XPATH, "//table/thead/tr")[1]
                    cols = thead.find_elements(By.XPATH, ".//child::th")
                    cols = [c.text for c in cols]

                    for i, r in enumerate(rows):
                        if not r.text:
                            continue
                        tds = r.find_elements(By.XPATH, ".//child::td")
                        if not len(tds):
                            continue
                        date = r.find_element(By.XPATH, ".//child::th").text

                        opp_team = self.get_value("Opponent", tds, cols)
                        venue = self.get_value("Venue", tds, cols)

                        stats = []
                        for stat_col in selected_stats[stat_type]:
                            stats.append(float(self.get_value(stat_col, tds, cols) or 0))

                        self.save_game_stats(
                            season,
                            team_name,
                            opp_team,
                            date,
                            venue,
                            stats,
                            selected_stats[stat_type],
                            self.games_stats_dict,
                        )

                    time.sleep(6)

    def complete_stats(self, season, game_stats, reg_cols):
        reg_dict = {col: stat for col, stat in zip(reg_cols, game_stats)}
        game_key = (reg_dict["home_team"], reg_dict["away_team"], reg_dict["date"])
        advanced_stats_dict = self.games_stats_dict[season][game_key]
        game_dict = {**reg_dict, **advanced_stats_dict}
        return game_dict

    def combine_fbref_stats(self):
        for season in self.fbref_seasons.keys():
            print(
                f"Total games in the {season} season:", len(self.fbref_seasons[season])
            )

            columns = [
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
                self.complete_stats(season, game_stats, columns)
                for game_stats in self.fbref_seasons[season]
            ]

            self.fbref_seasons[season] = pd.DataFrame(complete_games)
