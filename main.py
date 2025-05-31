import sys
import os
import requests
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QGraphicsDropShadowEffect, QStackedWidget, QGraphicsOpacityEffect, QMainWindow, QDockWidget, QTableWidget, \
    QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QBrush, QPixmap, QImage
import mysql.connector as mc
import json
from widgets.map import MapWindow

class WeatherApp(QMainWindow):
    WEATHER_GRADIENTS = {
        "Clear_day": ("#fceabb", "#f8b500"),
        "Clear_night": ("#112159", "#93659F"),
        "Clouds_day": ("#d7d2cc", "#304352"),
        "Clouds_night": ("#112159", "#6f7675"),
        "Rain_day": ("#4e54c8", "#8f94fb"),
        "Rain_night": ("#112159", "#4e54c8"),
        "Drizzle_day": ("#89f7fe", "#66a6ff"),
        "Drizzle_night": ("#112159", "#66a6ff"),
        "Thunderstorm_day": ("#373B44", "#4286f4"),
        "Thunderstorm_night": ("#272930", "#245BB2"),
        "Snow": ("#e0eafc", "#cfdef3"),
        "Mist": ("#d3cce3", "#e9e4f0"),
        "Fog": ("#d3cce3", "#e9e4f0"),
        "Haze": ("#d3cce3", "#e9e4f0"),
        "Smoke": ("#636363", "#a2ab58"),
        "Dust": ("#b79891", "#94716b"),
        "Sand": ("#c2b280", "#e6d3b3"),
        "Ash": ("#121212", "#b43131"),
        "Squall": ("#3a6073", "#16222a"),
        "Tornado": ("#232526", "#414345"),
    }

    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)

        self.change_display_button = QPushButton("Advanced", self)
        self.change_unit_button = QPushButton("°C", self)

        self.map_button = QPushButton("🗺️", self)
        self.database_button = QPushButton("📝", self)

        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.temperature_label_advanced = QLabel(self)
        self.emoji_label_advanced = QLabel(self)
        self.description_label_advanced = QLabel(self)

        self.feels_like_temp_label = QLabel(self)
        self.temp_min_label = QLabel(self)
        self.temp_max_label = QLabel(self)
        self.pressure_label = QLabel(self)
        self.visibility_label = QLabel(self)
        self.wind_direction_label = QLabel(self)
        self.wind_gust_label = QLabel(self)
        self.coordinates_label = QLabel(self)
        self.sunrise_label = QLabel(self)
        self.sunset_label = QLabel(self)
        self.country_label = QLabel(self)
        self.dt_label = QLabel(self)
        self.dt_label_advanced = QLabel(self)
        self.clouds_label = QLabel(self)
        self.humidity_label = QLabel(self)
        self.wind_speed_label = QLabel(self)
        self.clouds_label_advanced = QLabel(self)
        self.humidity_label_advanced = QLabel(self)
        self.wind_speed_label_advanced = QLabel(self)

        self.stacked_widget = QStackedWidget(self)
        self.compact_widget = QWidget()
        self.advanced_widget = QWidget()

        self.map_dock = None
        self.db_dock = None

        self.weather_data = None
        self.previous_data = None
        self.unit_is_fahrenheit = True
        self.is_daytime = None

        self.auto_saves_city_data = True
        self.auto_saves_coords_data = False

        self.initUI()
        self.db_connection = self.db_connect()
        self.toggle_db_dock()

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setWindowTitle("Weather App")
        self.setMinimumSize(420, 720)
        self.setMaximumHeight(720)

        for label in [
            self.feels_like_temp_label,
            self.temp_min_label,
            self.temp_max_label,
            self.pressure_label,
            self.visibility_label,
            self.wind_direction_label,
            self.wind_gust_label,
            self.coordinates_label,
            self.sunrise_label,
            self.sunset_label,
            self.country_label,
            self.dt_label,
            self.dt_label_advanced
        ]:
            label.setAlignment(Qt.AlignCenter)

        self.clouds_label.setAlignment(Qt.AlignCenter)
        self.humidity_label.setAlignment(Qt.AlignCenter)
        self.wind_speed_label.setAlignment(Qt.AlignCenter)
        self.clouds_label_advanced.setAlignment(Qt.AlignCenter)
        self.humidity_label_advanced.setAlignment(Qt.AlignCenter)
        self.wind_speed_label_advanced.setAlignment(Qt.AlignCenter)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.temperature_label_advanced.setAlignment(Qt.AlignCenter)
        self.emoji_label_advanced.setAlignment(Qt.AlignCenter)
        self.description_label_advanced.setAlignment(Qt.AlignCenter)

        self.clouds_label.setFixedSize(100, 50)
        self.humidity_label.setFixedSize(100, 50)
        self.wind_speed_label.setFixedSize(100, 50)
        self.change_unit_button.setFixedSize(30, 30)
        self.change_display_button.setFixedSize(100, 30)
        self.map_button.setFixedSize(40, 40)
        self.database_button.setFixedSize(40, 40)

        # FOR BOTH LAYOUTS
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addWidget(self.change_unit_button, alignment=Qt.AlignLeft)
        bottom_button_layout.spacing()
        bottom_button_layout.addWidget(self.country_label)
        bottom_button_layout.spacing()
        bottom_button_layout.addWidget(self.change_display_button, alignment=Qt.AlignRight)

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.map_button)
        top_row_layout.addWidget(self.city_label)
        top_row_layout.addWidget(self.database_button)

        input_layout = QVBoxLayout()
        input_layout.addLayout(top_row_layout)
        input_layout.addWidget(self.city_input)
        input_layout.addWidget(self.get_weather_button)

        # FOR COMPACT LAYOUT
        secondary_layout = QHBoxLayout()
        secondary_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        secondary_layout.addWidget(self.clouds_label)
        secondary_layout.addWidget(self.humidity_label)
        secondary_layout.addWidget(self.wind_speed_label)

        # FOR ADVANCED LAYOUT
        secondary_layout_advanced = QHBoxLayout()
        secondary_layout_advanced.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        secondary_layout_advanced.addWidget(self.clouds_label_advanced)
        secondary_layout_advanced.addWidget(self.humidity_label_advanced)
        secondary_layout_advanced.addWidget(self.pressure_label)
        secondary_layout_advanced.addWidget(self.visibility_label)

        wind_layout = QHBoxLayout()
        wind_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        wind_layout.addWidget(self.wind_speed_label_advanced)
        wind_layout.addWidget(self.wind_direction_label)
        wind_layout.addWidget(self.wind_gust_label)

        horizon_layout = QHBoxLayout()
        horizon_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        horizon_layout.addWidget(self.sunrise_label, alignment=Qt.AlignBottom)
        horizon_layout.addStretch()
        horizon_layout.addWidget(self.feels_like_temp_label)
        horizon_layout.addStretch()
        horizon_layout.addWidget(self.sunset_label, alignment=Qt.AlignBottom)

        temperature_layout = QVBoxLayout()
        temperature_layout.setSpacing(0)
        temperature_layout_row = QHBoxLayout()
        temperature_layout_row.setSpacing(15)
        temperature_layout_row.setAlignment(Qt.AlignHCenter)
        temperature_layout_row.addWidget(self.temp_min_label, alignment=Qt.AlignTop)
        temperature_layout_row.addWidget(self.temperature_label_advanced, alignment=Qt.AlignTop)
        temperature_layout_row.addWidget(self.temp_max_label, alignment=Qt.AlignTop)
        temperature_layout.addLayout(temperature_layout_row)
        temperature_layout.addWidget(self.emoji_label_advanced)

        # COMPACT LAYOUT
        compact_layout = QVBoxLayout()
        compact_layout.addWidget(self.temperature_label)
        compact_layout.addWidget(self.emoji_label)
        compact_layout.addStretch()
        compact_layout.addWidget(self.description_label)
        compact_layout.addStretch()
        compact_layout.addLayout(secondary_layout)
        compact_layout.addStretch()
        compact_layout.addWidget(self.dt_label)
        self.compact_widget.setLayout(compact_layout)

        # ADVANCED LAYOUT
        advanced_layout = QVBoxLayout()
        advanced_layout.addLayout(temperature_layout)
        advanced_layout.addLayout(horizon_layout)
        advanced_layout.addWidget(self.description_label_advanced)
        advanced_layout.addLayout(secondary_layout_advanced)
        advanced_layout.addLayout(wind_layout)
        advanced_layout.addStretch()
        advanced_layout.addWidget(self.dt_label_advanced)
        self.advanced_widget.setLayout(advanced_layout)

        # STACKED WIDGET
        self.stacked_widget.addWidget(self.compact_widget)
        self.stacked_widget.addWidget(self.advanced_widget)
        self.stacked_widget.setCurrentIndex(0)

        # MAIN LAYOUT
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(bottom_button_layout)
        self.setLayout(main_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setFixedSize(420, 720)
        self.setCentralWidget(central_widget)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.change_unit_button.setObjectName("change_unit_button")
        self.change_display_button.setObjectName("change_display_button")
        self.map_button.setObjectName("map_button")
        self.database_button.setObjectName("database_button")
        self.temperature_label.setObjectName("temperature_label")
        self.temperature_label_advanced.setObjectName("temperature_label_advanced")
        self.emoji_label.setObjectName("emoji_label")
        self.emoji_label_advanced.setObjectName("emoji_label_advanced")
        self.description_label.setObjectName("description_label")
        self.description_label_advanced.setObjectName("description_label_advanced")
        self.clouds_label.setObjectName("clouds_label")
        self.clouds_label_advanced.setObjectName("clouds_label_advanced")
        self.humidity_label.setObjectName("humidity_label")
        self.humidity_label_advanced.setObjectName("humidity_label_advanced")
        self.wind_speed_label.setObjectName("wind_speed_label")
        self.wind_speed_label_advanced.setObjectName("wind_speed_label_advanced")
        self.temp_min_label.setObjectName("temp_min_label")
        self.temp_max_label.setObjectName("temp_max_label")
        self.feels_like_temp_label.setObjectName("feels_like_temp_label")
        self.pressure_label.setObjectName("pressure_label")
        self.visibility_label.setObjectName("visibility_label")
        self.wind_direction_label.setObjectName("wind_direction_label")
        self.wind_gust_label.setObjectName("wind_gust_label")
        self.sunrise_label.setObjectName("sunrise_label")
        self.sunset_label.setObjectName("sunset_label")
        self.dt_label.setObjectName("dt_label")
        self.dt_label_advanced.setObjectName("dt_label_advanced")

        self.add_text_shadow(self.city_label, Qt.white, (0, 0), 50)
        self.add_text_shadow(self.temperature_label)
        self.add_text_shadow(self.temperature_label_advanced)
        self.add_text_shadow(self.description_label)
        self.add_text_shadow(self.description_label_advanced)

        self.add_text_shadow(self.clouds_label)
        self.add_text_shadow(self.humidity_label)
        self.add_text_shadow(self.wind_speed_label)

        temp_min_opacity = QGraphicsOpacityEffect()
        temp_min_opacity.setOpacity(0.45)
        temp_max_opacity = QGraphicsOpacityEffect()
        temp_max_opacity.setOpacity(0.45)

        self.temp_min_label.setGraphicsEffect(temp_min_opacity)
        self.temp_max_label.setGraphicsEffect(temp_max_opacity)

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
            QPushButton#get_weather_button{
                font-size: 30px;
                font-weight: bold;
            }
            QPushButton#change_display_button, QPushButton#change_unit_button{
                font-size: 20px;
                font-style: italic;
            }
            QLabel#temperature_label, QLabel#temperature_label_advanced{
                font-size: 75px;
            }
            QLabel#emoji_label, QLabel#emoji_label_advanced{
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
            QLabel#description_label, QLabel#description_label_advanced{
                font-size: 50px;
            }
            QLabel#temp_min_label, QLabel#temp_max_label{
                font-size: 40px;
            }
            QLabel#wind_speed_label, QLabel#humidity_label, QLabel#clouds_label{
                font-size: 20px;
                font-weight: bold;
                padding: 0px 1px 0px 1px;
            }
            QLabel#wind_speed_label_advanced, QLabel#humidity_label_advanced, QLabel#clouds_label_advanced,
            QLabel#pressure_label, QLabel#visibility_label, QLabel#wind_direction_label, QLabel#wind_gust_label, QLabel#sunrise_label, QLabel#sunset_label,
            QLabel#feels_like_temp_label{
                font-size: 20px;
                padding: 0px 1px 0px 1px;
            }
            QPushButton#map_button, QPushButton#database_button{
                font-size: 20px;
            }
        """)

        self.city_input.returnPressed.connect(self.get_weather_by_city)
        self.get_weather_button.clicked.connect(self.get_weather_by_city)
        self.change_unit_button.clicked.connect(self.change_unit)
        self.change_display_button.clicked.connect(self.change_display)
        self.map_button.clicked.connect(self.toggle_map_dock)
        self.database_button.clicked.connect(self.toggle_db_dock)

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
            current_local_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=timezone_offset)))

            self.is_daytime = sunrise_time < current_local_time < sunset_time

            if weather_main == "Clear":
                key = "Clear_day" if self.is_daytime else "Clear_night"
            elif weather_main == "Clouds":
                key = "Clouds_day" if self.is_daytime else "Clouds_night"
            elif weather_main == "Rain":
                key = "Rain_day" if self.is_daytime else "Rain_night"
            elif weather_main == "Drizzle":
                key = "Drizzle_day" if self.is_daytime else "Drizzle_night"
            elif weather_main == "Thunderstorm":
                key = "Thunderstorm_day" if self.is_daytime else "Thunderstorm_night"
            else:
                key = weather_main

            top_color, bottom_color = self.WEATHER_GRADIENTS.get(key, (top_color, bottom_color))

        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(top_color))
        gradient.setColorAt(1, QColor(bottom_color))

        painter.fillRect(rect, QBrush(gradient))

    def clear_labels(self):
        self.emoji_label.clear()
        self.emoji_label_advanced.clear()
        self.description_label.clear()
        self.description_label_advanced.clear()
        self.clouds_label.clear()
        self.humidity_label.clear()
        self.wind_speed_label.clear()
        self.clouds_label_advanced.clear()
        self.humidity_label_advanced.clear()
        self.wind_speed_label_advanced.clear()
        self.wind_direction_label.clear()
        self.wind_gust_label.clear()
        self.visibility_label.clear()
        self.pressure_label.clear()
        self.sunrise_label.clear()
        self.sunset_label.clear()
        self.dt_label.clear()
        self.dt_label_advanced.clear()
        self.temp_min_label.clear()
        self.temp_max_label.clear()
        self.feels_like_temp_label.clear()
        self.country_label.clear()

    def get_weather_by_city(self):
        api_key = os.getenv("API_KEY")
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        data = self.fetch_weather_data(url)
        if data:
            print(data)
            self.previous_data = self.weather_data
            self.weather_data = data
            self.display_weather()
            self.update_map()
            self.update_save_data_button()
            if self.auto_saves_city_data:
                self.save_current_data()

    def get_weather_by_coords(self, lat, lon):
        api_key = os.getenv("API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        data = self.fetch_weather_data(url)
        if data:
            print(data)
            self.previous_data = self.weather_data
            self.weather_data = data
            self.update_map()
            self.display_weather()
            self.update_save_data_button()
            if self.auto_saves_coords_data:
                self.save_current_data()

    def  fetch_weather_data(self, url):
        self.temperature_label.setText("")
        self.temperature_label_advanced.setText("")
        self.clear_labels()

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
            self.change_display_button.setEnabled(True)


    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label_advanced.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.temperature_label_advanced.setText(message)
        self.clear_labels()

    def display_weather(self):
        if self.weather_data:
            self.repaint()

            self.city_input.setText(f"{self.weather_data['name']}, {self.weather_data['sys']['country']}")
            weather_id = self.weather_data["weather"][0]["id"]
            weather_description = self.weather_data["weather"][0]["description"]
            self.emoji_label.setText(self.get_weather_emoji(weather_id))
            self.emoji_label_advanced.setText(self.get_weather_emoji(weather_id))
            self.description_label.setText(weather_description.title())
            self.description_label_advanced.setText(weather_description.title())

            if len(self.description_label.text()) >= 25:
                self.description_label.setStyleSheet("font-size: 28px;")
                self.description_label_advanced.setStyleSheet("font-size: 28px;")
            elif len(self.description_label.text()) >= 15:
                self.description_label.setStyleSheet("font-size: 40px;")
                self.description_label_advanced.setStyleSheet("font-size: 40px;")
            else:
                pass

            self.clouds_label.setText(f"Clouds\n{self.weather_data['clouds']['all']}%")
            self.humidity_label.setText(f"Humidity\n{self.weather_data['main']['humidity']}%")
            self.clouds_label_advanced.setText(f"Clouds\n{self.weather_data['clouds']['all']}%")
            self.humidity_label_advanced.setText(f"Humidity\n{self.weather_data['main']['humidity']}%")

            self.temperature_label.setStyleSheet("font-size: 75px;")
            self.temperature_label_advanced.setStyleSheet("font-size: 75px;")

            def convert_to_c(temp):
                return temp - 273.15
            def convert_to_f(temp):
                return (temp * 9 / 5) - 459.67
            def get_direction_arrow(degrees):
                directions = [
                    (0, "↑"), (45, "↗"), (90, "→"), (135, "↘"),
                    (180, "↓"), (225, "↙"), (270, "←"), (315, "↖"), (360, "↑")
                ]
                closest_direction = min(directions, key=lambda x: abs(x[0] - degrees))
                return closest_direction[1]

            if self.unit_is_fahrenheit:
                self.temperature_label.setText(f"{convert_to_f(self.weather_data['main']['temp']):.0f}°F")
                self.wind_speed_label.setText(f"Wind\n{self.weather_data['wind']['speed'] * 2.237:.1f} mph")
                self.wind_speed_label_advanced.setText(f"Wind Speed\n{self.weather_data['wind']['speed'] * 2.237:.1f} mph")
                self.feels_like_temp_label.setText(f"Feels Like\n{convert_to_f(self.weather_data['main']['feels_like']):.0f}°")
                self.temp_min_label.setText(f"{convert_to_f(self.weather_data['main']['temp_min']):.0f}°")
                self.temp_max_label.setText(f"{convert_to_f(self.weather_data['main']['temp_max']):.0f}°")
                self.temperature_label_advanced.setText(f"{convert_to_f(self.weather_data['main']['temp']):.0f}°F")
                self.pressure_label.setText(f"Pressure\n{self.weather_data['main']['pressure'] * 0.02953:.2f} inHg")
                self.visibility_label.setText(f"Visibility\n{self.weather_data['visibility'] * 0.000621:.1f} mi")
                if self.weather_data['wind'].get('gust'):
                    self.wind_gust_label.setText(f"Wind Gust\n{self.weather_data['wind']['gust'] * 2.237:.1f} mph")
                else:
                    self.wind_gust_label.setText("Wind Gust\nN/A")
            else:
                self.temperature_label.setText(f"{convert_to_c(self.weather_data['main']['temp']):.0f}°C")
                self.wind_speed_label.setText(f"Wind\n{self.weather_data['wind']['speed']:.1f} m/s")
                self.wind_speed_label_advanced.setText(f"Wind Speed\n{self.weather_data['wind']['speed']:.1f} m/s")
                self.feels_like_temp_label.setText(f"Feels Like\n{convert_to_c(self.weather_data['main']['feels_like']):.0f}°")
                self.temp_min_label.setText(f"{convert_to_c(self.weather_data['main']['temp_min']):.0f}°")
                self.temp_max_label.setText(f"{convert_to_c(self.weather_data['main']['temp_max']):.0f}°")
                self.temperature_label_advanced.setText(f"{convert_to_c(self.weather_data['main']['temp']):.0f}°C")
                self.pressure_label.setText(f"Pressure\n{self.weather_data['main']['pressure']:.1f} hPa")
                self.visibility_label.setText(f"Visibility\n{self.weather_data['visibility'] / 1000:.1f} km")
                if self.weather_data['wind'].get('gust'):
                    self.wind_gust_label.setText(f"Wind Gust\n{self.weather_data['wind']['gust']:.1f} m/s")
                else:
                    self.wind_gust_label.setText("Wind Gust\nN/A")

            timezone = datetime.timezone(datetime.timedelta(seconds=self.weather_data['timezone']))

            self.sunrise_label.setText(
                f"Sunrise\n{datetime.datetime.fromtimestamp(self.weather_data['sys']['sunrise'], tz=timezone).strftime('%H:%M')}")
            self.sunset_label.setText(
                f"Sunset\n{datetime.datetime.fromtimestamp(self.weather_data['sys']['sunset'], tz=timezone).strftime('%H:%M')}")
            self.wind_direction_label.setText(
                f"Wind Direction\n{get_direction_arrow(self.weather_data['wind']['deg'])} {self.weather_data['wind']['deg']}°")
            self.dt_label.setText(
                f"Data collected @ {datetime.datetime.fromtimestamp(self.weather_data['dt']).strftime('%I:%M %p, %B %d, %Y')}")
            self.dt_label_advanced.setText(
                f"Data collected @ {datetime.datetime.fromtimestamp(self.weather_data['dt']).strftime('%I:%M %p, %B %d, %Y')}")

            # not using. might add search location by clicking point on map and searching with coords
            # self.coordinates_label.setText(f"Coords\n{self.weather_data['coord']['lat']}, {self.weather_data['coord']['lon']}")

            url = f"https://flagcdn.com/h24/{self.weather_data['sys']['country'].lower()}.png"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                image_data = response.content
                image = QImage()
                if image.loadFromData(image_data):
                    pixmap = QPixmap.fromImage(image)
                    self.country_label.setPixmap(pixmap)
                else:
                    print("Flag didn't load")
            except Exception as e:
                print(f"Error loading flag: {e}")
        else:
            print("Missing weather data.")


    def change_unit(self):
        self.unit_is_fahrenheit = not self.unit_is_fahrenheit
        self.change_unit_button.setText("°F" if not self.unit_is_fahrenheit else "°C")
        if self.weather_data:
            self.display_weather()
        if self.db_dock and self.db_dock.isVisible():
            self.load_saved_weather_data()

    def change_display(self):
        current_index = self.stacked_widget.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.stacked_widget.setCurrentIndex(new_index)
        self.change_display_button.setText("Compact" if new_index == 1 else "Advanced")

    def get_weather_emoji(self, weather_id):
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
            if self.is_daytime:
                return "☀"
            else:
                return "🌙"
        elif weather_id == 801:
            return "🌤"
        elif weather_id == 802:
            return "⛅"
        elif weather_id == 803:
            return "🌥"
        elif weather_id == 804:
            return "☁"
        else:
            return ""

    def transform_weather_json(self, json_data):
        tz_offset = json_data.get("timezone", 0)
        tz = datetime.timezone(datetime.timedelta(seconds=tz_offset))
        return {
            "location_id": json_data["id"],
            "weather_id": json_data["weather"][0]["id"],
            "weather_main": json_data["weather"][0]["main"],
            "weather_description": json_data["weather"][0]["description"],
            "temp": json_data["main"]["temp"],
            "feels_like": json_data["main"]["feels_like"],
            "temp_min": json_data["main"]["temp_min"],
            "temp_max": json_data["main"]["temp_max"],
            "pressure": json_data["main"]["pressure"],
            "humidity": json_data["main"]["humidity"],
            "visibility": json_data.get("visibility", None),
            "wind_speed": json_data["wind"]["speed"],
            "wind_dir": json_data["wind"].get("deg", None),
            "wind_gust": json_data["wind"].get("gust", None),
            "clouds": json_data["clouds"]["all"],
            "sunrise": datetime.datetime.fromtimestamp(json_data['sys']['sunrise'], tz=tz).strftime('%H:%M:%S'),
            "sunset": datetime.datetime.fromtimestamp(json_data['sys']['sunset'], tz=tz).strftime('%H:%M:%S'),
            "dt": datetime.datetime.fromtimestamp(json_data['dt']),
            "raw_json": json.dumps(json_data)
        }

    def toggle_map_dock(self):
        if self.map_dock is None:
            lat = lon = None
            if self.weather_data:
                lat = self.weather_data['coord']['lat']
                lon = self.weather_data['coord']['lon']
            self.map_widget = MapWindow(self, lat, lon)
            self.map_dock = QDockWidget("Map", self)
            self.map_dock.setWidget(self.map_widget)
            self.map_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
            self.map_dock.setMinimumWidth(484)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.map_dock)

            self.map_dock.visibilityChanged.connect(self.adjust_window_size)
            self.map_dock.topLevelChanged.connect(self.on_dock_floating)
        else:
            self.map_dock.setVisible(not self.map_dock.isVisible())

    def toggle_db_dock(self):
        if self.db_dock is None:
            self.db_dock = QDockWidget("Saved Weather Data", self)
            self.db_dock.setAllowedAreas(Qt.RightDockWidgetArea)
            self.db_dock.setMinimumWidth(484)

            db_dock_widget = QWidget()
            self.db_dock_layout = QVBoxLayout(db_dock_widget)

            hlayout = QHBoxLayout()
            self.save_current_data_button = QPushButton("Save Current", self)
            self.save_current_data_button.setEnabled(False)
            auto_save_city_button = QPushButton("Auto-Save City", self)
            auto_save_city_button.setCheckable(True)
            auto_save_city_button.setChecked(True)
            auto_save_city_button.toggled.connect(self.auto_save_city_data)
            auto_save_coords_button = QPushButton("Auto-Save Coords", self)
            auto_save_coords_button.setCheckable(True)
            auto_save_city_button.toggled.connect(self.auto_save_coords_data)

            btns = [auto_save_city_button, auto_save_coords_button, self.save_current_data_button]
            for btn in btns:
                btn.setFixedHeight(32)
                btn.setStyleSheet("font-size: 20px;"
                                              "font-family: calibri;"
                                              "padding: 0 6 0 6;")
            hlayout.addWidget(self.save_current_data_button)
            hlayout.addWidget(auto_save_city_button)
            hlayout.addWidget(auto_save_coords_button)
            self.db_dock_layout.addLayout(hlayout)

            self.weather_table = QTableWidget()
            self.weather_table.setColumnCount(8)
            self.weather_table.setHorizontalHeaderLabels(["", "City", "Temp", "Weather", "Clouds", "Humidity", "Wind", "Time Collected"])
            self.db_dock_layout.addWidget(self.weather_table)

            self.db_dock.setWidget(db_dock_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.db_dock)

            self.db_dock.setVisible(False)

            self.db_dock.visibilityChanged.connect(self.adjust_window_size)
            self.db_dock.topLevelChanged.connect(self.on_dock_floating)

            self.load_saved_weather_data()
        else:
            is_visible = self.db_dock.isVisible()
            self.db_dock.setVisible(not is_visible)
            if not is_visible:
                self.load_saved_weather_data()

    def on_dock_floating(self, floating):
        sender = self.sender()
        if floating:
            sender.resize(sender.minimumWidth(), 720)

    def adjust_window_size(self):
        base_width = 420
        total_width = base_width

        if self.db_dock and self.db_dock.isVisible() and not self.db_dock.isFloating():
            total_width += self.db_dock.minimumWidth()
        if self.db_dock and not self.db_dock.isVisible() and self.db_dock.isFloating():
            self.db_dock.setFloating(False)

        if self.map_dock and self.map_dock.isVisible() and not self.map_dock.isFloating():
            total_width += self.map_dock.minimumWidth()
        if self.map_dock and not self.map_dock.isVisible() and self.map_dock.isFloating():
            self.map_dock.setFloating(False)

        self.setMinimumWidth(total_width)

        if ((not self.db_dock or not self.db_dock.isVisible() or self.db_dock.isFloating()) and
                (not self.map_dock or not self.map_dock.isVisible() or self.map_dock.isFloating())):
            self.resize(base_width, 720)

        self.resize(total_width, 720)

    def load_saved_weather_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
        SELECT wd.raw_json, l.name, wd.temp, wd.weather_main, wd.clouds, wd.humidity, wd.wind_speed, wd.dt
        FROM weather_data wd
        JOIN locations l ON wd.location_id = l.id
        ORDER BY wd.dt DESC
        LIMIT 50
    """)
        rows = cursor.fetchall()
        self.weather_table.setRowCount(len(rows))

        for row_i, row_data in enumerate(rows):
            raw_json_str = row_data[0]
            btn = QPushButton("Load")
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, raw=raw_json_str: self.load_weather_from_json(raw))
            self.weather_table.setCellWidget(row_i, 0, btn)
            for col_i, value in enumerate(row_data[1:]):
                table_col = col_i + 1
                if col_i == 1:
                    temp_k = float(value)
                    if self.unit_is_fahrenheit:
                        value = f"{(temp_k * 9 / 5) - 459.67:.1f}°F"
                    else:
                        value = f"{temp_k - 273.15:.1f}°C"
                elif col_i == 2:
                    value = value.title()
                elif col_i == 3 or col_i == 4:
                    value = f"{value}%"
                elif col_i == 5:
                    if self.unit_is_fahrenheit:
                        value = f"{value * 2.237:.1f} mph"
                    else:
                        value = f"{value :.1f} m/s"
                elif col_i == 6:
                    value = value.strftime("%H:%M | %m/%d/%y")

                self.weather_table.setItem(row_i, table_col, QTableWidgetItem(str(value)))

        self.weather_table.resizeColumnsToContents()
        cursor.close()

    def load_weather_from_json(self, raw_json_str):
        self.previous_data = self.weather_data
        self.weather_data = json.loads(raw_json_str)
        self.display_weather()
        self.update_map()
        self.update_save_data_button()

    def db_connect(self):
        try:
            mydb = mc.connect(  host="localhost",
                                user="weather_app",
                                password=os.getenv("DB_PASS"),
                                database="weather_app",
                                use_pure=True)

            if mydb.is_connected():
                print("Connected to MySQL database")
                return mydb
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def save_weather_to_db(self, transformed_data):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id FROM locations WHERE id = %s", (transformed_data["location_id"],))
            result = cursor.fetchone()

            if not result:
                cursor.execute("""
                    INSERT INTO locations (id, name, country, lat, lon, timezone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.weather_data["id"],
                    self.weather_data["name"],
                    self.weather_data["sys"]["country"],
                    self.weather_data['coord']['lat'],
                    self.weather_data['coord']['lon'],
                    self.weather_data["timezone"]
                ))
                self.db_connection.commit()

            insert_query = """
                INSERT INTO weather_data (
                    location_id, weather_id, weather_main, weather_description, temp,
                    feels_like, temp_min, temp_max, pressure, humidity, visibility,
                    wind_speed, wind_dir, wind_gust, clouds, sunrise, sunset, dt, raw_json
                ) VALUES (
                    %(location_id)s, %(weather_id)s, %(weather_main)s, %(weather_description)s,
                    %(temp)s, %(feels_like)s, %(temp_min)s, %(temp_max)s,
                    %(pressure)s, %(humidity)s, %(visibility)s,
                    %(wind_speed)s, %(wind_dir)s, %(wind_gust)s, %(clouds)s,
                    %(sunrise)s, %(sunset)s, %(dt)s, %(raw_json)s
                )
            """

            cursor.execute(insert_query, transformed_data)
            self.db_connection.commit()
            cursor.close()
            self.load_saved_weather_data()
            print("Data saved to DB.")

        except mc.Error as e:
            print(f"SQL Error: {e}")

    def auto_save_city_data(self, checked):
        if checked:
            self.auto_saves_city_data = True
        else:
            self.auto_saves_city_data = False

    def auto_save_coords_data(self, checked):
        if checked:
            self.auto_saves_coords_data = True
        else:
            self.auto_saves_coords_data = False

    def update_save_data_button(self):
        if self.previous_data == self.weather_data:
            self.save_current_data_button.setEnabled(False)
        else:
            self.save_current_data_button.setEnabled(True)

    def save_current_data(self):
        if self.weather_data != self.previous_data:
            self.save_weather_to_db(self.transform_weather_json(self.weather_data))

    def update_map(self):
        if self.map_dock and self.weather_data:
            lat = self.weather_data['coord']['lat']
            lon = self.weather_data['coord']['lon']
            self.map_widget.set_marker(lat, lon)
            self.map_widget.update_coords_display(lat, lon)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())