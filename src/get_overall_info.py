import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

from utils.file import save_json

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

for season in range(start_season, end_season + 1):
    scrapper_service = ScrapperService(
        season=season,
        single_year_season=single_year_season,
        fbref_league_id=fbref_league_id,
    )

    scrapper_service.start_driver()
    teams_overall_info, players_overall_info = scrapper_service.fbref_overall_scrapper()

    scrapper_service.close_driver()

    mysql_service = MySQLService()

    teams_pk = ["Team", "Season"]
    players_pk = ["Season", "Name", "Team"]

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
