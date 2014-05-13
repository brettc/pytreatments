import logging
log = logging.getLogger("history")
import os
import time
import cPickle as pickle

from analysis_data import AnalysisData


class History(object):
    def __init__(self, pth, sim=None, replicate_seed=None):
        self.path = pth

        if sim is not None:
            self.running = True
            self.mode = 'w'
            self.init(sim)
        else:
            self.mode = 'r'
            self.mark_time()
            self.analysis_data = AnalysisData()
            self.analysis_data.load(self.path)
            self.load()
            log.debug("Loading history from %s took %f seconds",
                      pth, self.report_time())
            self.running = False

            # Verify that the seed is the same (ensures stability of analysis
            # under changing code)
            if replicate_seed is not None:
                if self.sim.seed != replicate_seed:
                    log.warning(
                        "The replicate seed (%d) given by the experiment is different "
                        "from the saved seed (%d) in the history!",
                        replicate_seed, self.sim.seed)

            # Extra verification can be built into here
            self.verify()

    def load_pickle(self):
        f = open(self.pickle_path, 'rb')
        sim = pickle.load(f)

        # We're going to save this
        self.sim = sim

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
        self.load_pickle()

    def init(self, sim):
        self.sim = sim

    def close(self):
        self.save_pickle()

    def verify(self):
        pass

    @property
    def pickle_path(self):
        return os.path.join(self.path, 'history.pickle')
