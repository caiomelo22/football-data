import re
import time
import pandas as pd
import typing as t
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from .stats_helper import selected_stats
from ..mixins import DriverMixin
from tqdm import tqdm


class FbrefScrapperService(DriverMixin):
    def __init__(
        self,
        season_str: str,
        fbref_league_id: str,
        country: str = None,
        league: str = None,
        include_advanced_stats: bool = False,
    ):
        DriverMixin.__init__(
            self,
        )

        self.season_str = season_str
        self.country = country
        self.league = league
        self.league_id = fbref_league_id
        self.include_advanced_stats = include_advanced_stats

    def get_teams_squad_id(
        self, home_td_index: int, away_td_index: int, tds: t.List[WebElement]
    ) -> t.Tuple[str, str]:
        # Define the squad id index based on the number of columns in the table
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

    def parse_score(self, score_string: str) -> t.Tuple[int, int]:
        # Pattern to match scores with optional penalty shootouts
        match = re.match(r"(?:\(\d+\) )?(\d+)[–-](\d+)(?: \(\d+\))?", score_string)

        if match:
            # Extract the main scores
            home_score = int(match.group(1))
            away_score = int(match.group(2))

            return home_score, away_score
        else:
            raise ValueError("Invalid score format")

    def fbref_scrapper(self) -> None:
        self.fbref_data = []
        self.fbref_squad_ids = []

        url = f"https://fbref.com/en/comps/{self.league_id}/{self.season_str}/schedule/Scores-and-Fixtures"
        self.driver.get(url)

        fb = self.driver.find_element(By.CLASS_NAME, "fb")

        head = fb.find_element(By.XPATH, "//table/thead/tr")
        ths = head.find_elements(By.XPATH, ".//child::th")

        home_xg, away_xg = None, None

        # Define the default indexes of the required data in the table
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

        matches = fb.find_elements(By.XPATH, "//table/tbody/tr")

        print("Scrapping info from the fbref website:")
        for i in tqdm(range(len(matches))):
            curr_match = matches[i]
            if not curr_match.text:
                continue

            try:
                tds = curr_match.find_elements(By.XPATH, ".//child::td")
                week = curr_match.find_element(By.XPATH, ".//child::th").text

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

                # Save the squad ids for the advanced stats scrapper afterwards
                if self.include_advanced_stats:
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

            self.fbref_data.append(match_info)

        if self.include_advanced_stats:
            self.fbref_squad_ids = set(self.fbref_squad_ids)

    def get_value(self, attr: str, tds: t.List[WebElement], cols: str) -> str:
        col_index = cols.index(attr)
        return tds[col_index - 1].text

    def save_match_stats(
        self,
        team: str,
        opp_team: str,
        date: str,
        venue: str,
        stats: t.List[float],
        cols: t.List[str],
        matches_dict: t.Dict[t.Any],
    ) -> None:
        if venue == "Home":
            home_team, away_team = team, opp_team
            prefixed_cols = ["home_" + col for col in cols]
        else:
            away_team, home_team = team, opp_team
            prefixed_cols = ["away_" + col for col in cols]

        # Save the advanced stats in the dict by the composed key (home, away, date)
        stats_dict = {col: stat for col, stat in zip(prefixed_cols, stats)}
        match_key = (home_team, away_team, date)

        if match_key in matches_dict:
            matches_dict[match_key].update(stats_dict)
        else:
            matches_dict[match_key] = stats_dict

    def fbref_advanced_stats_scrapper(self) -> None:
        self.matches_stats_dict = {}

        # Go through every squad and their respective advanced stats
        for squad_idx, si in enumerate(self.fbref_squad_ids):
            squad_id, team_name = si

            for stat_type in selected_stats.keys():
                print(
                    f"{self.season} {squad_idx}/{len(self.fbref_squad_ids)} --> {team_name}:{stat_type}"
                )

                url = f"https://fbref.com/en/squads/{squad_id}/{self.season_str}/matchlogs/c{self.league_id}/{stat_type}"
                self.driver.get(url)

                try:
                    matches = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
                    thead = self.driver.find_elements(By.XPATH, "//table/thead/tr")[1]
                    cols = thead.find_elements(By.XPATH, ".//child::th")
                    cols = [c.text for c in cols]
                except:
                    print(f"Error when fetching {stat_type} info for {team_name}")
                    continue

                for curr_match in matches:
                    if not curr_match.text:
                        continue

                    tds = curr_match.find_elements(By.XPATH, ".//child::td")

                    if not len(tds):
                        continue

                    try:
                        date = curr_match.find_element(By.XPATH, ".//child::th").text
                    except:
                        continue

                    # Get the opponent and whether the team is playing home/away
                    opp_team = self.get_value("Opponent", tds, cols)
                    venue = self.get_value("Venue", tds, cols)

                    # Get the advanced stats for the current match
                    stats = []
                    for stat_col in selected_stats[stat_type]:
                        stats.append(float(self.get_value(stat_col, tds, cols) or 0))

                    self.save_match_stats(
                        team_name,
                        opp_team,
                        date,
                        venue,
                        stats,
                        selected_stats[stat_type],
                        self.matches_stats_dict,
                    )

                time.sleep(6)

    def complete_stats(self, match_stats: dict, reg_cols: t.List[str]) -> dict:
        # Set the default dict with the base stats of the match
        reg_dict = {col: stat for col, stat in zip(reg_cols, match_stats)}
        match_key = (reg_dict["home_team"], reg_dict["away_team"], reg_dict["date"])

        # Get the advanced stats of that match based on the match_key
        if self.matches_stats_dict:
            advanced_stats_dict = self.matches_stats_dict.get(match_key, {})
        else:
            advanced_stats_dict = dict()

        # Get the full match dict
        match_dict = {**reg_dict, **advanced_stats_dict}

        return match_dict

    def get_league_str(self) -> str:
        return f"{self.country}-{self.league}"

    def combine_fbref_stats(self) -> None:
        print(f"Total matches in the {self.season} season:", len(self.fbref_data))

        columns = [
            "season",
            "date",
            "week",
            "home_team",
            "home_xg",
            "home_score",
            "away_score",
            "away_xg",
            "away_team",
        ]
        complete_matches = [
            self.complete_stats(match_stats, columns) for match_stats in self.fbref_data
        ]

        self.fbref_data_df = pd.DataFrame(complete_matches)

        self.fbref_data_df["league"] = self.get_league_str()

    def clean_sub_stat_str(self, stat: str, sub_stat: str) -> str:
        sub_stat_cleaned = (
            sub_stat.replace("-", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace("%", "Pct")
        )
        return f"{stat.capitalize()}_{sub_stat_cleaned}"

    def get_teams_overall_rows(
        self, tables: t.List[WebElement], season: int, stat: str, sub_stats: str
    ) -> pd.DataFrame:
        teams_overall_table = tables[0]

        head = teams_overall_table.find_elements(By.TAG_NAME, "tr")[1]
        ths = head.find_elements(By.TAG_NAME, "th")

        ths_dict = {th.text: th for th in ths}

        sub_stats_indexes = dict()

        ths_keys = list(ths_dict.keys())

        for sub_stat in sub_stats:
            for i in range(len(ths_keys)):
                if ths_keys[i] == sub_stat:
                    sub_stats_indexes[sub_stat] = i
                    break

        rows = teams_overall_table.find_elements(By.TAG_NAME, "tr")

        league_str = self.get_league_str()

        teams_info = list()

        for i in tqdm(range(len(rows))):
            r = rows[i]
            if not r.text:
                continue

            try:
                tds = r.find_elements(By.TAG_NAME, "td")
                th = r.find_element(By.TAG_NAME, "th")

                if len(tds) < len(sub_stats_indexes):
                    continue

                team_info = [season, league_str, th.text]  # Team

                for sub_stat_index in sub_stats_indexes.values():
                    sub_stat_value = tds[sub_stat_index - 1].text or None
                    team_info.append(sub_stat_value)

            except:
                continue

            teams_info.append(team_info)

        index_columns = ["Season", "League", "Team"]
        stats_columns = [self.clean_sub_stat_str(stat, s) for s in sub_stats]

        df = pd.DataFrame(teams_info, columns=index_columns + stats_columns)
        df.set_index(index_columns, inplace=True)

        return df

    def get_players_overall_rows(
        self, tables: t.List[WebElement], season: int, stat: str, sub_stats: t.List[str]
    ) -> pd.DataFrame:
        players_overall_table = tables[2]

        head = players_overall_table.find_elements(By.TAG_NAME, "tr")[1]
        ths = head.find_elements(By.TAG_NAME, "th")

        ths_dict = {th.text: th for th in ths}

        sub_stats_indexes = dict()

        ths_keys = list(ths_dict.keys())

        for sub_stat in sub_stats:
            for i in range(len(ths_keys)):
                if ths_keys[i] == sub_stat:
                    sub_stats_indexes[sub_stat] = i
                    break

        rows = players_overall_table.find_elements(By.TAG_NAME, "tr")

        players_info = list()

        league_str = self.get_league_str()

        for i in tqdm(range(len(rows))):
            r = rows[i]
            if not r.text:
                continue

            try:
                tds = r.find_elements(By.TAG_NAME, "td")

                if len(tds) < len(sub_stats_indexes):
                    continue

                player_info = [
                    season,
                    league_str,
                    tds[0].text,  # Name
                    tds[1].text.split(" ")[-1],  # Nation
                    tds[2].text,  # Position
                    tds[3].text,  # Team
                    tds[4].text.split("-")[0],  # Age
                ]

                for sub_stat, sub_stat_index in sub_stats_indexes.items():
                    sub_stat_value = tds[sub_stat_index - 1].text or None
                    player_info.append(sub_stat_value)

            except:
                continue

            players_info.append(player_info)

        index_columns = [
            "Season",
            "League",
            "Name",
            "Nation",
            "Position",
            "Team",
            "Age",
        ]
        stats_columns = [self.clean_sub_stat_str(stat, s) for s in sub_stats]

        df = pd.DataFrame(players_info, columns=index_columns + stats_columns)
        df.set_index(index_columns, inplace=True)

        return df

    def clean_df(self, df: pd.DataFrame) -> None:
        for col in df.columns:
            # Standardize nulls to proper NA values
            df[col].replace(
                ["", "None", "none", "NaN", "nan", None], pd.NA, inplace=True
            )

            # Try converting to numeric (non-destructive check)
            converted = pd.to_numeric(df[col], errors="ignore")

            if col == "Age":
                print(converted)
                print(df[col].notna().sum(), converted.notna().sum())

            # If all non-null values were successfully converted, update column
            if df[col].notna().sum() == converted.notna().sum():
                df[col] = converted

        df.reset_index(drop=False, inplace=True)

    def fbref_overall_scrapper(self) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
        teams_overall_info = None
        players_overall_info = None

        for stat, sub_stats in selected_stats.items():
            print(f"Scrapping {stat} data...")

            url = f"https://fbref.com/en/comps/{self.league_id}/{self.season_str}/{stat}/Stats"

            self.driver.get(url)

            fb = self.driver.find_element(By.CLASS_NAME, "fb")

            tables = fb.find_elements(By.CLASS_NAME, "stats_table")

            teams_stats_overall_info = self.get_teams_overall_rows(
                tables, self.season_str, stat, sub_stats
            )
            players_stats_overall_info = self.get_players_overall_rows(
                tables, self.season_str, stat, sub_stats
            )

            if teams_overall_info is None:
                teams_overall_info = teams_stats_overall_info
                players_overall_info = players_stats_overall_info
            else:
                teams_overall_info = pd.concat(
                    [teams_overall_info, teams_stats_overall_info], axis=1
                )
                players_overall_info = pd.concat(
                    [players_overall_info, players_stats_overall_info], axis=1
                )

        self.clean_df(teams_overall_info)
        self.clean_df(players_overall_info)

        return teams_overall_info, players_overall_info
