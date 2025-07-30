import typing as t


def get_season_str(single_year_season: bool, season: t.Optional[int]) -> str:
    if season is None:
        return ""
    elif single_year_season:
        return f"{season}"
    else:
        return f"{season}-{season+1}"
