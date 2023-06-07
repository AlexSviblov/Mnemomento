import PyQt5
from PyQt5 import QtCore, QtWebEngineWidgets
import folium
import jinja2
import logging


# переделанный класс для работы с вебом, который генерируется JS'ом, который генерируется шаблонами
class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    coordinates_transfer = QtCore.pyqtSignal(str)

    # перехват сообщений, которые кидает JS в консоль, сообщение в консоль я плюю сам в шаблоне класса folium.features.ClickForLatLng
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        try:
            float(msg.split(',')[0])
            float(msg.split(',')[1])
        except ValueError:
            logging.info(f"JS map message: {msg}")
        else:
            self.coordinates_transfer.emit(msg)


class ClickForLatLng(folium.features.ClickForLatLng):

    _template = jinja2.Template(
        """
            {% macro script(this, kwargs) %}
                function getLatLng(e){
                    var lat = e.latlng.lat.toFixed(4),
                        lng = e.latlng.lng.toFixed(4);
                    var txt = {{this.format_str}};
                    console.log(txt);
                    };
                {{this._parent.get_name()}}.on('click', getLatLng);
            {% endmacro %}
            """
    )  # noqa

    def __init__(self, format_str=None, alert=True):
        super().__init__()
        self._name = "ClickForLatLng"
        self.format_str = format_str or 'lat + "," + lng'
        self.alert = alert


class LatLngPopup(folium.features.LatLngPopup):
    """
    When one clicks on a Map that contains a LatLngPopup,
    a popup is shown that displays the latitude and longitude of the pointer.

    """

    _template = jinja2.Template(
        """
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Широта: " + e.latlng.lat.toFixed(4) +
                                    "<br>Долгота: " + e.latlng.lng.toFixed(4))
                        .openOn({{this._parent.get_name()}});
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """
    )  # noqa

    def __init__(self):
        super().__init__()
        self._name = "LatLngPopup"
