# Brasileirao-Data
Project designed to gather and clean data from the brazilian football league from the API-Football api.

# Setup
In order to run this program, you are gonna have to sign up on the [API-Football](https://www.api-football.com/pricing) website. You can sign up for free with up to 100 request a day. When you're done setting up your account, an access token will be given to you, which will be used in the request headers. To use the access token and set your database variables, you're gonna have to create a config.py file with the following variables:

```
api_football_key = YOUR_ACCESS_TOKEN
conn_host = YOUR_CONNECTION_HOST
conn_database = YOUR_CONNECTION_DATABASE
conn_user = YOUR_CONNECTION_USER
conn_password = YOUR_CONNECTION_PASSWORD
```

And that's it! Now you can make requests to the API and store football fixtures from your favorite leagues in your database. Enjoy!

