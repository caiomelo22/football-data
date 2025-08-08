import numpy as np
from services import ScrapperService
from dotenv import load_dotenv

from utils.helper_functions import insert_matches

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = False
include_advanced_stats = False
create_matches_table = True
start_season = 2012
end_season = 2024

league = "premier-league"
country = "england"

# Fbref info
fbref_league_id = 9

# NowGoal info
nowgoal_league_id = 36

# DB data
matches_table = "matches_v2"
advanced_stats_table = "matches_v2_advanced_stats"

for season in range(start_season, end_season + 1):
    scrapper_service = ScrapperService(
        season=season,
        single_year_season=single_year_season,
        fbref_league_id=fbref_league_id,
        nowgoal_league_id=nowgoal_league_id,
        country=country,
        league=league,
        include_advanced_stats=include_advanced_stats,
    )

    full_data_df = scrapper_service.scrape_full_data()

    advanced_stats_df = (
        scrapper_service.advanced_stats_df if include_advanced_stats else None
    )

    insert_matches(
        matches_table=matches_table,
        advanced_stats_table=advanced_stats_table,
        data_df=full_data_df,
        create_matches_table=create_matches_table and season == start_season,
        advanced_stats_df=advanced_stats_df,
    )
