import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

from utils.helper_functions import insert_matches

# Load environment variables from the .env file
load_dotenv()

season = 2024

# DB data
matches_table = "matches_v2"
advanced_stats_table = "matches_v2_advanced_stats"

# General infos
leagues_to_refresh = [
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 11,
        "league": "serie-a",
        "country": "italy",
        "nowgoal_league_id": 34,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 32,
        "league": "liga-portugal",
        "country": "portugal",
        "nowgoal_league_id": 23,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 9,
        "league": "premier-league",
        "country": "england",
        "nowgoal_league_id": 36,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 10,
        "league": "championship",
        "country": "england",
        "nowgoal_league_id": 37,
    },
    {
        "single_year_season": True,
        "include_advanced_stats": False,
        "fbref_league_id": 22,
        "league": "mls",
        "country": "usa",
        "nowgoal_league_id": 21,
    },
    {
        "single_year_season": True,
        "include_advanced_stats": False,
        "fbref_league_id": 25,
        "league": "j1-league",
        "country": "japan",
        "nowgoal_league_id": None,
    },
    {
        "single_year_season": True,
        "include_advanced_stats": False,
        "fbref_league_id": 29,
        "league": "allsvenskan",
        "country": "sweden",
        "nowgoal_league_id": 26,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 13,
        "league": "ligue-1",
        "country": "france",
        "nowgoal_league_id": 11,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 23,
        "league": "eredivisie",
        "country": "netherlands",
        "nowgoal_league_id": 16,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 12,
        "league": "laliga",
        "country": "spain",
        "nowgoal_league_id": 31,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 20,
        "league": "bundesliga",
        "country": "germany",
        "nowgoal_league_id": 8,
    },
]

for league in leagues_to_refresh:
    print("=" * 50)
    print(f"\nBegan processing league {league['country']} - {league['league']}")

    scrapper_service = ScrapperService(
        season=season,
        single_year_season=league["single_year_season"],
        fbref_league_id=league["fbref_league_id"],
        country=league["country"],
        league=league["league"],
        include_advanced_stats=league["include_advanced_stats"],
        nowgoal_league_id=league["nowgoal_league_id"],
    )

    full_data_df = scrapper_service.scrape_full_data()

    advanced_stats_df = (
        scrapper_service.advanced_stats_df if league["include_advanced_stats"] else None
    )

    insert_matches(
        matches_table=matches_table,
        advanced_stats_table=advanced_stats_table,
        data_df=full_data_df,
        advanced_stats_df=advanced_stats_df,
    )
