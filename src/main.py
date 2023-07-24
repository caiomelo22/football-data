import pandas as pd
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infoss
single_year_season = True
start_season = 2023
end_season = 2024

# Fbref info
fbref_league = "Major-League-Soccer"
fbref_league_id = 22

# BetExplorer info
bet_explorer_league = "mls"
bet_explorer_country = "usa"
bet_explorer_stage = ""

scrapper_service = ScrapperService(
    start_season=start_season,
    end_season=end_season,
    single_year_season=single_year_season,
    fbref_league=fbref_league,
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