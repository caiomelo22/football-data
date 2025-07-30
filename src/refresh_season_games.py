import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

season = 2024

# General infos
leagues_to_refresh = [
    {
        "single_year_season": True,
        "include_advanced_stats": False,
        "fbref_league_id": 22,
        "league": "mls",
        "country": "usa",
        "nowgoal_league_id": None,
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
        "nowgoal_league_id": None,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 13,
        "league": "ligue-1",
        "country": "france",
        "nowgoal_league_id": None,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 23,
        "league": "eredivisie",
        "country": "netherlands",
        "nowgoal_league_id": None,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 12,
        "league": "laliga",
        "country": "spain",
        "nowgoal_league_id": None,
    },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 20,
        "league": "bundesliga",
        "country": "germany",
        "nowgoal_league_id": None,
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

    mysql_service = MySQLService()

    data_list = full_data_df.to_dict(orient="records")
    mysql_service.insert_multiple_rows("matches", data_list)

    mysql_service.close()
