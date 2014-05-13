import logging
log = logging.getLogger("analysis_data")
import cPickle as pickle
import pathlib


class AnalysisData(object):
    def __init__(self, **kwargs):
        self.data = kwargs

    def __getattr__(self, name):
        return self.data[name]

    def data_path(self, base_path):
        p = pathlib.Path(base_path)
        return p / 'analysis_data.pickle'

    def load(self, base_path):
        pth = self.data_path(base_path)
        if not pth.exists():
            return

        with pth.open('rb') as f:
            self.data = pickle.load(f)
        
    def save(self, base_path):
        pth = self.data_path(base_path)
        with pth.open('wb') as f:
            pickle.dump(self.data, f, -1)

