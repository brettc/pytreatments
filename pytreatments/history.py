import logging
log = logging.getLogger("history")
import os
import time
import cPickle as pickle

from analysis_data import AnalysisData


class History(object):
    @property
    def pickle_path(self):
        return os.path.join(self.path, 'history.pickle')

    def __init__(self, pth, sim=None):
        self.path = pth

        # If we get a simulation, then we're saving. Otherwise, we're loading.
        if sim is not None:
            self.running = True
            self.mode = 'w'
            self.sim = sim
            self.on_init()
        else:
            # TODO: We should be able to load in 'w' mode, and continue the
            # simulation!!
            self.mode = 'r'
            self.mark_time()
            self.load()
            log.debug("Loading history from %s took %f seconds",
                      pth, self.report_time())
            self.running = False

    def load_pickle(self):
        f = open(self.pickle_path, 'rb')
        self.sim = pickle.load(f)

    def save_pickle(self):
        if self.mode == 'w':
            # Time to save the state
            log.debug("Saving pickle file of simulation here '%s'", self.pickle_path)
            f = open(self.pickle_path, 'wb')
            pickle.dump(self.sim, f, -1)

    def mark_time(self):
        self.start_counting = time.clock()

    def report_time(self):
        return time.clock() - self.start_counting

    def load(self):
        self.analysis_data = AnalysisData().load(self.path)
        self.load_pickle()

        # Now let the derived class do it's thing
        self.on_load()

    def close(self):
        self.on_close()

        # Now save out our simulation
        self.save_pickle()

    def on_load(self):
        pass

    def on_close(self):
        pass

    def on_init(self):
        pass



