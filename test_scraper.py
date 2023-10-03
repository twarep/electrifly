import pytest
from dotenv import load_dotenv
from scraper import convert_str_to_datetime, weather_data
from datetime import datetime

class TestScraper:
  def test_convert_str_to_datetime(self):
    load_dotenv()
    test_datetime = "Oct. 1, 2023, 8:20 PM"
    converted_datetime = convert_str_to_datetime(test_datetime)
    expected_datetime = datetime(2023, 10, 1, 20, 20)
    assert converted_datetime == expected_datetime
