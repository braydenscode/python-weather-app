import sys
import os
import requests
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QBrush, QGradient

class WeatherApp(QWidget):
    WEATHER_GRADIENTS = {
        # "Clear": ("#fceabb", "#f8b500"),
        "Clear_day": ("#fceabb", "#f8b500"),
        "Clear_night": ("#112159", "#93659F"),
        "Clouds": ("#d7d2cc", "#304352"),
        "Rain": ("#4e54c8", "#8f94fb"),
        "Drizzle": ("#89f7fe", "#66a6ff"),
        "Thunderstorm": ("#373B44", "#4286f4"),
        "Snow": ("#e0eafc", "#cfdef3"),
        "Mist": ("#d3cce3", "#e9e4f0"),
        "Fog": ("#d3cce3", "#e9e4f0"),
        "Haze": ("#d3cce3", "#e9e4f0"),
        "Smoke": ("#636363", "#a2ab58"),
        "Dust": ("#b79891", "#94716b"),
        "Sand": ("#c2b280", "#e6d3b3"),
        "Ash": ("#a770ef", "#cf8bf3"),
        "Squall": ("#3a6073", "#16222a"),
        "Tornado": ("#232526", "#414345"),
    }

    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.change_unit_button = QPushButton("°C", self)
        self.change_unit_button.hide()
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

        self.weather_data = None
        self.unit_is_fahrenheit = True
        self.temperature_k = None

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setWindowTitle("Weather App")

        temp_layout = QHBoxLayout()
        temp_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        temp_layout.addWidget(self.temperature_label, alignment=Qt.AlignVCenter)
        temp_layout.addWidget(self.change_unit_button, alignment=Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addLayout(temp_layout)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.change_unit_button.setFixedSize(50, 50)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.change_unit_button.setObjectName("change_unit_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.add_text_shadow(self.city_label)
        self.add_text_shadow(self.temperature_label)
        self.add_text_shadow(self.description_label)

        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family: calibri;
            }
            QLabel#city_label{
                font-size: 40px;
                font-style: italic;
            }
            QLineEdit#city_input{
                font-size: 40px;
            }
            QPushButton#get_weather_button, QPushButton#change_unit_button{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temperature_label{
                font-size: 75px;
                padding-right: 10px;
            }
            QLabel#emoji_label{
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
            QLabel#description_label{
                font-size: 50px;
            }
        """)

        self.city_input.returnPressed.connect(self.get_weather)
        self.get_weather_button.clicked.connect(self.get_weather)
        self.change_unit_button.clicked.connect(self.change_unit)

    def add_text_shadow(self, label, color=Qt.white, offset=(0, 0), blur_radius=8):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(*offset)
        shadow.setColor(color)
        label.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        top_color = "#a1c4fd"
        bottom_color = "#c2e9fb"

        if self.weather_data:
            weather_main = self.weather_data["weather"][0]["main"]
            top_color, bottom_color = self.WEATHER_GRADIENTS.get(weather_main, (top_color, bottom_color))

            sunrise_timestamp = self.weather_data["sys"]["sunrise"]
            sunset_timestamp = self.weather_data["sys"]["sunset"]
            timezone_offset = self.weather_data["timezone"]

            sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp, tz=datetime.timezone(datetime.timedelta(seconds=timezone_offset)))
            sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp, tz=datetime.timezone(datetime.timedelta(seconds=timezone_offset)))
            current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=timezone_offset)))

            is_daytime = sunrise_time < current_time < sunset_time

            if not is_daytime:
                if weather_main == "Clear":
                    key = "Clear_day" if is_daytime else "Clear_night"
                else:
                    key = weather_main
                top_color, bottom_color = self.WEATHER_GRADIENTS.get(key, (top_color, bottom_color))


        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(top_color))
        gradient.setColorAt(1, QColor(bottom_color))

        painter.fillRect(rect, QBrush(gradient))

    def get_weather(self):
        api_key = os.getenv("API_KEY")
        self.temperature_k = None
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        self.temperature_label.setText("")
        self.emoji_label.clear()
        self.description_label.clear()

        self.get_weather_button.setEnabled(False)
        self.change_unit_button.setEnabled(False)

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                print(data)
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal server error:\nPlease try again later")
                case 501:
                    self.display_error("Bad gateway:\nInvalid response from the server")
                case 502:
                    self.display_error("Service unavailable:\nServer is down")
                case 503:
                    self.display_error("Gateway timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")
        finally:
            self.get_weather_button.setEnabled(True)
            self.change_unit_button.setEnabled(True)



    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data=None):
        if data:
            self.weather_data = data
            self.repaint()
            self.temperature_k = data["main"]["temp"]
            weather_id = data["weather"][0]["id"]
            weather_description = data["weather"][0]["description"]
            self.emoji_label.setText(self.get_weather_emoji(weather_id))
            self.description_label.setText(weather_description.capitalize())

        if self.temperature_k is not None:
            self.change_unit_button.show()
            self.temperature_label.setStyleSheet("font-size: 75px;")
            temperature_c = self.temperature_k - 273.15
            temperature_f = (self.temperature_k * 9 / 5) - 459.67
            if self.unit_is_fahrenheit:
                self.temperature_label.setText(f"{temperature_f:.0f}°F")
            else:
                self.temperature_label.setText(f"{temperature_c:.1f}°C")
        else:
            self.change_unit_button.hide()


    def change_unit(self):
        self.unit_is_fahrenheit = not self.unit_is_fahrenheit
        self.change_unit_button.setText("°F" if not self.unit_is_fahrenheit else "°C")
        self.display_weather()

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈"
        elif 300 <= weather_id <= 321:
            return "🌦"
        elif 500 <= weather_id <= 531:
            return "🌧"
        elif 600 <= weather_id <= 622:
            return "❄"
        elif 701 <= weather_id <= 741:
            return "🌫"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪"
        elif weather_id == 800:
            return "☀"
        elif 801 <= weather_id <= 804:
            return "☁"
        else:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())