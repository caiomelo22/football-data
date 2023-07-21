from services import ScrapperService

# General info
single_year_season = True
start_season = 2023
end_season = 2024

# Fbref info
fbref_league = "Serie-A"
fbref_league_id = 24

# BetExplorer info
bet_explorer_league = "serie-a"
bet_explorer_country = "brazil"
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

scrapper_service.fbref_scrapper()
scrapper_service.fbref_advanced_stats_scrapper()

scrapper_service.bet_explorer_scrapper()

scrapper_service.match_seasons_data()
print(scrapper_service.fbref_seasons[2023])
