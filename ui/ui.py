from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect

from weather_api import get_weather_by_city


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

    add_text_shadow(self, self.city_label, Qt.white, (0, 0), 50)
    add_text_shadow(self, self.temperature_label)
    add_text_shadow(self, self.temperature_label_advanced)
    add_text_shadow(self, self.description_label)
    add_text_shadow(self, self.description_label_advanced)

    add_text_shadow(self, self.clouds_label)
    add_text_shadow(self, self.humidity_label)
    add_text_shadow(self, self.wind_speed_label)

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

    self.city_input.returnPressed.connect(lambda: get_weather_by_city(self))
    self.get_weather_button.clicked.connect(lambda: get_weather_by_city(self))
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


def get_weather_gradient(weather_data, is_daytime):
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

    top_color = "#a1c4fd"
    bottom_color = "#c2e9fb"

    if weather_data:
        weather_main = weather_data["weather"][0]["main"]
        top_color, bottom_color = WEATHER_GRADIENTS.get(weather_main, (top_color, bottom_color))

        if weather_main == "Clear":
            key = "Clear_day" if is_daytime else "Clear_night"
        elif weather_main == "Clouds":
            key = "Clouds_day" if is_daytime else "Clouds_night"
        elif weather_main == "Rain":
            key = "Rain_day" if is_daytime else "Rain_night"
        elif weather_main == "Drizzle":
            key = "Drizzle_day" if is_daytime else "Drizzle_night"
        elif weather_main == "Thunderstorm":
            key = "Thunderstorm_day" if is_daytime else "Thunderstorm_night"
        else:
            key = weather_main

        top_color, bottom_color = WEATHER_GRADIENTS.get(key, (top_color, bottom_color))
        return top_color, bottom_color
    return top_color, bottom_color
