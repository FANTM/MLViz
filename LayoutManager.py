import pydevlpr_protocol as pd
import PySimpleGUI as sg
from typing import List


class LayoutManager:

    class Key:
        RECORD = 'record'
        STOP = 'stop'
        CLEAR = 'clear'
        SAVE = 'save'
        TRAIN = 'train'
        LOAD = 'load'
        FILENAME = 'filename'
        TRAIN_FILENAME = 'trainfilename'
        SAVEMODEL_FILENAME = 'savemodelfilename'
        LOADMODEL_FILENAME = 'loadmodelfilename'
        DATA_MANAGER = 'datamanager'
        TRAIN_MANAGER = 'trainmanager'
        TEST_MANAGER = 'testmanager'
        OPT_STANDARDIZE = 'opt_stand'
        CLF_LINEARSVM = 'clf_linsvm'
        NUM_DEVLPRS = 'numdevlprs'
        BTN_PRESS = 'press'
        BTN_RLSE  = 'release'
        LABEL_BUTTON_TEMPLATE = 'labelbtn{}'
        LABEL_INPUT_TEMPLATE = 'labelinput{}'
        CONNECT_TEMPLATE = 'connect{}'
        DISCONNECT_TEMPLATE = 'disconnect{}'
        PIN_TEMPLATE = 'pin{}'
        TOPIC_TEMPLATE = 'topic{}'
        ROW_TEMPLATE = 'row{}'
        
    FONT_FAMILY = 'Helvetica'
    FONT_SIZES = {'h1': 24, 'h2': 20, 'h3': 16,
                  'h4': 12, 'p': 10, 'button': 12}
    NUM_ROWS = 2
    NUM_LABELS = 4

    def __init__(self):
        self._record_layout = [[LayoutManager.RecordGestureColumn()]]
        self._train_layout = [[LayoutManager.TrainColumn()]]
        self._test_layout = [[LayoutManager.TestColumn()]]
        self._tabgroup_layout = [
            sg.TabGroup([
                [
                    sg.Tab('Record Data', self._record_layout),
                    sg.Tab('Train Model', self._train_layout),
                    sg.Tab('Test Model', self._test_layout)
                ]
            ])
        ]
        self._plot_layout = LayoutManager.Body(LayoutManager.NUM_ROWS)
        self._layout = [
            [sg.Column([self._tabgroup_layout]),
            sg.Column(self._plot_layout)]
        ]

    def __call__(self) -> List[sg.Element]:
        return self._layout

    @property
    def layout(self):
        return self._layout

    @staticmethod
    def Body(NUM_ROWS):
        return [LayoutManager.DataRow(i) for i in range(0, NUM_ROWS)]

    @staticmethod
    def Button(label, key=None, disabled=False, size=(None, None), pad=None):
        return sg.Button(label, border_width=0, enable_events=True, mouseover_colors=('white', '#004D86'), 
            key=key, disabled=disabled, size=size, pad=pad, font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))

    @staticmethod
    def Text(label, size=(None, None), text_size='p', justification='left'):
        return sg.Text(label, size=size,
            justification=justification, font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES[text_size]))

    @staticmethod
    def Canvas(size=(None, None), key=None):
        return sg.Canvas(size=size, key=key, expand_x=True, expand_y=True)

    @staticmethod
    def PinSelect(index):
        # Need to change the pin amount (5 -> ?)
        return sg.Spin(values=list(range(0,6)), key=LayoutManager.Key.PIN_TEMPLATE.format(index), font=(LayoutManager.FONT_FAMILY,
            LayoutManager.FONT_SIZES['p']))

    @staticmethod
    def TopicSelect(index):
        return LayoutManager.Select(LayoutManager.Key.TOPIC_TEMPLATE.format(index), size=(14, None), 
            values=[pd.DataTopic.RAW_DATA_TOPIC, pd.DataTopic.NOTCH_60_TOPIC, pd.DataTopic.NOTCH_50_TOPIC])

    @staticmethod
    def Select(key, values, size=(14, None)):
        return sg.Combo(values=values, tooltip=key, readonly=True, enable_events=True, key=key, size=size, 
            font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['p']))

    @staticmethod
    def NumPinSlider():
        return [[
            LayoutManager.Text('Number of DEVLPRS')
        ],
        [
            sg.Slider(range=(1, 6), key=LayoutManager.Key.NUM_DEVLPRS, trough_color="#DAE0E6", 
                relief=sg.RELIEF_FLAT,enable_events=True, default_value=3, resolution=1, tick_interval=1, orientation='h', expand_x=True)
        ]]

    @staticmethod
    def DataRow(index):
        return sg.Frame('EMG {}'.format(index), key=LayoutManager.Key.ROW_TEMPLATE.format(index), expand_x=True, vertical_alignment="center", layout=[
                    [
                        sg.Column([
                            [ LayoutManager.TopicSelect(index), LayoutManager.PinSelect(index) ],
                            [ LayoutManager.Button('Connect', size=(12, 1), key=LayoutManager.Key.CONNECT_TEMPLATE.format(index)) ],
                            [ LayoutManager.Button('Disconnect', size=(12, 1), key=LayoutManager.Key.DISCONNECT_TEMPLATE.format(index)) ],
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
        return [
            LayoutManager.Button("Label {}".format(index), key=LayoutManager.Key.LABEL_BUTTON_TEMPLATE.format(index)), 
            sg.Input(default_input, key=LayoutManager.Key.LABEL_INPUT_TEMPLATE.format(index),
                size=(22, None), font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))]

    @staticmethod
    def FileSelect(input_txt, input_key):
        finput = sg.Input(input_txt, key=input_key, size=(22, None), font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))
        fbrowse = sg.FileBrowse(font=(LayoutManager.FONT_FAMILY, LayoutManager.FONT_SIZES['button']))
        return finput,fbrowse

    @staticmethod
    def RecordGestureColumn():
        return sg.Column([
            [sg.Text('Output Filename')],
            [
                *LayoutManager.FileSelect('data/recording.csv', LayoutManager.Key.FILENAME) # need to break the tuple with *
            ],
            [sg.Text('Labels')],
            *[LayoutManager.LabelRow(i, 'label_{}'.format(i)) for i in range(0, LayoutManager.NUM_LABELS)],
            [
                LayoutManager.Button('Start', key=LayoutManager.Key.RECORD), 
                LayoutManager.Button('Pause', key=LayoutManager.Key.STOP), 
                LayoutManager.Button('Clear', key=LayoutManager.Key.CLEAR), 
                LayoutManager.Button('Save', key=LayoutManager.Key.SAVE), 
                LayoutManager.Button('Exit')
            ]
        ], vertical_alignment='top', key=LayoutManager.Key.DATA_MANAGER)

    @staticmethod
    def TrainColumn():
        return sg.Column([
            [sg.Text('Training Data Filename')],
            [*LayoutManager.FileSelect('data/recording.csv', LayoutManager.Key.TRAIN_FILENAME)], # need to break tuple with *
            [sg.Text('Output Model Filename')],
            [*LayoutManager.FileSelect('models/recording.model', LayoutManager.Key.SAVEMODEL_FILENAME)], # need to break tuple with *
            [sg.Text('Options')],
            [
                sg.Checkbox('Standardize', default=True, key=LayoutManager.Key.OPT_STANDARDIZE)
            ],
            [sg.Text('Classifier')],
            [
                sg.Radio('Linear SVM', group_id='clf', default=True, key=LayoutManager.Key.CLF_LINEARSVM)
            ],
            [LayoutManager.Button('Train', key=LayoutManager.Key.TRAIN)]
        ], vertical_alignment='top', key=LayoutManager.Key.TRAIN_MANAGER)

    @staticmethod
    def TestColumn():
        return sg.Column([
            [sg.Text('Trained Model Filename')],
            [*LayoutManager.FileSelect('models/recording.model', LayoutManager.Key.LOADMODEL_FILENAME)], # need to break tuple with *
            [LayoutManager.Button('Load Model', key=LayoutManager.Key.LOAD)],
            [sg.Frame('Predicted Gesture',
                [
                    [sg.Text('--', justification='center', expand_x=True)]
                ],
            expand_x=True)]
        ], vertical_alignment='top', key=LayoutManager.Key.TEST_MANAGER)
