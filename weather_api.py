import os
import requests

from ui.ui_helpers import clear_labels, display_error
from utils import daytime_check


def get_weather_by_city(self):
    api_key = os.getenv("API_KEY")
    city = self.city_input.text()
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    data = fetch_weather_data(self, url)
    if data:
        print(data)
        self.previous_data = self.weather_data
        self.weather_data = data
        self.is_daytime = daytime_check(data)
        self.display_weather()
        self.update_map()
        self.update_save_data_button()
        if self.auto_saves_city_data:
            self.save_current_data()


def get_weather_by_coords(self, lat, lon):
    api_key = os.getenv("API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    data = fetch_weather_data(self, url)
    if data:
        print(data)
        self.previous_data = self.weather_data
        self.weather_data = data
        self.is_daytime = daytime_check(data)
        self.update_map()
        self.display_weather()
        self.update_save_data_button()
        if self.auto_saves_coords_data:
            self.save_current_data()


def fetch_weather_data(self, url):
    self.temperature_label.setText("")
    self.temperature_label_advanced.setText("")
    clear_labels(self)

    self.get_weather_button.setEnabled(False)
    self.change_unit_button.setEnabled(False)
    self.change_display_button.setEnabled(False)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["cod"] == 200:
            return data

    except requests.exceptions.HTTPError as http_error:
        match response.status_code:
            case 400:
                display_error(self, "Bad request:\nPlease check your input")
            case 401:
                display_error(self, "Unauthorized:\nInvalid API key")
            case 403:
                display_error(self, "Forbidden:\nAccess is denied")
            case 404:
                display_error(self, "Not found:\nCity not found")
            case 500:
                display_error(self, "Internal server error:\nPlease try again later")
            case 501:
                display_error(self, "Bad gateway:\nInvalid response from the server")
            case 502:
                display_error(self, "Service unavailable:\nServer is down")
            case 503:
                display_error(self, "Gateway timeout:\nNo response from the server")
            case _:
                display_error(self, f"HTTP error occurred:\n{http_error}")

    except requests.exceptions.ConnectionError:
        display_error(self, "Connection Error:\nCheck your internet connection")
    except requests.exceptions.Timeout:
        display_error(self, "Timeout Error:\nThe request timed out")
    except requests.exceptions.TooManyRedirects:
        display_error(self, "Too many redirects:\nCheck the URL")
    except requests.exceptions.RequestException as req_error:
        display_error(self, f"Request Error:\n{req_error}")
    finally:
        self.get_weather_button.setEnabled(True)
        self.change_unit_button.setEnabled(True)
        self.change_display_button.setEnabled(True)