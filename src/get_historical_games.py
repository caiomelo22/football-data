import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = True
include_advanced_stats = False
create_matches_table = False
start_season = 2025
end_season = 2025

# Fbref info
fbref_league_id = 24

# BetExplorer info
bet_explorer_league = "serie-a-betano"
bet_explorer_country = "brazil"
bet_explorer_stage = "Main"
bet_explorer_hide_last_season_str = True

for season in range(start_season, end_season + 1):
    scrapper_service = ScrapperService(
        season=season,
        single_year_season=single_year_season,
        fbref_league_id=fbref_league_id,
        country=bet_explorer_country,
        league=bet_explorer_league,
        include_advanced_stats=include_advanced_stats,
    )

    full_data_df = scrapper_service.scrape_full_data()

    mysql_service = MySQLService()

    if create_matches_table and season == start_season:
        mysql_service.create_table_from_df("matches", full_data_df)

    data_list = full_data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows("matches", data_list)

    mysql_service.close()
