default_stats_dict = {
    "shooting": [
        "Sh",
        "SoT",
        "SoT%",
        "G/Sh",
        "G/SoT",
        "Dist",
        "npxG",
        "npxG/Sh",
        "G-xG",
        "np:G-xG",
    ],
    "passing_types": ["Att", "Cmp", "TB", "Sw", "Crs", "CK"],
    "gca": ["SCA"],
    "possession": ["Att", "Succ", "Succ%"],
    "defense": [
        "Tkl",
        "TklW",
    ],
    "misc": [
        "Fls",
        "Fld",
        "Off",
        "PKwon",
        "PKcon",
        "OG",
        "Recov",
        "CrdY",
        "CrdR",
    ],
}

selected_stats = {
    **default_stats_dict,
    "keeper": ["SoTA", "Saves", "Save%", "CS", "PKatt", "PKA", "PKsv", "PKm"],
}

overall_stats = {
    **default_stats_dict,
    "stats": [
        "MP",
        "Starts",
        "Min",
        "90s",
        "Gls",
        "Ast",
        "PK",
        "PKatt",
        "xG",
    ],
    "keepers": ["SoTA", "Saves", "Save%", "CS", "PKatt", "PKA", "PKsv", "PKm"],
}
