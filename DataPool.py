from collections import deque
from LayoutManager import LayoutManager
from typing import Deque, List
import logging

class DataPool:
    def __init__(self, size: int):
        VIZ_BUF_SIZE = 2000
        PRED_BUF_SIZE = 700
        self.record_buffers: List[List[float]] = [list() for _ in range(0, size)]
        self.size: int = size
        self.label: str = "None"
        self.circular_buffers: List[Deque[float]] = [deque([0.0]*VIZ_BUF_SIZE, maxlen=VIZ_BUF_SIZE) for _ in range(0, size)]
        self.recording: bool = False
        # want some smaller circular buffers just for prediction windows
        self.prediction_buffers: List[Deque[float]] = [deque([0.0]*PRED_BUF_SIZE, maxlen=PRED_BUF_SIZE) for _ in range(0, size)]

    def append(self, pin: int, data: float):
        try:
            if self.recording:
                self.record_buffers[pin].append({"label": self.label, "data": data})
            self.circular_buffers[pin].append(data)
            self.prediction_buffers[pin].append(data)
        except IndexError:
            logging.error("Improper data pool access, buffer doesn't exist")
        
    def clear(self) -> None:
        for i in range(0, self.size):
            self.record_buffers[i].clear()

    def to_csv(self) -> List[str]:
        non_zero_buffers = list(filter(lambda buffer: len(buffer) > 0, self.record_buffers))
        num_buffers = len(non_zero_buffers)
        min_len = min([len(buffer) for buffer in non_zero_buffers])
        payload = []
        payload.append("label," + ",".join(['emg_{}'.format(i) for i in range(0, num_buffers)]) + '\n')
        for i in range(0, min_len):
            payload.append("{},{}\n".format(str(non_zero_buffers[0][i]["label"]), ",".join( [str(non_zero_buffers[j][i]["data"]) for j in range(0, num_buffers)])))
        return payload

    def get_prediction_buffers(self) -> List[List[float]]:
        return [list(dq) for dq in self.prediction_buffers]

DATA_POOL = DataPool(LayoutManager.NUM_ROWS)
