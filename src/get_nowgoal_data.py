import typing as t
from services.mysql import MySQLService
from services.scrapper.nowgoal import NowGoalScrapperService
from dotenv import load_dotenv
import pandas as pd

from utils.helper_functions import get_league_str


def create_mysql_nowgoal_matches_table(
    matches_data_df: pd.DataFrame, pk_cols: t.List[str]
) -> None:
    mysql_service = MySQLService()

    mysql_service.create_table_from_df("nowgoal_matches", matches_data_df, pk_cols)

    mysql_service.close()


def insert_nowgoal_matches(matches_data_df: pd.DataFrame, pk_cols: t.List[str]) -> None:
    mysql_service = MySQLService()

    data_list = matches_data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows("nowgoal_matches", data_list, pk_cols)

    mysql_service.close()


# Load environment variables from the .env file
load_dotenv()

first_season = 2012
last_season = 2025

league_id = 36
league = "premier-league"
country = "england"

create_nowgoal_matches_table = True
single_year_season = False

for season in range(first_season, last_season):
    if single_year_season:
        season_str = f"{season}"
    else:
        season_str = f"{season}-{season+1}"

    print(f"Fetching data for the {season_str} season...")

    scrapper_service = NowGoalScrapperService(
        nowgoal_league_id=league_id, season_str=season_str
    )

    scrapper_service.start_driver()

    scrapper_service.nowgoal_scrapper()

    pk_cols = ["date", "home_team", "away_team"]

    scrapper_service.nowgoal_data_df["league"] = get_league_str(country, league)

    if create_nowgoal_matches_table and season == first_season:
        create_mysql_nowgoal_matches_table(scrapper_service.nowgoal_data_df, pk_cols)

    insert_nowgoal_matches(scrapper_service.nowgoal_data_df, pk_cols)

    scrapper_service.close_driver()
