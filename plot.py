import logging
from typing import Tuple, Union, List, Dict
from matplotlib.pyplot import subplot
from matplotlib.figure import Figure


class PlotManager:
    X_LABEL = "Time (mS)"
    Y_LABEL = "Magnitude of EMG"
    DPI = 60
    FIGSIZE=(12,2)
    SUBPLOT_KEY = "figure"
    FIGURE_KEY = "subplot"

    def __init__(self, num_plots: int) -> None:
        # style.use('fivethirtyeight')
        self._plots: List[Dict[str, Union[Figure, subplot]]] = []
        for i in range(0, num_plots):
            self._plots.append({
                PlotManager.FIGURE_KEY : Figure(figsize=PlotManager.FIGSIZE, dpi=PlotManager.DPI, constrained_layout=True, frameon=False)
            })
            self._plots[i][PlotManager.SUBPLOT_KEY] = self._plots[i][PlotManager.FIGURE_KEY].add_subplot(111, frame_on=False, axisbelow=False)
            self._plots[i][PlotManager.SUBPLOT_KEY].xaxis.set_visible(False)
            self._plots[i][PlotManager.SUBPLOT_KEY].yaxis.set_visible(False)

    def ax(self, index: int) -> subplot:
        try:
            return self._plots[index][PlotManager.SUBPLOT_KEY]
        except:
            logging.error("Plot not found")
            return 

    def fig(self, index: int) -> Figure:
        return self._plots[index][PlotManager.FIGURE_KEY]

    def redraw(self, index: int):
        self._plots[index][PlotManager.SUBPLOT_KEY].cla()
        return self
    
    def plot(self, index: int, data: List[int]):
        self._plots[index][PlotManager.SUBPLOT_KEY].plot(data, color='purple')
        return self

    def get_size_pixels(self, index: int) -> Tuple(float, float):
        (w, h) = self._plots[index][PlotManager.FIGURE_KEY].get_size_inches()
        return (w * PlotManager.DPI, h * PlotManager.DPI)

    def set_size_pixels(self, index: int, w: int, h: int) -> Figure:
        self._plots[index][PlotManager.FIGURE_KEY].set_size_inches(float(w) / PlotManager.DPI, float(h) / PlotManager.DPI)
        return self.fig(index)