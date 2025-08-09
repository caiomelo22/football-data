from services.scrapper.mixins.driver import DriverMixin
import time
import pandas as pd
import typing as t
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm
from datetime import datetime


class NowGoalScrapperService(DriverMixin):
    def __init__(self, nowgoal_league_id: int, season_str: str):
        DriverMixin.__init__(
            self,
        )

        self.nowgoal_league_id = nowgoal_league_id
        self.season_str = season_str

    def get_betting_data_from_match(
        self, match_cols: t.List[WebElement], market_element: WebElement
    ) -> t.List[float]:
        market_element.click()

        # Define the betting columns
        betting_cols = match_cols[5:8]

        betting_cols_formatted = []

        for col in betting_cols:
            col_text = col.text

            if not col_text:
                betting_cols_formatted.append(None)
                continue
            elif "/" not in col_text:
                betting_cols_formatted.append(float(col_text))
                continue

            # Case of quarter lines
            val_splitted = col_text.split("/")

            first_value = float(val_splitted[0])
            second_value = float(val_splitted[1])

            # If both parts of the string are negative, get a negative result
            if first_value < 0:
                second_value *= -1

            formatted_value = (first_value + second_value) / 2

            betting_cols_formatted.append(formatted_value)

        return betting_cols_formatted

    def clean_team_name(self, team: WebElement) -> str:
        a_tag = team.find_element(By.TAG_NAME, "a")

        team_text = a_tag.text

        return team_text

    def get_match_score(
        self, score: WebElement
    ) -> t.Tuple[t.Optional[int], t.Optional[int]]:
        score_text = score.text

        try:
            home_score, away_score = score_text.split("-")

            return int(home_score), int(away_score)
        except:
            return None, None

    def build_match_date(self, match_date: WebElement) -> datetime:
        match_date_attr = match_date.get_attribute("data-t")

        date, _ = match_date_attr.split(" ")

        year, month, day = date.split("-")

        # Ignore the time of the matches since there might be timezone divergences
        new_date = datetime(int(year), int(month), int(day), 0, 0)

        return new_date

    def get_match_data(
        self,
        match: WebElement,
        ahc_span: WebElement,
        moneyline_span: WebElement,
        totals_span: WebElement,
    ) -> t.Optional[dict]:
        # If it fails the first time, try again after sleeping for 1.5 second
        for i in range(2):
            try:
                if i > 0:
                    time.sleep(1.5)

                match_cols = match.find_elements(By.TAG_NAME, "td")
                match_info_cols = match_cols[
                    :5
                ]  # Only get the columns with useful data

                match_round, match_date, home_team, score, away_team = match_info_cols

                home_score, away_score = self.get_match_score(score)

                if None in [home_score, away_score]:
                    return None

                home_team = self.clean_team_name(home_team)
                away_team = self.clean_team_name(away_team)

                match_date_formatted = self.build_match_date(match_date)

                home_ahc_odds, ahc_line, away_ahc_odds = (
                    self.get_betting_data_from_match(match_cols, ahc_span)
                )
                home_odds, draw_odds, away_odds = self.get_betting_data_from_match(
                    match_cols, moneyline_span
                )
                overs_odds, totals_line, unders_odds = self.get_betting_data_from_match(
                    match_cols, totals_span
                )

                return {
                    "round": int(match_round.text),
                    "date": match_date_formatted,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    # Moneyline odds
                    "home_odds": home_odds,
                    "draw_odds": draw_odds,
                    "away_odds": away_odds,
                    # Asian Handicap odds
                    "home_ahc_odds": home_ahc_odds,
                    "ahc_line": ahc_line,
                    "away_ahc_odds": away_ahc_odds,
                    # Totals odds
                    "overs_odds": overs_odds,
                    "totals_line": totals_line,
                    "unders_odds": unders_odds,
                }
            except:
                if i == 0:
                    continue

                return None

    def get_match_html_elements(
        self, prev_first_match: t.Optional[WebElement]
    ) -> t.List[WebElement]:
        for i in range(2):
            time.sleep(i + 1)

            matches_table = self.driver.find_element(By.ID, "Table3")
            matches_table_trs = matches_table.find_elements(By.TAG_NAME, "tr")

            matches = matches_table_trs[2:]  # Remove the first unused rows

            # Retry in case there was no time to update the matches elements
            if matches[0] == prev_first_match:
                continue

            return matches

        return []

    def scrape_league_by_round(
        self, prev_first_match: t.Optional[WebElement] = None
    ) -> t.Tuple[t.List[dict], t.Optional[WebElement]]:
        round_matches = []

        matches = self.get_match_html_elements(prev_first_match)

        odds_div = self.driver.find_element(By.CLASS_NAME, "odds")

        ahc_span, moneyline_span, totals_span = odds_div.find_elements(
            By.TAG_NAME, "span"
        )

        for match in matches:
            match_data = self.get_match_data(
                match=match,
                ahc_span=ahc_span,
                moneyline_span=moneyline_span,
                totals_span=totals_span,
            )

            if not match_data:
                continue

            round_matches.append(match_data)

        if matches:
            prev_first_match = matches[0]

        # Return the round matches and the first match element to be defined as the prev_first_match
        return round_matches, prev_first_match

    def scrape_league_by_stage(self) -> t.List[dict]:
        round_tds = self.driver.find_elements(By.CLASS_NAME, "lsm2")

        # If there are multiple rounds in the competition
        if round_tds:
            stage_matches = []
            prev_first_match = None

            # Iterate through the rounds
            for i in tqdm(range(len(round_tds))):
                round_td = round_tds[i]

                round_td.click()

                round_matches, prev_first_match = self.scrape_league_by_round(
                    prev_first_match
                )

                stage_matches.extend(round_matches)
        else:
            # Competition with a single round
            stage_matches, _ = self.scrape_league_by_round()

        return stage_matches

    def nowgoal_scrapper(self) -> None:
        url = f"https://football.nowgoal.com/league/{self.season_str}/{self.nowgoal_league_id}"
        self.driver.get(url)

        season = int(self.season_str.split("-")[0])

        time.sleep(3)

        stages_div = self.driver.find_element(By.ID, "SubSelectDiv")

        # Check if there is more than one stage in the competition
        if stages_div:
            stages_elements = stages_div.find_elements(By.TAG_NAME, "li")
            stages = [se.text for se in stages_elements]

            matches_data = []

            # Iterate through each stage
            for stage in stages:
                stage_element = self.driver.find_element(
                    By.XPATH, f"//li[text()='{stage}']"
                )

                stage_element.click()

                time.sleep(1)

                stage_matches = self.scrape_league_by_stage()

                matches_data.extend(stage_matches)
        else:
            # Single format competition
            matches_data = self.scrape_league_by_stage()

        matches_data_df = pd.DataFrame(matches_data)

        matches_data_df["season"] = season

        self.nowgoal_data_df = matches_data_df
