import os
import mysql.connector as mc
from PyQt5.QtWidgets import QPushButton, QTableWidgetItem
import datetime
import json


def db_connect():
    try:
        mydb = mc.connect(host="localhost",
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
    if self.db_connection is None or not self.db_connection.is_connected():
        print("Database is not connected.\tNo weather data was saved.")
        return
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
        load_saved_weather_data(self)
        print("Data saved to DB.")

    except mc.Error as e:
        print(f"SQL Error: {e}")


def load_saved_weather_data(self):
    if self.db_connection is None or not self.db_connection.is_connected():
        print("Database is not connected.\tNo weather data was loaded.")
        return
    try:
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
    except mc.Error as e:
        print(f"SQL Error: {e}")


def transform_weather_json(json_data):
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
