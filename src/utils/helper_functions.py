def get_season_str(single_year_season: bool, season: int) -> str:
    if single_year_season:
        return f"{season}"
    else:
        return f"{season}-{season+1}"
