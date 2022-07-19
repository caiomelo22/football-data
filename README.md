# Football-Data
Project designed to gather, clean and store data from football leagues on the API-Football api.

# Setup
In order to run this program, you are gonna have to sign up on the [API-Football](https://www.api-football.com/pricing) website. You can sign up for free with up to 100 request a day. When you're done setting up your account, an access token will be given to you, which will be used in the request headers. To use the access token and set your database variables, you're gonna have to create a config.py file with the following variables:

```
api_football_key = YOUR_ACCESS_TOKEN
conn_host = YOUR_CONNECTION_HOST
conn_database = YOUR_CONNECTION_DATABASE
conn_user = YOUR_CONNECTION_USER
conn_password = YOUR_CONNECTION_PASSWORD
```

# Collecting Odds
In order to scrape the odds for the matches that you've collected in the main program, you have to run the odds.py program to do a web scrapping job in the Odds Portal website. The only issue with this website is that the names of some of the teams might be different from the ones registered in the API used to get the matches. In order to fix this issue, you have to manually change the name of the teams in the database to the ones written in the Odds Portal website. For exemaple, the name of a team in the API was "Atletico Paranaense" while in the odds website was "Athletico-PR".

# Selecting the League
The default league used in this project is the brazilian Serie A. If you want to collect data from other leagues, first of all you have to change the league id set in the main.ipynb program. The other thing that needs to be changed is the Odds Portal url parameters set in the odds.ipynb program. To check which parameters you need, go to the [Odds Portal](https://www.oddsportal.com/) website to check which are the parameters of your country/league selected.

And that's it! Now you can make requests to the API, store football fixtures from your favorite leagues in your database and get the odds from each match. Enjoy!

