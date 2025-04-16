# Intro
Project designed to gather and store data from football leagues scrapped on the betexplorer and fbref websites. This project collects stats and advanced stats from the fbref website and gathers odds info for each match on BetExplorer. In the end, it combines all of the information into your MySQL server.

# Setup
In order to run this program, you are gonna have to create a `.env` file in the root of the project. In this env file, you'll have to set the following variables to connect to your host MySQL server:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=pwd
DB_DATABASE=football-data
```

Run the pip install command in order to install the required packages.
```
>> pip install -r requirements.txt
```

# Executing
To execute the data scrapper to fetch historical games, just and run the [Get Historical Games](https://github.com/caiomelo22/football-data/blob/main/src/get_historical_games.py).

```
>> python ./src/get_historical_games.py.py
```

Or if you want to run the scrapper just for the most recent season of multiple leagues, run the [Refresh Season Games](https://github.com/caiomelo22/football-data/blob/main/src/refresh_season_games.py). There you can also choose which leagues are going to be processed.

```
>> python ./src/refresh_season_games.py
```

Now we have a new program to fetch overall stats for each team and players of a specific league. To fetch this data, just run the [Get Overall Info](https://github.com/caiomelo22/football-data/blob/main/src/get_overall_info.py).

```
>> python ./src/get_overall_info.py
```

## Customize leagues
If you want to scrape matches from different leagues, just clone the project and mess around with the different programs' global parameters. They're set based on the URI information from the sites mentioned before.

# Disclaimer
This project was made for educational purposes only. The data gathered with this project was used for private projects only, of which are not used to sell it in any way.

