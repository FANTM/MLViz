from collections import deque
from layout import LayoutManager
from typing import Deque, List
import logging

class DataPool:
    def __init__(self, size: int):
        self.record_buffers: List[List[int]] = [list() for _ in range(0, size)]
        self.size: int = size
        self.circular_buffers: List[Deque[int]] = [deque(maxlen=3000) for _ in range(0, size)]
        self.recording: bool = False

    def append(self, pin: int, data: int):
        try:
            if self.recording:
                self.record_buffers[pin].append(data)
            self.circular_buffers[pin].append(data)
        except IndexError:
            logging.error("Improper data pool access, buffer doesn't exist")
        
    def clear(self) -> None:
        for i in range(0, self.size):
            self.record_buffers[i].clear()

    def to_csv(self) -> List[str]:
        min_len = min([len(self.record_buffers[i]) for i in range(0, self.size)])
        payload = []
        payload.append("label," + ",".join(['emg_{}'.format(i) for i in range(0, self.size)]) + '\n')
        for i in range(0, min_len):
            payload.append(",".join( [str(self.record_buffers[j][i]) for j in range(0, self.size)])+ "\n")
        return payload

DATA_POOL = DataPool(LayoutManager.NUM_ROWS)