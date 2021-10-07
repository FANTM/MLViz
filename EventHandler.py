import logging
from threading import Event, Thread
from typing import Any, Callable, Dict, Tuple
import PySimpleGUI as sg
from DataPool import DATA_POOL, DataPool
from LayoutManager import LayoutManager
from pydevlpr import add_callback, remove_callback
from ml_tools import MLOptions, MLResources


EVENT_CALLBACK = Callable[[sg.Window, Dict[str, Any]], None]

SAVE_FINISHED_EVENT = Event()

class EventHandler:
    def __init__(self, window, plot):
        self.pydevlpr_callbacks = {}
        self.plot = plot
        self.handlers: Dict[LayoutManager.Key, EVENT_CALLBACK] = {
            LayoutManager.Key.STOP: EventHandler.on_stop,
            LayoutManager.Key.RECORD: EventHandler.on_record,
            LayoutManager.Key.CLEAR: EventHandler.on_clear,
            LayoutManager.Key.SAVE: EventHandler.on_save,
            LayoutManager.Key.NUM_DEVLPRS: EventHandler.on_num_devlprs_change,
            LayoutManager.Key.TRAIN: EventHandler.on_train,
            LayoutManager.Key.LOAD: EventHandler.on_load_model,
        }
        for i in range(0, LayoutManager.NUM_ROWS):
            connect_key = LayoutManager.Key.CONNECT_TEMPLATE.format(i)
            disconnect_key = LayoutManager.Key.DISCONNECT_TEMPLATE.format(i)
            self.handlers[connect_key] = self.generate_connect_handler(i)
            self.handlers[disconnect_key] = self.generate_disconnect_handler(i)

        for i in range(0, LayoutManager.NUM_LABELS):
            key_base = LayoutManager.Key.LABEL_BUTTON_TEMPLATE.format(i)
            window[key_base].bind('<Button-1>', LayoutManager.Key.BTN_PRESS)
            window[key_base].bind('<ButtonRelease-1>', LayoutManager.Key.BTN_RLSE)
            press_handler, release_handler = self.generate_label_handlers(i)

            self.handlers[key_base + LayoutManager.Key.BTN_PRESS] = press_handler
            self.handlers[key_base] = release_handler  # Not intuitive, but callback for release is just key

    def generate_pydevlpr_callback(self, index):
        def add_data(data: str):
            DATA_POOL.append(index, float(data))
        return add_data

    def generate_label_handlers(self, index) -> Tuple[EVENT_CALLBACK, EVENT_CALLBACK]:
        def on_press_label(window: sg.Window, values: Dict[str, Any]):
            label = values[LayoutManager.Key.LABEL_INPUT_TEMPLATE.format(index)]
            DATA_POOL.label = label
        def on_release_label(window: sg.Window, values: Dict[str, Any]):
            DATA_POOL.label = 'None'
        return (on_press_label, on_release_label)

    def generate_connect_handler(self, index) -> EVENT_CALLBACK:
        def on_connect(window: sg.Window, values: Dict[str, Any]):
            topic = values[LayoutManager.Key.TOPIC_TEMPLATE.format(index)]
            pin = values[LayoutManager.Key.PIN_TEMPLATE.format(index)]
            try:
                if index in self.pydevlpr_callbacks.keys():
                    remove_callback(self.pydevlpr_callbacks[index]["topic"], self.pydevlpr_callbacks[index]["pin"], self.pydevlpr_callbacks[index]["callback"])
                self.pydevlpr_callbacks[index] = {   
                        "topic": topic,
                        "pin": pin,
                        "callback": self.generate_pydevlpr_callback(index)
                    }
                add_callback(topic, pin, self.pydevlpr_callbacks[index]["callback"])
                window[LayoutManager.Key.ROW_TEMPLATE.format(index)].update('{}'.format(topic))
                col_w, col_h = window['canvas_col_{}'.format(index)].get_size()
                self.plot.set_size_pixels(index, col_w, col_h)
                window[LayoutManager.Key.CONNECT_TEMPLATE.format(index)].update(disabled=True)
            except Exception as e:
                logging.info("TOPIC: {} PIN: {}".format(topic, pin))
                logging.error(e)
                sg.popup("Make sure to select a topic and pin!")
        return on_connect

    def generate_disconnect_handler(self, index) -> EVENT_CALLBACK:
        def on_disconnect(window: sg.Window, values: Dict[str, Any]):
            try:
                remove_callback(self.pydevlpr_callbacks[index]["topic"], self.pydevlpr_callbacks[index]["pin"], self.pydevlpr_callbacks[index]["callback"])
                del self.pydevlpr_callbacks[index]
            except Exception as e:
                logging.error(e)
                sg.popup("Failed to remove the callback")
        return on_disconnect

    def handle_event(self, event, window, values):
        try:
            self.handlers[event](window, values)
        except KeyError:
            pass

    @staticmethod
    def on_record(window: sg.Window, values: Dict[str, Any]) -> None:
        DATA_POOL.recording = True

    @staticmethod
    def on_stop(window: sg.Window, values: Dict[str, Any]) -> None:
        DATA_POOL.recording = False

    @staticmethod
    def on_clear(window: sg.Window, values: Dict[str, Any]) -> None:
        DATA_POOL.clear()
    
    @staticmethod
    def save_data(data: DataPool, filename: str) -> None:
        with open(filename, "w") as f:
            f.writelines(data.to_csv())
        SAVE_FINISHED_EVENT.set()

    @staticmethod
    def on_save(window: sg.Window, values: Dict[str, Any]) -> None:
        try:
            t: Thread = Thread(target=EventHandler.save_data, args=(DATA_POOL, values[LayoutManager.Key.FILENAME]))
            window[LayoutManager.Key.FILENAME].update(disabled=True)
            window[LayoutManager.Key.RECORD].update(disabled=True)
            window[LayoutManager.Key.SAVE].update(disabled=True)
            window[LayoutManager.Key.CLEAR].update(disabled=True)
            window[LayoutManager.Key.STOP].update(disabled=True)
            t.start()
        except Exception as e:
            sg.Popup("Failed to write to file: {}".format(e))

    @staticmethod
    def on_train(window: sg.Window, values: Dict[str, Any]) -> None:
        # grab the training data filename and the output model filename
        data_fname = values[LayoutManager.Key.TRAIN_FILENAME]
        modl_fname = values[LayoutManager.Key.SAVEMODEL_FILENAME]
        # create an MLOptions object for our training thread
        ml_opts = MLOptions(data_fname, modl_fname)
        # set any options that are available
        ml_opts.set_standardize(window[LayoutManager.Key.OPT_STANDARDIZE].get())
        # and mark the selected classifier
        if window[LayoutManager.Key.CLF_LINEARSVM].get():
            ml_opts.linearsvc()
        # and grab the train button to be updated
        train_btn = window[LayoutManager.Key.TRAIN]
        MLResources.start_training_job(ml_opts, train_btn)

    @staticmethod
    def on_load_model(window: sg.Window, values: Dict[str, Any]) -> None:
        # grab the desired model file
        model_fname = values[LayoutManager.Key.LOADMODEL_FILENAME]
        # pass that sucker along
        MLResources.load_model(model_fname)
        print(MLResources.ml_model())

    # TODO Making number of channels dynamic is surprisingly hard.
    @staticmethod
    def on_num_devlprs_change(window: sg.Window, values: Dict[str, Any]) -> None:
        sg.popup("Please don't use me, Im under construction.")
        # new_num_devlprs = int(values[LayoutManager.Key.NUM_DEVLPRS])
        # LayoutManager.NUM_ROWS = new_num_devlprs


