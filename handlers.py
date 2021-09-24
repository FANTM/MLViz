from threading import Event, Thread
from typing import Any, Callable, Dict
import PySimpleGUI as sg
from DataPool import DATA_POOL, DataPool
from layout import LayoutManager

EVENT_CALLBACK = Callable[[sg.Window, Dict[str, Any]], None]

SAVE_FINISHED_EVENT = Event()

def on_record(window: sg.Window, values: Dict[str, Any]) -> None:
    DATA_POOL.recording = True

def on_stop(window: sg.Window, values: Dict[str, Any]) -> None:
    DATA_POOL.recording = False

def on_clear(window: sg.Window, values: Dict[str, Any]) -> None:
    DATA_POOL.clear()

def save_data(data: DataPool, filename: str) -> None:
    with open(filename, "w") as f:
        f.writelines(data.to_csv())
    SAVE_FINISHED_EVENT.set()

def on_save(window: sg.Window, values: Dict[str, Any]) -> None:
    try:
        t: Thread = Thread(target=save_data, args=(DATA_POOL, values[LayoutManager.Key.FILENAME]))
        window[LayoutManager.Key.FILENAME].update(disabled=True)
        window[LayoutManager.Key.RECORD].update(disabled=True)
        window[LayoutManager.Key.SAVE].update(disabled=True)
        window[LayoutManager.Key.CLEAR].update(disabled=True)
        window[LayoutManager.Key.STOP].update(disabled=True)
        t.start()
    except Exception as e:
        sg.Popup("Failed to write to file: {}".format(e))

# TODO Making number of channels dynamic is surprisingly hard.
def on_num_devlprs_change(window: sg.Window, values: Dict[str, Any]) -> None:
    sg.popup("Please don't use me, Im under construction.")
    # new_num_devlprs = int(values[LayoutManager.Key.NUM_DEVLPRS])
    # LayoutManager.NUM_ROWS = new_num_devlprs

EVENT_HANDLERS: Dict[LayoutManager.Key, EVENT_CALLBACK] = {
    LayoutManager.Key.STOP: on_stop,
    LayoutManager.Key.RECORD: on_record,
    LayoutManager.Key.CLEAR: on_clear,
    LayoutManager.Key.SAVE: on_save,
    LayoutManager.Key.NUM_DEVLPRS: on_num_devlprs_change,
}