from datetime import datetime

import gi
from matplotlib import rcParams
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure

from halo.API import OpenWeatherMap
from halo.DataStore import DataStore
from halo.Icon import Icon
from halo.settings import DISPLAY_TEMP_UNITS

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Lato']


class SummaryView:
    """
    Display the trends chart and daily summary of weather data.
    """

    def __init__(self, single_day_mode: bool = False):
        """
        Initialises charting and summary.

        :param single_day_mode: Set to true to render
        summary of single item(used in historic view).
        """
        self.single_day_mode = single_day_mode
        self.chart_data = []
        self.view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.chart = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.summary = Gtk.Box(spacing=10)
        self.label = Gtk.Label()
        self.label.set_name('f_temp')

        # Dynamically create widgets.
        self.items = []
        for _ in range(1) if single_day_mode else range(5):
            item = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            temperature = Gtk.Label()
            time = Gtk.Label()
            status = Gtk.Image()
            temperature.set_name("f_temp")
            time.set_name("f_time")

            item.pack_start(temperature, False, False, 0)
            item.pack_start(status, False, False, 0)
            item.pack_start(time, False, False, 0)
            self.items.append([status, temperature, time])
            self.summary.pack_start(item, True, True, 10)

        # Initializing and Formatting Charts
        self.fig = Figure(figsize=(5, 1), dpi=100)
        self.axis = self.fig.add_subplot(111)

        self.fig.patch.set_facecolor("None")
        self.axis.patch.set_visible(False)
        self.axis.spines['top'].set_visible(False)
        self.axis.spines['right'].set_visible(False)
        self.axis.spines['bottom'].set_visible(False)
        self.axis.spines['left'].set_visible(False)
        self.axis.get_xaxis().set_ticks([])
        self.axis.tick_params(axis='y', colors='white')

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(500, 100)

        self.canvas.mpl_connect('motion_notify_event', self.hover)
        self.canvas.mpl_connect('axes_leave_event', self.hide_label)
        self.chart.pack_start(self.label, True, True, 0)
        self.chart.pack_start(self.canvas, True, True, 0)

        self.view.pack_start(self.chart, False, False, 20)
        self.view.pack_start(self.summary, False, False, 15)

        self._store = DataStore()

    def get_view(self) -> Gtk.Box:
        """
        Returns the view object for rendering ui.

        :return: View
        """
        return self.view

    def render(self, weather_data: list, chart_data: list):
        """
        Update the GUI data.

        :param weather_data: Weather data
        :param chart_data: Charting data
        """
        self.chart_data = chart_data
        self._store.refresh_preference()
        # Summary
        for weather, box in zip(weather_data, self.items):
            box[2].set_text(str(int(weather['main']['temp'])) + DISPLAY_TEMP_UNITS[self._store.get_units()])
            box[1].set_text(datetime.fromtimestamp(weather['dt']).strftime("%-I %p"))
            if not self.single_day_mode:
                box[0].set_from_pixbuf(Icon.get_icon(OpenWeatherMap.get_icons(weather['weather'][0]['icon'])))
        if self.single_day_mode:
            self.items[0][1].set_text("Yesterday")

        # Chart
        self.axis.clear()
        self.axis.patch.set_visible(False)
        self.axis.get_xaxis().set_ticks([])
        self.axis.plot(list(range(len(chart_data))), self.chart_data, 'w-')

    def hover(self, event: MouseEvent):
        if event.inaxes is not self.axis:
            return
        x = int(event.xdata)
        if x >= len(self.chart_data) or x < 0:
            return
        self.label.set_text(str(self.chart_data[x]) + DISPLAY_TEMP_UNITS[self._store.get_units()])

    def hide_label(self, event):
        self.label.set_text("")
