from datetime import timedelta
import pandas as pd
from .bet_explorer import BetExplorerScrapperService
from .fbref import FbrefScrapperService
from thefuzz import fuzz


class ScrapperService(FbrefScrapperService, BetExplorerScrapperService):
    def __init__(
        self,
        start_season,
        end_season,
        single_year_season,
        fbref_league,
        fbref_league_id,
        be_stage,
        be_country,
        be_league,
    ):
        # Call the constructors of parent classes explicitly
        FbrefScrapperService.__init__(
            self,
            fbref_league,
            fbref_league_id,
            start_season,
            end_season,
            single_year_season,
        )
        BetExplorerScrapperService.__init__(
            self,
            be_country,
            be_league,
            be_stage,
            start_season,
            end_season,
            single_year_season,
        )

    def set_fuzz_score(self, home_team, away_team, row):
        home_score = fuzz.ratio(row["home_team"], home_team)
        away_score = fuzz.ratio(row["away_team"], away_team)
        return home_score + away_score

    def match_seasons_data(self):
        for season in self.bet_explorer_seasons.keys():
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
            odds_df = pd.DataFrame(self.bet_explorer_seasons[season], columns=columns)

            fbref_season = self.fbref_seasons[season]
            fbref_season["date"] = pd.to_datetime(fbref_season["date"])

            fbref_season["home_odds"] = None
            fbref_season["away_odds"] = None
            fbref_season["draw_odds"] = None

            for i, row in fbref_season.iterrows():
                print(f"{season}/{self.end_season-1} : {i}/{len(fbref_season)}")

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

                    fbref_season.at[i, "home_odds"] = match["home_odds"]
                    fbref_season.at[i, "away_odds"] = match["away_odds"]
                    fbref_season.at[i, "draw_odds"] = match["draw_odds"]

                except:
                    continue

            self.fbref_seasons[season] = fbref_season