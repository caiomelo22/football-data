from services.mysql import MySQLService
from services.scrapper.nowgoal import NowGoalScrapperService
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

create_nowgoal_matches_table = True

scrapper = NowGoalScrapperService()

scrapper.start_driver()

matches_data_df = scrapper.scrape_data(season_str="2024-2025", league_id=36)

scrapper.close_driver()

mysql_service = MySQLService()

if create_nowgoal_matches_table:
    pk_cols = ["season", "round", "home_team", "away_team"]
    mysql_service.create_table_from_df("nowgoal_matches", matches_data_df, pk_cols)

data_list = matches_data_df.to_dict(orient="records")

mysql_service.insert_multiple_rows("nowgoal_matches", data_list)

mysql_service.close()
