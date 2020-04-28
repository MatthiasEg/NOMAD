import os
import string


class FakeDataReader:

    def __init__(self, fileSuffix: string):
        self._dataPath = "/home/manuel/PREN/workspaces/informatik/object_detection/darknet/fakedata"
        self._timestamps = []
        self._counter = 230
        self._fileSuffix = fileSuffix
        self._load_files()

    def _load_files(self):
        for path, subdirectories, files in os.walk(self._dataPath):
            for name in files:
                if name.endswith('.' + self._fileSuffix):
                    timestamp = name.split('.')[0] + '.' + name.split('.')[1]
                    self._timestamps.append(timestamp)
        self._timestamps.sort(key=lambda x: float(x))

    def getNextFilePath(self) -> string:
        timestamp: string = self._timestamps[self._counter]
        self._counter = self._counter + 1
        #if self._counter >= len(self._timestamps):
         #   self._counter = 0
        return self._dataPath + "/" + timestamp + '.' + self._fileSuffix

    def getNextTimestamp(self) -> string:
        timestamp: string = self._timestamps[self._counter]
        self._counter = self._counter + 1
        #if self._counter >= len(self._timestamps):
         #   self._counter = 0
        return timestamp
