import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = True
include_advanced_stats = True
create_matches_table = False
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

    print(teams_overall_info)
    print(players_overall_info)

    # scrapper_service.close_driver()

    # scrapper_service.match_seasons_data()

    # mysql_service = MySQLService()

    # if create_matches_table and season == start_season:
    #     mysql_service.create_table_from_df("matches", scrapper_service.fbref_season)

    # data_list = scrapper_service.fbref_season.to_dict(orient="records")

    # mysql_service.insert_multiple_rows("matches", data_list)
        
    # mysql_service.close()