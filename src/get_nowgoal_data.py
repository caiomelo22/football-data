from services.mysql import MySQLService
from services.scrapper.nowgoal import NowGoalScrapperService
from dotenv import load_dotenv
import pandas as pd


def create_mysql_nowgoal_matches_table(matches_data_df: pd.DataFrame):
    pk_cols = ["season", "round", "home_team", "away_team"]
    mysql_service = MySQLService()

    mysql_service.create_table_from_df("nowgoal_matches", matches_data_df, pk_cols)

    mysql_service.close()


def insert_nowgoal_matches(matches_data_df: pd.DataFrame):
    mysql_service = MySQLService()

    data_list = matches_data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows("nowgoal_matches", data_list)

    mysql_service.close()


# Load environment variables from the .env file
load_dotenv()

first_season = 2012
last_season = 2025

league_id = 36

create_nowgoal_matches_table = True
single_year_season = False

for season in range(first_season, last_season):
    if single_year_season:
        season_str = f"{season}"
    else:
        season_str = f"{season}-{season+1}"

    print(f"Fetching data for the {season_str} season...")

    scrapper = NowGoalScrapperService(league_id=league_id, season_str=season_str)

    scrapper.start_driver()

    scrapper.nowgoal_scrapper()

    if create_nowgoal_matches_table and season == first_season:
        create_mysql_nowgoal_matches_table(scrapper.nowgoal_data_df)

    insert_nowgoal_matches(scrapper.nowgoal_data_df)

    scrapper.close_driver()
