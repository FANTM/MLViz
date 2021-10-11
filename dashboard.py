#!/usr/bin/env python
from tkinter import Canvas
from typing import List

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pydevlpr import stop
from ml_tools import MLResources

from DataPool import DATA_POOL
from EventHandler import SAVE_FINISHED_EVENT, EventHandler
from LayoutManager import LayoutManager
from PlotManager import PlotManager

#sg.theme('Reddit')

# Yet another usage of MatPlotLib with animations.

def draw_figure(canvas: Canvas, figure: Figure, loc=(0, 0)) -> FigureCanvasTkAgg:
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=2)
    return figure_canvas_agg

def update_plot(plot_manager: PlotManager, index: int, fig_agg: FigureCanvasTkAgg) -> None:
    plot_manager.redraw(index).plot(index, DATA_POOL.circular_buffers[index])
    fig_agg.draw()

def main() -> None:    
    # define the form layout 
    layout = LayoutManager()

    # draw the initial plot in the window
    plot = PlotManager(LayoutManager.NUM_ROWS)
    
    # create the form and show it without the plot
    window: sg.Window = sg.Window('MLViz',
                layout(), location=(100,100), use_ttk_buttons=True, finalize=True)
    
    # create the event overseer
    event_handlers = EventHandler(window, plot)
    
    window.hide()
    fig_aggs: List[FigureCanvasTkAgg] = []
    canvases: List[Canvas] = []

    for i in range(0, LayoutManager.NUM_ROWS):    
        canvas_elem = window['canvas_{}'.format(i)]
        canvases.append(canvas_elem.TKCanvas)
        fig_aggs.append(draw_figure(canvases[i], plot.fig(i)))

    window.read(timeout=0)
    window.un_hide()
    # need to initialize the ML resources
    MLResources.initialize(DATA_POOL, window)
    # spin forever until exit
    while True:
        event, values = window.read(timeout=10)
        if event in ('Exit', None):
            break
        
        if SAVE_FINISHED_EVENT.is_set():
            window[LayoutManager.Key.FILENAME].update(disabled=False)
            window[LayoutManager.Key.RECORD].update(disabled=False)
            window[LayoutManager.Key.SAVE].update(disabled=False)
            window[LayoutManager.Key.CLEAR].update(disabled=False)
            window[LayoutManager.Key.STOP].update(disabled=False)
            SAVE_FINISHED_EVENT.clear()

        event_handlers.handle_event(event, window, values)

        for i in range(0, LayoutManager.NUM_ROWS):
            update_plot(plot, i, fig_aggs[i])
        
    stop()
    MLResources.cleanup()
    window.close()

if __name__ == '__main__':
    main()
