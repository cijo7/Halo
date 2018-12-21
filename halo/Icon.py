import gi

from halo.settings import BASE

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf  # noqa: E402


class Icon:
    """
    It is for choosing and retuning Weather icons.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_icon(status: str, size: int = 50) -> GdkPixbuf.Pixbuf:
        """
        Return Weather icons as per status.

        Possible values as follows:
         Thunderstorm: 200 - 233,
         Light: rain 300 - 302,
         Rain: 500 - 522, 900,
         Snow: 600 - 623,
         Smoke: 711,
         Dust: 731,
         Fog: 700 - 751,
         Clear Sky: 800,
         Partial Cloudy: 801 - 803,
         Cloudy: 804
        """
        status = int(status)
        if 200 <= status <= 233:
            name = "wi-thunderstorm"
        elif 300 <= status <= 302:
            name = "wi-rain-mix"
        elif 500 <= status <= 522 or status == 900:
            name = "wi-rain"
        elif 600 <= status <= 623:
            name = "wi-snow"
        elif status == 711:
            name = "wi-smoke"
        elif status == 731:
            name = "wi-dust"
        elif 700 <= status <= 751:
            name = "wi-fog"
        elif status == 800:
            name = "wi-day-sunny"
        elif 801 <= status <= 803:
            name = "wi-day-cloudy"
        else:
            name = "wi-cloudy"

        return GdkPixbuf.Pixbuf.new_from_file_at_scale(
            BASE + "/assets/icon/{}.svg".format(name),
            size, size, True)
