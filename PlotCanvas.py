from typing import List, Any


from PySide6.QtWidgets import (QWidget, QSizePolicy)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    """Matplotlib-Canvas, der in die Qt-GUI eingebettet wird."""

    def __init__(self, parent: QWidget = None, width: float = 5, height: float = 4, dpi: int = 100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.fig.set_facecolor('#19232D')  # Hintergrundfarbe des gesamten Plots

        # Achsen konfigurieren
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#19232D')  # Hintergrundfarbe des Diagramms
        self.ax.title.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(axis='both', colors='white')

        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setParent(parent)

    def plot(self, x_data: List[Any], y_data: List[Any], title: str = "", x_label: str = "", y_label: str = "",
             diagram_typ: str = "Linie", color: str = "lime", legend: bool = False, legend_title=None, legend_text=None,
             colorbar: bool = False
             ):
        """
        Plottet die übergebenen Daten anhand der gewünschten Parameter.

        :param x_data: Daten für die x-Achse.
        :param y_data: Daten für die y-Achse.
        :param title: Plot-Titel.
        :param x_label: Beschriftung der x-Achse.
        :param y_label: Beschriftung der y-Achse.
        :param diagram_typ: Typ des Diagramms: "Linie", "Scatter" oder "Bar".
        :param color: Farbe der Darstellung.
        :param legend: Ob eine Legende angezeigt wird.
        :param legend_title: Titel der Legende.
        :param legend_text: Text der Legende.
        :param colorbar: Ob ein Colorbar hinzugefügt wird (gilt vor allem für Scatter-Plots).
        """
        self.ax.clear()
        label = f"{x_label} vs. {y_label}"

        if diagram_typ == "Linie":
            self.ax.plot(x_data, y_data, marker='', linestyle='-', color=color, label=label)
        elif diagram_typ == "Scatter":
            self.ax.scatter(x_data, y_data, c=color, label=label)
            if colorbar:
                # self.fig.colorbar(matplotlib.cm.ScalarMappable(cmap='OrRd'), ax=self.ax)
                pass
        elif diagram_typ == "Bar":
            self.ax.bar(x_data, y_data, color=color, label=label)
        else:
            self.ax.plot(x_data, y_data, marker='', linestyle='-', c=color, label=label)

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # Textfarbe ändern
        self.ax.title.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(axis='both', colors='white')

        # Grid konfigurieren
        self.ax.grid(True, axis='both', color='#404240', linestyle='-', linewidth=1)

        # Legende anpassen
        if legend:
            leg = self.ax.legend() if not legend_title else self.ax.legend(title=legend_title)
            leg.get_frame().set_facecolor('#19232D')
            leg.get_title().set_color('white')

            for text in leg.get_texts():
                text.set_text(legend_text if legend_text else text.get_text())
                text.set_color('white')

        self.draw()
