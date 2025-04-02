import numpy as np
from services import ScrapperService, MySQLService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

season = 2024

# General infos
leagues_to_refresh = [
    # {
    #     "single_year_season": True,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 22,
    #     "bet_explorer_league": "mls",
    #     "bet_explorer_country": "usa",
    #     "bet_explorer_stage": "Main",
    # },
    # {
    #     "single_year_season": True,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 25,
    #     "bet_explorer_league": "j1-league",
    #     "bet_explorer_country": "japan",
    #     "bet_explorer_stage": "Main",
    # },
    # {
    #     "single_year_season": True,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 29,
    #     "bet_explorer_league": "allsvenskan",
    #     "bet_explorer_country": "sweden",
    #     "bet_explorer_stage": "Main",
    # },
    # {
    #     "single_year_season": False,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 13,
    #     "bet_explorer_league": "ligue-1",
    #     "bet_explorer_country": "france",
    #     "bet_explorer_stage": "Main",
    # },
    # {
    #     "single_year_season": False,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 23,
    #     "bet_explorer_league": "eredivisie",
    #     "bet_explorer_country": "netherlands",
    #     "bet_explorer_stage": "Main",
    # },
    {
        "single_year_season": False,
        "include_advanced_stats": False,
        "fbref_league_id": 12,
        "bet_explorer_league": "laliga",
        "bet_explorer_country": "spain",
        "bet_explorer_stage": "Main",
    },
    # {
    #     "single_year_season": False,
    #     "include_advanced_stats": False,
    #     "fbref_league_id": 20,
    #     "bet_explorer_league": "bundesliga",
    #     "bet_explorer_country": "germany",
    #     "bet_explorer_stage": None,
    # },
]

for league in leagues_to_refresh:
    print("=" * 50)
    print(f"\nBegan processing league {league['bet_explorer_country']} - {league['bet_explorer_league']}")
    scrapper_service = ScrapperService(
        season=season,
        single_year_season=league["single_year_season"],
        fbref_league_id=league["fbref_league_id"],
        be_country=league["bet_explorer_country"],
        be_league=league["bet_explorer_league"],
        be_stage=league["bet_explorer_stage"],
    )

    scrapper_service.start_driver()
    scrapper_service.fbref_scrapper(league["include_advanced_stats"])

    if league["include_advanced_stats"]:
        scrapper_service.fbref_advanced_stats_scrapper()
    
    scrapper_service.combine_fbref_stats()

    scrapper_service.bet_explorer_scrapper(hide_last_season_str=True)

    scrapper_service.close_driver()

    scrapper_service.match_seasons_data()

    mysql_service = MySQLService()

    data_list = scrapper_service.fbref_season.to_dict(orient="records")
    mysql_service.insert_multiple_rows("matches", data_list)
        
    mysql_service.close()