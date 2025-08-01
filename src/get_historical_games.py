import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# General infos
single_year_season = False
include_advanced_stats = False
create_matches_table = True
start_season = 2024
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

    mysql_service = MySQLService()

    if create_matches_table and season == start_season:
        pk_cols = ["date", "league", "home_team", "away_team"]
        mysql_service.create_table_from_df(matches_table, full_data_df, pk_cols)

    data_list = full_data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows(matches_table, data_list)

    if include_advanced_stats:
        advanced_stats_df = scrapper_service.advanced_stats_df

        if create_matches_table and season == start_season:
            pk_cols = ["date", "league", "home_team", "away_team"]
            mysql_service.create_table_from_df(
                advanced_stats_table, advanced_stats_df, pk_cols
            )

        advanced_stats_data_list = advanced_stats_df.to_dict(orient="records")

        mysql_service.insert_multiple_rows(
            advanced_stats_table, advanced_stats_data_list
        )

    mysql_service.close()
