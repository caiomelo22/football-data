import typing as t
from services.mysql import MySQLService
from services.scrapper.bet_explorer.service import BetExplorerScrapperService
from services.scrapper.nowgoal import NowGoalScrapperService
from dotenv import load_dotenv
import pandas as pd

from utils.helper_functions import get_league_str


def create_mysql_bet_explorer_matches_table(
    matches_data_df: pd.DataFrame, pk_cols: t.List[str]
) -> None:
    mysql_service = MySQLService()

    mysql_service.create_table_from_df("bet_explorer_matches", matches_data_df, pk_cols)

    mysql_service.close()


def insert_bet_explorer_matches(
    matches_data_df: pd.DataFrame, pk_cols: t.List[str]
) -> None:
    mysql_service = MySQLService()

    data_list = matches_data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows("bet_explorer_matches", data_list, pk_cols)

    mysql_service.close()


# Load environment variables from the .env file
load_dotenv()

# General Scrapper info
first_season = 2025
last_season = 2025

create_betexplorer_matches_table = True
single_year_season = True

# BetExplorer info
league = "serie-a-betano"
country = "brazil"
bet_explorer_stage = None

for season in range(first_season, last_season + 1):
    print(f"Fetching BetExplorer data for the {season} season...")

    scrapper_service = BetExplorerScrapperService(
        country=country,
        league=league,
        stage=bet_explorer_stage,
        season=season,
        single_year_season=single_year_season,
    )

    scrapper_service.start_driver()

    scrapper_service.bet_explorer_scrapper()

    pk_cols = ["date", "home_team", "away_team"]

    scrapper_service.bet_explorer_data_df["league"] = get_league_str(country, league)
    scrapper_service.bet_explorer_data_df["season"] = season

    if create_betexplorer_matches_table and season == first_season:
        create_mysql_bet_explorer_matches_table(
            scrapper_service.bet_explorer_data_df, pk_cols
        )

    insert_bet_explorer_matches(scrapper_service.bet_explorer_data_df, pk_cols)

    scrapper_service.close_driver()
