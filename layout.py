import pydevlpr_protocol
import PySimpleGUI as sg
from typing import List


class LayoutManager:

    class Key:
        RECORD = 'record'
        STOP = 'stop'
        CLEAR = 'clear'
        SAVE = 'save'
        FILENAME = 'filename'
        DATA_MANAGER = 'datamanager'
        NUM_DEVLPRS = 'numdevlprs'

    FONT_FAMILY = 'Helvetica'
    FONT_SIZES = {'h1': 24, 'h2': 20, 'h3': 16,
                  'h4': 12, 'p': 10, 'button': 12}
    NUM_ROWS = 3

    def __init__(self):
        self._layout = [
            [    # Rows!                
                LayoutManager.RecordGestureColumn(),
                LayoutManager.Body(LayoutManager.NUM_ROWS),
            ],   # End rows
        ]

    def __call__(self) -> List[sg.Element]:
        return self._layout

    @property
    def layout(self):
        return self._layout

    @staticmethod
    def Body(NUM_ROWS):
        return sg.Column([LayoutManager.DataRow(i) for i in range(0, NUM_ROWS)])

    @staticmethod
    def Button(label, key=None, disabled=False, size=(None, None), pad=None):
        return sg.Button(label, border_width=0, enable_events=True, mouseover_colors=('white', '#004D86'), key=key, disabled=disabled, size=size, pad=pad, font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))

    @staticmethod
    def Text(label, size=(None, None), text_size='p', justification='left'):
        return sg.Text(label, size=size,
                       justification=justification, font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES[text_size]))

    @staticmethod
    def Canvas(size=(None, None), key=None):
        return sg.Canvas(size=size, key=key, expand_x=True, expand_y=True)

    @staticmethod
    def PinSelect(index):
        return sg.Text("Pin: {}".format(index), metadata={"pin": index}, key="pin_{}".format(index), font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['p']))

    @staticmethod
    def TopicSelect(index):
        return LayoutManager.Select("topic_{}".format(index), size=(14, None), values=pydevlpr_protocol.DataTopic.topics())

    @staticmethod
    def Select(key, values, size=(14, None)):
        return sg.Combo(values=values, tooltip=key, readonly=True, enable_events=True, key=key, size=size, font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['p']))

    @staticmethod
    def NumPinSlider():
        return [[
            LayoutManager.Text('Number of DEVLPRS')
        ],
        [
            sg.Slider(range=(1, 6), key=LayoutManager.Key.NUM_DEVLPRS, trough_color="#DAE0E6", relief=sg.RELIEF_FLAT,enable_events=True, default_value=3, resolution=1, tick_interval=1, orientation='h', expand_x=True)
        ]]

    @staticmethod
    def DataRow(index):
        return sg.Frame('Row', key='row_{}'.format(index), expand_x=True, vertical_alignment="center", layout=[
                    [
                        sg.Column([
                            [
                                LayoutManager.TopicSelect(index), LayoutManager.PinSelect(index), 
                            ],
                            [
                                    LayoutManager.Button('Connect', size=(12, 1), key='connect_{}'.format(index)),
                                    LayoutManager.Button('Disconnect', size=(12, 1), key='disconnect_{}'.format(index))
                            ],
                        ]),
                        sg.VerticalSeparator(),
                        sg.Column([
                            [
                                LayoutManager.Canvas( key='canvas_{}'.format(index)), 
                            ]], key="canvas_col_{}".format(index), justification="left", element_justification="left")
                    ]
                ]
                ),
    
    @staticmethod
    def LabelRow(index, default_input):
        return [LayoutManager.Button("Label {}".format(index)), sg.Input(default_input, 
                size=(22, None), font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))]

    @staticmethod
    def RecordGestureColumn():
        return sg.Column([[
            sg.Frame("Data Manager", [
                *LayoutManager.NumPinSlider(),
                [sg.Text('Output Filename')],
                [sg.Input('recording.csv', key=LayoutManager.Key.FILENAME, size=(22, None), font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button'])), 
                    sg.FileBrowse( font=(LayoutManager.FONT_FAMILY, 
                                        LayoutManager.FONT_SIZES['button']))],
                [sg.Text('Labels')],
                LayoutManager.LabelRow(1, 'fist'),
                LayoutManager.LabelRow(2, 'thumb'),
                LayoutManager.LabelRow(3, 'index'),
                LayoutManager.LabelRow(4, 'four'),
                LayoutManager.LabelRow(5, 'custom'),           
                [LayoutManager.Button('Start', key=LayoutManager.Key.RECORD), LayoutManager.Button('Pause', key=LayoutManager.Key.STOP), LayoutManager.Button('Clear', key=LayoutManager.Key.CLEAR), LayoutManager.Button('Save', key=LayoutManager.Key.SAVE), LayoutManager.Button('Exit')]
        ])]], vertical_alignment='top', key=LayoutManager.Key.DATA_MANAGER)
