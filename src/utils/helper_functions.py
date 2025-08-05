import typing as t
import pandas as pd

from services.mysql.service import MySQLService


def get_season_str(single_year_season: bool, season: t.Optional[int]) -> str:
    if season is None:
        return ""
    elif single_year_season:
        return f"{season}"
    else:
        return f"{season}-{season+1}"


def insert_matches(
    matches_table: str,
    advanced_stats_table: str,
    data_df: pd.DataFrame,
    create_matches_table: bool = False,
    advanced_stats_df: t.Optional[pd.DataFrame] = None,
) -> None:
    mysql_service = MySQLService()

    pk_cols = ["date", "home_team", "away_team"]

    if create_matches_table:
        mysql_service.create_table_from_df(matches_table, data_df, pk_cols)

    data_list = data_df.to_dict(orient="records")

    mysql_service.insert_multiple_rows(matches_table, data_list, pk_cols)

    if advanced_stats_df is not None:
        if create_matches_table:
            mysql_service.create_table_from_df(
                advanced_stats_table, advanced_stats_df, pk_cols
            )

        advanced_stats_data_list = advanced_stats_df.to_dict(orient="records")

        mysql_service.insert_multiple_rows(
            advanced_stats_table, advanced_stats_data_list, pk_cols
        )

    mysql_service.close()
