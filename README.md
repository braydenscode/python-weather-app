# 🌤️ Python Real-Time Weather App
A real-time weather application built with Python and PyQt5.
> 🧠 Inspired by the final project of Bro Code's 2024 Python Course.
<br/>

![python_b8EQaXSfHC](https://github.com/user-attachments/assets/5e1c519d-e2f1-4a35-8558-1f307ff75320)

## ✨ Features
- Real-Time Weather Retrieval by City
- Real-Time Map-Based Weather Retrieval
- Compact and Advanced Display Modes
- Unit Switching (Imperial/Metric)
- Weather Condition Emojis
- Dynamic Background Gradient
- Flag Indicator for Country
- MySQL Database Integration
- Manual and Auto-Save Options
- Loading of Saved Entries
- Docked Table of Saved Data
- Docked Interactive Map

## 🛠️ Installation
<details><summary><b>Set Up MySQL Database</b></summary>

  1. Create a new SQL tab and execute this query to set up schema and tables.

  ```
CREATE DATABASE IF NOT EXISTS weather_app;
USE weather_app;

CREATE TABLE IF NOT EXISTS locations (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(2),
    timezone INT,
    lat FLOAT,
    lon FLOAT
);

CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    weather_id INT,
    weather_main VARCHAR(50),
    weather_description VARCHAR(255),
    temp FLOAT,
    feels_like FLOAT,
    temp_min FLOAT,
    temp_max FLOAT,
    pressure INT,
    humidity INT,
    visibility INT,
    wind_speed FLOAT,
    wind_dir INT,
    wind_gust FLOAT,
    clouds INT,
    sunrise TIME,
    sunset TIME,
    dt DATETIME,
    raw_json JSON,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);
  ```
  2. Create a new SQL tab and execute this query to set up account and password. (Replace with your own password)
    
    CREATE USER IF NOT EXISTS 'weather_app'@'localhost' IDENTIFIED BY 'your_password_here';
    GRANT ALL PRIVILEGES ON weather_app.* TO 'weather_app'@'localhost';
    FLUSH PRIVILEGES;

</details>

<details><summary><b>Run Instructions</b></summary>

1. Clone Repo:

    ```
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. Create a Virtual Environment:

    ```
    python -m venv .venv
    ```

3. Activate Virtual Environment:

    - Bash
    ```sh
    source .venv/bin/activate
    ```
    - cmd
    ```cmd
    .venv\Scripts\activate
    ```

4. Install Dependencies:

    ```
      pip install -r requirements.txt
    ```

5. (Temporarily) Set Environment Variables:
    - Bash
    ```sh
    export OPENWEATHER_API_KEY=your_openweather_key
    ```
    - cmd
    ```cmd
    set OPENWEATHER_API_KEY=your_openweather_key
    ```

6. Run the Application:

    ```
      python main.py
    ```
</details>

## 🙌 Acknowledgments
- [BroCode Python Course](https://www.youtube.com/watch?v=ix9cRaBkVe0&t=39966s)

- [OpenWeather API](https://openweathermap.org/api)

- [flagcdn.com](https://flagcdn.com/)

- [Leaflet.js](https://leafletjs.com/)
