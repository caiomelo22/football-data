from datetime import timedelta
import pandas as pd
import typing as t

from utils.helper_functions import get_season_str
from .nowgoal import NowGoalScrapperService
from .fbref import FbrefScrapperService
from thefuzz import fuzz
from tqdm import tqdm


class ScrapperService(FbrefScrapperService, NowGoalScrapperService):
    def __init__(
        self,
        season: int,
        single_year_season: bool,
        league: str,
        country: str,
        fbref_league_id: int,
        nowgoal_league_id: int,
        include_advanced_stats: bool,
    ):
        season_str = get_season_str(single_year_season, season)

        # Call the constructors of parent classes explicitly
        FbrefScrapperService.__init__(
            self,
            season_str=season_str,
            league=league,
            country=country,
            fbref_league_id=fbref_league_id,
            include_advanced_stats=include_advanced_stats,
        )
        NowGoalScrapperService.__init__(
            self, nowgoal_league_id=nowgoal_league_id, season_str=season_str
        )

        self.season = season

    def scrape_full_data(self) -> pd.DataFrame:
        self.start_driver()

        # Fetch Fbref data
        self.fbref_scrapper()

        if self.include_advanced_stats:
            self.fbref_advanced_stats_scrapper()

        self.combine_fbref_stats()

        # Fetch NowGoal data
        self.nowgoal_scrapper()

        self.close_driver()

        # Match both Fbref and NowGoal data together
        self.match_seasons_data()

        return self.fbref_data_df

    def set_fuzz_score(self, home_team: str, away_team: str, row: pd.Series) -> int:
        home_score = fuzz.ratio(row["home_team"], home_team)
        away_score = fuzz.ratio(row["away_team"], away_team)
        return home_score + away_score

    def get_nowgoal_match_by_fbref_match(self, curr_match: pd.Series) -> pd.Series:
        plus_one_day = self.nowgoal_data_df["date"] + timedelta(days=1)
        minus_one_day = self.nowgoal_data_df["date"] - timedelta(days=1)

        # Get NowGoal matches within a one day range from the Fbref match
        # Just in case of match time divergences
        same_date_matches = self.nowgoal_data_df[
            (self.nowgoal_data_df["date"] == curr_match["date"])
            | (minus_one_day == curr_match["date"])
            | (plus_one_day == curr_match["date"])
        ].reset_index(drop=True)

        # Get the teams string matchup score for each match
        same_date_matches["matchup_score"] = same_date_matches.apply(
            lambda x: self.set_fuzz_score(
                curr_match["home_team"], curr_match["away_team"], x
            ),
            axis=1,
        )

        # Select the one with the best score to merge the betting info
        same_date_matches = same_date_matches.sort_values(
            by="matchup_score", ascending=False
        ).reset_index(drop=True)

        nowgoal_match = same_date_matches.iloc[0]

        return nowgoal_match

    def get_betting_columns_from_nowgoal_df(self) -> t.List:
        betting_cols = []

        for col in self.nowgoal_data_df.columns:
            if "odds" in col or "line" in col:
                betting_cols.append(col)

        return betting_cols

    def match_seasons_data(self) -> None:
        self.fbref_data_df["date"] = pd.to_datetime(self.fbref_data_df["date"])
        self.fbref_data_df["season"] = self.season

        betting_cols = self.get_betting_columns_from_nowgoal_df()

        # Add betting cols to the Fbref DF
        for betting_col in betting_cols:
            self.fbref_data_df[betting_col] = None

        print("Matching seasons data:")

        for i in tqdm(range(len(self.fbref_data_df))):
            curr_match = self.fbref_data_df.iloc[i]

            try:
                nowgoal_match = self.get_nowgoal_match_by_fbref_match(curr_match)

                # Add betting info to the Fbref DF
                for betting_col in betting_cols:
                    self.fbref_data_df.at[i, betting_col] = nowgoal_match[betting_col]
            except:
                continue

        # Clean column naming
        self.fbref_data_df.rename(
            columns=lambda x: x.replace(":", "_")
            .replace("%", "_pct")
            .replace("-", "_")
            .replace("/", "_"),
            inplace=True,
        )
