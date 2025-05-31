from PyQt5.QtCore import pyqtSlot, QObject, QTimer
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QWidget

class MapWindow(QWidget):
    def __init__(self, weather_app, lat=None, lon=None, parent=None):
        super().__init__(parent)
        self.weather_app = weather_app
        self.setWindowTitle("Map")
        self.view = QWebEngineView(self)

        self.lat = lat
        self.lon = lon

        self.coords_display = QLineEdit(self)
        self.coords_display.setReadOnly(True)
        self.coords_display.setPlaceholderText("Click on map to get coordinates")
        self.coords_display.setFixedHeight(30)
        self.coords_display.setStyleSheet("font-size: 20px;")

        self.get_weather_button = QPushButton("Get Weather", self)
        self.get_weather_button.setFixedHeight(32)
        self.get_weather_button.setStyleSheet("font-size: 20px;"
                                              "font-family: calibri;"
                                              "font-weight: bold;"
                                              "padding: 0 15 0 15;")
        self.get_weather_button.clicked.connect(self.on_get_weather_click)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.coords_display)
        hlayout.addWidget(self.get_weather_button)

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.view)
        self.setLayout(vlayout)

        self.channel = QWebChannel()
        self.js_bridge = MapBridge(self)
        self.channel.registerObject('bridge', self.js_bridge)
        self.view.page().setWebChannel(self.channel)

        self.load_map()

    def update_coords_display(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.coords_display.setText(f"{lat:.4f}, {lon:.4f}")

    def on_get_weather_click(self):
        if self.lat is not None and self.lon is not None:
            self.get_weather_button.setEnabled(False)
            self.weather_app.get_weather_by_coords(self.lat, self.lon)
            QTimer.singleShot(5000, lambda: self.get_weather_button.setEnabled(True))

    def load_map(self):
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Map</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
                  crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
                    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
                    crossorigin=""></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>html, body, #map {{ height: 100%; margin: 0; }}</style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                let map = L.map('map', {{worldCopyJump: true}}).setView([{self.lat or 36}, {self.lon or -98}], 3);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                }}).addTo(map);
                let marker = null;
                if ({'true' if self.lat is not None and self.lon is not None else 'false'}) {{
                    marker = L.marker([{self.lat}, {self.lon}]).addTo(map);
                }}
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.bridge = channel.objects.bridge;
                }});
                map.on('click', function(e) {{
                    if (marker) {{ marker.setLatLng(e.latlng); }}
                    else {{ marker = L.marker(e.latlng).addTo(map); }}
                    if (window.bridge) {{
                        window.bridge.mapClicked(e.latlng.lat, e.latlng.lng);
                    }}
                }});
            </script>
        </body>
        </html>
        '''
        self.view.setHtml(html)

    def set_marker(self, lat, lon):
        js = f"""
        if (typeof marker !== 'undefined' && marker) {{
            marker.setLatLng([{lat}, {lon}]);
        }} else {{
            marker = L.marker([{lat}, {lon}]).addTo(map);
        }}
        map.setView([{lat}, {lon}], map.getZoom());
        """
        self.view.page().runJavaScript(js)

class MapBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(float, float)
    def mapClicked(self, lat, lon):
        if self.parent:
            self.parent.update_coords_display(lat, lon)