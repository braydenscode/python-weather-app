import datetime


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


def daytime_check(weather_data):
    if weather_data:
        sunrise_timestamp = weather_data["sys"]["sunrise"]
        sunset_timestamp = weather_data["sys"]["sunset"]
        timezone_offset = weather_data["timezone"]

        sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp, tz=datetime.timezone(
            datetime.timedelta(seconds=timezone_offset)))
        sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp,
                                                      tz=datetime.timezone(datetime.timedelta(seconds=timezone_offset)))
        current_local_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=timezone_offset)))

        is_daytime = sunrise_time < current_local_time < sunset_time
        return is_daytime
    return None