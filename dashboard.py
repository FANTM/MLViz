#!/usr/bin/env python
import logging
from tkinter import Canvas
from typing import Callable, List

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pydevlpr import add_callback, remove_callback, stop

from DataPool import DATA_POOL
from handlers import EVENT_HANDLERS, SAVE_FINISHED_EVENT
from layout import LayoutManager
from plot import PlotManager

sg.theme('Reddit')

# Yet another usage of MatPlotLib with animations.

def data_add(index: int) -> Callable[[str], None]:
    def data_add_internal(data: str):
        DATA_POOL.append(index, int(data))
        # CENTER[index].append(int(data))
        # avg = sum(CENTER[index]) / len(CENTER[index])
        # BUFFER[index].append(FILTERS[index].next_sample(int(data) - avg))
    return data_add_internal

PYDEVLPR_CALLBACKS = [data_add(i) for i in range(0, LayoutManager.NUM_ROWS)]

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
    window: sg.Window = sg.Window('DEVLPR Data Pal',
                layout(), use_ttk_buttons=True, finalize=True)
    window.hide()
    fig_aggs: List[FigureCanvasTkAgg] = []
    canvases: List[Canvas] = []

    for i in range(0, LayoutManager.NUM_ROWS):    
        canvas_elem = window['canvas_{}'.format(i)]
        canvases.append(canvas_elem.TKCanvas)
        # col_with_canvas = window['canvas_col_{}'.format(i)]
        fig_aggs.append(draw_figure(canvases[i], plot.fig(i)))

    window.read(timeout=0)
    window.un_hide()
    # make a bunch of random data points
    while True:
        event, values = window.read(timeout=10)
        print(event)
        if event in ('Exit', None):
            break
        
        if SAVE_FINISHED_EVENT.is_set():
            window[LayoutManager.Key.FILENAME].update(disabled=False)
            window[LayoutManager.Key.RECORD].update(disabled=False)
            window[LayoutManager.Key.SAVE].update(disabled=False)
            window[LayoutManager.Key.CLEAR].update(disabled=False)
            window[LayoutManager.Key.STOP].update(disabled=False)
            SAVE_FINISHED_EVENT.clear()

        try:
            EVENT_HANDLERS[event](window, values)
        except KeyError:
            pass

        for i in range(0, LayoutManager.NUM_ROWS):
            if event == 'connect_{}'.format(i):
                topic = values['topic_{}'.format(i)]
                pin = int(window['pin_{}'.format(i)].metadata["pin"])
                try:
                    print( PYDEVLPR_CALLBACKS[i])
                    add_callback(topic, pin, PYDEVLPR_CALLBACKS[i])
                    window['row_{}'.format(i)].update('{}'.format(topic))
                    col_w, col_h = window['canvas_col_{}'.format(i)].get_size()
                    plot.set_size_pixels(i, col_w, col_h)
                except Exception as e:
                    logging.info("TOPIC: {} PIN: {}".format(topic, pin))
                    logging.error(e)
                    sg.popup("Make sure to select a topic and pin!")
            if event == 'disconnect_{}'.format(i):
                try:
                    topic = values['topic_{}'.format(i)]
                    pin = int(window['pin_{}'.format(i)].metadata["pin"])
                    print( PYDEVLPR_CALLBACKS[i])
                    remove_callback(topic, pin, PYDEVLPR_CALLBACKS[i])
                except:
                    logging.error("failed: topic: {}, pin: {}".format(topic, pin))
                    sg.popup("Failed to remove the callback, try to set topic to the ")
        for i in range(0, LayoutManager.NUM_ROWS):
            update_plot(plot, i, fig_aggs[i])
        
    stop()
    window.close()

if __name__ == '__main__':
    main()
