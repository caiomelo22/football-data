import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = True
include_advanced_stats = False
create_matches_table = True
start_season = 2023
end_season = 2023

# Fbref info
fbref_league_id = 22

# BetExplorer info
bet_explorer_league = "mls"
bet_explorer_country = "usa"
bet_explorer_stage = "Main"
bet_explorer_hide_last_season_str = False

for season in range(start_season, end_season + 1):
    scrapper_service = ScrapperService(
        season=season,
        single_year_season=single_year_season,
        fbref_league_id=fbref_league_id,
        be_country=bet_explorer_country,
        be_league=bet_explorer_league,
        be_stage=bet_explorer_stage,
    )

    scrapper_service.start_driver()
    scrapper_service.fbref_scrapper()

    if include_advanced_stats:
        scrapper_service.fbref_advanced_stats_scrapper()
    
    scrapper_service.combine_fbref_stats()

    if bet_explorer_hide_last_season_str and season == end_season:
        scrapper_service.bet_explorer_scrapper(hide_last_season_str=True)
    else:
        scrapper_service.bet_explorer_scrapper()

    scrapper_service.close_driver()

    scrapper_service.match_seasons_data()

    mysql_service = MySQLService()

    if create_matches_table and season == start_season:
        mysql_service.create_table_from_df("matches", scrapper_service.fbref_season)

    scrapper_service.fbref_season = scrapper_service.fbref_season.replace({np.nan: 0})

    data_list = scrapper_service.fbref_season.to_dict(orient="records")
    mysql_service.insert_multiple_rows("matches", data_list)
        
    mysql_service.close()