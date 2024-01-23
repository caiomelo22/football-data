import pandas as pd
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = False
start_season = 2021
end_season = 2023

# Fbref info
fbref_league_id = 9

# BetExplorer info
bet_explorer_league = "premier-league"
bet_explorer_country = "england"
bet_explorer_stage = ""

scrapper_service = ScrapperService(
    start_season=start_season,
    end_season=end_season,
    single_year_season=single_year_season,
    fbref_league_id=fbref_league_id,
    be_country=bet_explorer_country,
    be_league=bet_explorer_league,
    be_stage=bet_explorer_stage,
)

scrapper_service.start_driver()
scrapper_service.fbref_scrapper()
scrapper_service.fbref_advanced_stats_scrapper()
scrapper_service.combine_fbref_stats()

scrapper_service.bet_explorer_scrapper()
scrapper_service.close_driver()

scrapper_service.match_seasons_data()

mysql_service = MySQLService()
first_season = next(iter(scrapper_service.fbref_seasons))
mysql_service.create_table_from_df("matches", scrapper_service.fbref_seasons[first_season])

for season in scrapper_service.fbref_seasons:
    data_list = scrapper_service.fbref_seasons[season].to_dict(orient="records")
    mysql_service.insert_multiple_rows("matches", data_list)
    
mysql_service.close()