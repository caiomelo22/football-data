from datetime import timedelta
import pandas as pd

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
            self,
        )

    def scrape_full_data(self) -> pd.DataFrame:
        self.start_driver()
        self.fbref_scrapper()

        if self.include_advanced_stats:
            self.fbref_advanced_stats_scrapper()

        self.combine_fbref_stats()

        # if bet_explorer_hide_last_season_str and season == end_season:
        #     self.bet_explorer_scrapper(hide_last_season_str=True)
        # else:
        #     self.bet_explorer_scrapper()

        self.close_driver()

        self.match_seasons_data()

        return self.fbref_season

    def set_fuzz_score(self, home_team, away_team, row):
        home_score = fuzz.ratio(row["home_team"], home_team)
        away_score = fuzz.ratio(row["away_team"], away_team)
        return home_score + away_score

    def match_seasons_data(self):
        columns = [
            "date",
            "home_team",
            "home_score",
            "home_odds",
            "away_team",
            "away_score",
            "away_odds",
            "draw_odds",
        ]
        odds_df = pd.DataFrame(self.bet_explorer_season, columns=columns)

        self.fbref_season["date"] = pd.to_datetime(self.fbref_season["date"])

        self.fbref_season["home_odds"] = None
        self.fbref_season["away_odds"] = None
        self.fbref_season["draw_odds"] = None

        print("Matching seasons data:")

        for i in tqdm(range(len(self.fbref_season))):
            row = self.fbref_season.iloc[i]

            try:
                plus_one_day = odds_df["date"] + timedelta(days=1)
                minus_one_day = odds_df["date"] - timedelta(days=1)
                same_date_matches = odds_df[
                    (odds_df["date"] == row["date"])
                    | (minus_one_day == row["date"])
                    | (plus_one_day == row["date"])
                ].reset_index(drop=True)
                same_date_matches["matchup_score"] = same_date_matches.apply(
                    lambda x: self.set_fuzz_score(
                        row["home_team"], row["away_team"], x
                    ),
                    axis=1,
                )
                same_date_matches = same_date_matches.sort_values(
                    by="matchup_score", ascending=False
                ).reset_index(drop=True)
                match = same_date_matches.iloc[0]

                self.fbref_season.at[i, "home_odds"] = match["home_odds"]
                self.fbref_season.at[i, "away_odds"] = match["away_odds"]
                self.fbref_season.at[i, "draw_odds"] = match["draw_odds"]

            except:
                continue

        self.fbref_season.rename(
            columns=lambda x: x.replace(":", "_")
            .replace("%", "_pct")
            .replace("-", "_")
            .replace("/", "_"),
            inplace=True,
        )
