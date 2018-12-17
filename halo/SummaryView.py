from datetime import datetime

import gi
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib import rcParams

from halo.Icon import Icon

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Lato']


class SummaryView:
    """
    Display the trends chart and daily summary of weather data.
    """
    def __init__(self, single_day_mode=False):
        """
        Initialises charting and summary.
        :param single_day_mode: Set to true to render summary of single item(used in historic view).
        """
        self.single_day_mode = single_day_mode
        self.view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.chart = Gtk.Box(spacing=10)
        self.summary = Gtk.Box(spacing=10)

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

        canvas = FigureCanvas(self.fig)
        canvas.set_size_request(500, 100)
        self.chart.pack_start(canvas, True, True, 0)

        self.view.pack_start(self.chart, False, False, 20)
        self.view.pack_start(self.summary, False, False, 15)

    def get_view(self):
        """
        Returns the view object for rendering ui.
        :return: View
        """
        return self.view

    def render(self, weather_data, chart_data):
        # Summary
        for weather, box in zip(weather_data, self.items):
            box[2].set_text(str(int(weather['temp'])) + "°C")
            box[1].set_text(datetime.fromtimestamp(weather['ts']).strftime("%a"))
            if not self.single_day_mode:
                box[0].set_from_pixbuf(Icon.get_icon(weather['weather']['code']))

        self.items[0][1].set_text("Yesterday" if self.single_day_mode else "Today")

        # Chart
        self.axis.clear()
        self.axis.patch.set_visible(False)
        self.axis.get_xaxis().set_ticks([])
        self.axis.plot(list(range(len(chart_data))), chart_data, 'w-')
