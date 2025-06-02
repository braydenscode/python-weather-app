import datetime
import json
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QBrush, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QStackedWidget, QMainWindow, QDockWidget, QTableWidget

from db import db_connect, save_weather_to_db, load_saved_weather_data, transform_weather_json
from ui.ui import initUI, get_weather_gradient
from utils import convert_to_f, convert_to_c, get_direction_arrow, daytime_check
from widgets.map import MapWindow


class WeatherApp(QMainWindow):
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

        initUI(self)
        self.db_connection = db_connect()
        self.toggle_db_dock()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        top_color, bottom_color = get_weather_gradient(self.weather_data, daytime_check(self.weather_data))

        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(top_color))
        gradient.setColorAt(1, QColor(bottom_color))

        painter.fillRect(rect, QBrush(gradient))

    def display_weather(self):
        if self.weather_data:
            self.is_daytime = daytime_check(self.weather_data)
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

            if self.unit_is_fahrenheit:
                self.temperature_label.setText(f"{convert_to_f(self.weather_data['main']['temp']):.0f}°F")
                self.wind_speed_label.setText(f"Wind\n{self.weather_data['wind']['speed'] * 2.237:.1f} mph")
                self.wind_speed_label_advanced.setText(
                    f"Wind Speed\n{self.weather_data['wind']['speed'] * 2.237:.1f} mph")
                self.feels_like_temp_label.setText(
                    f"Feels Like\n{convert_to_f(self.weather_data['main']['feels_like']):.0f}°")
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
                self.feels_like_temp_label.setText(
                    f"Feels Like\n{convert_to_c(self.weather_data['main']['feels_like']):.0f}°")
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
            load_saved_weather_data(self)

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
            self.save_current_data_button.clicked.connect(self.save_current_data)
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
            self.weather_table.setHorizontalHeaderLabels(
                ["", "City", "Temp", "Weather", "Clouds", "Hm", "Wind", "Time Collected"])
            self.db_dock_layout.addWidget(self.weather_table)

            self.db_dock.setWidget(db_dock_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.db_dock)

            self.db_dock.setVisible(False)

            self.db_dock.visibilityChanged.connect(self.adjust_window_size)
            self.db_dock.topLevelChanged.connect(self.on_dock_floating)

            load_saved_weather_data(self)
        else:
            is_visible = self.db_dock.isVisible()
            self.db_dock.setVisible(not is_visible)
            if not is_visible:
                load_saved_weather_data(self)

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

    def load_weather_from_json(self, raw_json_str):
        self.previous_data = self.weather_data
        data = json.loads(raw_json_str)
        self.weather_data = data
        self.is_daytime = daytime_check(data)
        self.display_weather()
        self.update_map()
        self.update_save_data_button()

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
            save_weather_to_db(self, transform_weather_json(self.weather_data))

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
