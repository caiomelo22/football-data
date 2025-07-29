import numpy as np
from services import MySQLService, FbrefScrapperService
from dotenv import load_dotenv

from utils.file import save_json
from utils.helper_functions import get_season_str

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = True
include_advanced_stats = True
create_matches_table = True
start_season = 2025
end_season = 2025

# Fbref info
fbref_league_id = 24
country = "brazil"
league = "serie-a"

for season in range(start_season, end_season + 1):
    season_str = get_season_str(single_year_season, season)

    scrapper_service = FbrefScrapperService(
        season_str=season_str,
        fbref_league_id=fbref_league_id,
        country=country,
        league=league,
    )

    scrapper_service.start_driver()
    teams_overall_info, players_overall_info = scrapper_service.fbref_overall_scrapper()

    scrapper_service.close_driver()

    mysql_service = MySQLService()

    teams_pk = ["Team", "Season", "League"]
    players_pk = ["Season", "Name", "Team", "League"]

    if create_matches_table and season == start_season:
        mysql_service.create_table_from_df(
            "overall_teams", teams_overall_info, teams_pk
        )
        mysql_service.create_table_from_df(
            "overall_players", players_overall_info, players_pk
        )

    teams_overall_data_list = teams_overall_info.to_dict(orient="records")
    players_overall_data_list = players_overall_info.to_dict(orient="records")

    mysql_service.insert_multiple_rows(
        "overall_teams", teams_overall_data_list, teams_pk
    )
    mysql_service.insert_multiple_rows(
        "overall_players", players_overall_data_list, players_pk
    )

    mysql_service.close()
